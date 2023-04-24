#!/usr/bin/python3
# coding=utf8
import sys
import cv2
import math
import time
import threading
import numpy as np
import apriltag
import HiwonderSDK.Board as Board
import HiwonderSDK.Misc as Misc
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *

#apriltag码垛

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

AK = ArmIK()

x = 0.0
y = 12.0
z = 5.0
st = True
tag_id = None
centerX = 340
centerY = 380
object_angle = 0
object_center_x = 0.0
object_center_y = 0.0

def reset():
    global x, y, z
    
    x = 0.0
    y = 12.0
    z = 5.0
    
# 初始位置
def initMove():
    Board.setBusServoPulse(1, 0, 1500)
    time.sleep(2)
    Board.setBusServoPulse(2, 500, 1000)
    time.sleep(2)
    AK.setPitchRangeMoving((x, y, z), -90,-90, 0, 1500)
    time.sleep(2)

def setBuzzer(s):
    Board.setBuzzer(1)
    time.sleep(s)
    Board.setBuzzer(0)
setBuzzer(0)
# 检测apriltag
detector = apriltag.Detector(searchpath=apriltag._get_demo_searchpath())# Uses the Detector class in the april tag file

def apriltagDetect(img):
    global object_center_x, object_center_y, object_angle
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    detections = detector.detect(gray, return_image=False)

    if len(detections) != 0:
        for detection in detections:                       
            corners = np.rint(detection.corners)  # 获取四个角点
            cv2.drawContours(img, [np.array(corners, np.int)], -1, (0, 255, 255), 2)
            tag_family = str(detection.tag_family, encoding='utf-8')  # 获取tag_family
            tag_id = int(detection.tag_id)  # 获取tag_id
            object_center_x, object_center_y = int(detection.center[0]), int(detection.center[1])  # 中心点
            object_angle = int(math.degrees(math.atan2(corners[0][1] - corners[1][1], corners[0][0] - corners[1][0])))  # 计算旋转角
            angle = int(object_angle % 90)
            print(angle)
            return tag_family, tag_id   
    return None, None

def defaultpos():
    AK.setPitchRangeMoving((0, 18, 5), -90,-90, 0, 1500)
    time.sleep(2)
    AK.setPitchRangeMoving((0, 18, 3), -90,-90, 0, 1500)
    time.sleep(2)
    Board.setBusServoPulse(1, 0, 1500)
    time.sleep(2)
    reset()
    AK.setPitchRangeMoving((x, y, z), -90,-90, 0, 1500)
    time.sleep(2)
    
def dropoff():
    AK.setPitchRangeMoving((20, 0, 5), -90,-90, 0, 1500) 
    time.sleep(2)
    Board.setBusServoPulse(2, 500, 500) 
    AK.setPitchRangeMoving((20, 0, 2), -90,-90, 0, 1000) 
    time.sleep(2)
    Board.setBusServoPulse(1, 0, 1500)#Release claw
    time.sleep(3)
    Board.setBusServoPulse(1, 800, 1500) #Close gripper
    time.sleep(3)
    AK.setPitchRangeMoving((20, 0, 5), -90,-90, 0, 1000) 
    time.sleep(2)


def move():
    global x, y, z, st
    global object_center_x, object_center_y
    
    initMove()
    num = 0
    slow = True
    x_st = False
    y_st = False
    while True:
        if tag_id is not None:
            if (object_center_x - centerX) > 20: # 机械臂X轴上靠近物块
                x += 0.2
            elif (object_center_x - centerX) < -20:
                x -= 0.2
            else:
                x_st = True
                
            if (object_center_y - centerY) > 5:   # 机械臂Y轴上靠近物块
                y -= 0.1
            elif (object_center_y - centerY) < -10:
                y += 0.1
            else:
                y_st = True
                
            if slow:
                AK.setPitchRangeMoving((x, y, 3), -90,-90, 0, 800) # 检测后移动的第一步需要慢一些
                time.sleep(0.8)
                slow = False
            else:
                AK.setPitchRangeMoving((x, y, 3), -90,-90, 0, 100)
                time.sleep(0.1)
            
            if x_st and y_st:  #机械臂已经在物块的上方
                st = False
                x_st = False
                y_st = False
                setBuzzer(0.1)
                angle = int(object_angle % 90) #读取物块的偏转角
                # 把偏转角转换成2号舵机的脉冲宽度
                if angle > 45:
                    angle = angle - 45
                    Servo2_Pulse = int(Misc.map(angle, 0, 45, 300, 500)) #Change claw angle to match object angle
                else:
                    Servo2_Pulse = int(Misc.map(angle, 0, 45, 500, 700))
                Board.setBusServoPulse(2, Servo2_Pulse, 500) 
                time.sleep(1)
                # 机械臂进行夹取
                AK.setPitchRangeMoving((x, y+1.6, 2), -90,-90, 0, 500) #Move Down
                time.sleep(2)
                Board.setBusServoPulse(1, 800, 1500) #Close gripper
                time.sleep(3)
                # 夹取后，抬起
                AK.setPitchRangeMoving((x, y, z+2), -90,-90, 0, 1500)#Lift
                time.sleep(2)
                # 移动到放置位置上方
                dropoff()
                defaultpos()
                #!/usr/bin/python3
# coding=utf8
import sys
import cv2
import math
import time
import threading
import numpy as np
import apriltag
import HiwonderSDK.Board as Board
import HiwonderSDK.Misc as Misc
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *

#apriltag码垛

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

AK = ArmIK()

x = 0.0
y = 12.0
z = 5.0
st = True
tag_id = None
centerX = 340
centerY = 380
object_angle = 0
object_center_x = 0.0
object_center_y = 0.0

def reset():
    global x, y, z
    
    x = 0.0
    y = 12.0
    z = 5.0
    
# 初始位置
def initMove():
    Board.setBusServoPulse(1, 0, 1500)
    time.sleep(2)
    Board.setBusServoPulse(2, 500, 1000)
    time.sleep(2)
    AK.setPitchRangeMoving((x, y, z), -90,-90, 0, 1500)
    time.sleep(2)

def setBuzzer(s):
    Board.setBuzzer(1)
    time.sleep(s)
    Board.setBuzzer(0)
setBuzzer(0)
# 检测apriltag
detector = apriltag.Detector(searchpath=apriltag._get_demo_searchpath())# Uses the Detector class in the april tag file

def apriltagDetect(img):
    global object_center_x, object_center_y, object_angle
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    detections = detector.detect(gray, return_image=False)

    if len(detections) != 0:
        for detection in detections:                       
            corners = np.rint(detection.corners)  # 获取四个角点
            cv2.drawContours(img, [np.array(corners, np.int)], -1, (0, 255, 255), 2)
            tag_family = str(detection.tag_family, encoding='utf-8')  # 获取tag_family
            tag_id = int(detection.tag_id)  # 获取tag_id
            object_center_x, object_center_y = int(detection.center[0]), int(detection.center[1])  # 中心点
            object_angle = int(math.degrees(math.atan2(corners[0][1] - corners[1][1], corners[0][0] - corners[1][0])))  # 计算旋转角
            angle = int(object_angle % 90)
            print(angle)
            return tag_family, tag_id   
    return None, None

def defaultpos():
    AK.setPitchRangeMoving((0, 18, 5), -90,-90, 0, 1500)
    time.sleep(2)
    AK.setPitchRangeMoving((0, 18, 3), -90,-90, 0, 1500)
    time.sleep(2)
    Board.setBusServoPulse(1, 0, 1500)
    time.sleep(2)
    reset()
    AK.setPitchRangeMoving((x, y, z), -90,-90, 0, 1500)
    time.sleep(2)
    
def dropoff():
    AK.setPitchRangeMoving((20, 0, 5), -90,-90, 0, 1500) 
    time.sleep(2)
    Board.setBusServoPulse(2, 500, 500) 
    AK.setPitchRangeMoving((20, 0, 2), -90,-90, 0, 1000) 
    time.sleep(2)
    Board.setBusServoPulse(1, 0, 1500)#Release claw
    time.sleep(3)
    Board.setBusServoPulse(1, 800, 1500) #Close gripper
    time.sleep(3)
    AK.setPitchRangeMoving((20, 0, 5), -90,-90, 0, 1000) 
    time.sleep(2)


def move():
    global x, y, z, st
    global object_center_x, object_center_y
    
    initMove()
    num = 0
    slow = True
    x_st = False
    y_st = False
    while True:
        if tag_id is not None:
            if (object_center_x - centerX) > 20: # 机械臂X轴上靠近物块
                x += 0.2
            elif (object_center_x - centerX) < -20:
                x -= 0.2
            else:
                x_st = True
                
            if (object_center_y - centerY) > 5:   # 机械臂Y轴上靠近物块
                y -= 0.1
            elif (object_center_y - centerY) < -10:
                y += 0.1
            else:
                y_st = True
                
            if slow:
                AK.setPitchRangeMoving((x, y, 3), -90,-90, 0, 800) # 检测后移动的第一步需要慢一些
                time.sleep(0.8)
                slow = False
            else:
                AK.setPitchRangeMoving((x, y, 3), -90,-90, 0, 100)
                time.sleep(0.1)
            
            if x_st and y_st:  #机械臂已经在物块的上方
                st = False
                x_st = False
                y_st = False
                setBuzzer(0.1)
                angle = int(object_angle % 90) #读取物块的偏转角
                # 把偏转角转换成2号舵机的脉冲宽度
                if angle > 45:
                    angle = angle - 45
                    Servo2_Pulse = int(Misc.map(angle, 0, 45, 300, 500)) #Change claw angle to match object angle
                else:
                    Servo2_Pulse = int(Misc.map(angle, 0, 45, 500, 700))
                Board.setBusServoPulse(2, Servo2_Pulse, 500) 
                time.sleep(1)
                # 机械臂进行夹取
                AK.setPitchRangeMoving((x, y+1.6, 5), -90,-90, 0, 500) #Move Down
                time.sleep(2)
                Board.setBusServoPulse(1, 800, 1500) #Close gripper
                time.sleep(3)
                # 夹取后，抬起
                dropoff()
                defaultpos()
                # 码垛高度调整
                num += 1
                num = 0 if num > 2 else num
                st = True
                time.sleep(1)
        else:
            slow = True
            time.sleep(0.01)
    
# 运行子线程
th = threading.Thread(target=move)
th.setDaemon(True)
th.start()

def run(img):
    global state
    global tag_id
    global action_finish
    global object_center_x, object_center_y
     
    img_h, img_w = img.shape[:2]
    
    if st:
        tag_family, tag_id = apriltagDetect(img) # apriltag检测
    
        if tag_id is not None:
            cv2.putText(img, "tag_id: " + str(tag_id), (10, img.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, [0, 255, 255], 2)
            cv2.putText(img, "tag_family: " + tag_family, (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, [0, 255, 255], 2)
		# Makes text appear on screen noting the tag id and family in hershey simplex font at the defined location
    else:
        cv2.putText(img, "tag_id: None", (10, img.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, [0, 255, 255], 2)
        cv2.putText(img, "tag_family: None", (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, [0, 255, 255], 2)
    
    return img

if __name__ == '__main__':
    
    initMove()
    cap = cv2.VideoCapture(-1) #读取摄像头
    
    while True:
        ret, img = cap.read()
        if ret:
            frame = img.copy()
            Frame = run(frame)           
            cv2.imshow('Frame', Frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
        else:
            time.sleep(0.01)
    cv2.destroyAllWindows()

