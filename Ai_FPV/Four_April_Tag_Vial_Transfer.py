
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
y = 15.0
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
    Board.setBusServoPulse(1, 400, 1500)
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

tag_0_x=0
tag_0_y=0
tag_1_x=0
tag_1_y=0
tag_2_x=0
tag_2_y=0
tag_3_x=0
tag_3_y=0
tag_4_x=0
tag_4_y=0
tag_5_x=0
tag_5_y=0
tag_6_x=0
tag_6_y=0
tag_7_x=0
tag_7_y=0

def pickupcalibrate():
    global object_center_x, object_center_y
    global tag_0_x, tag_0_y, tag_1_x, tag_1_y, tag_2_x, tag_2_y, tag_3_x, tag_3_y, tag_4_x, tag_4_y, tag_5_x, tag_5_y, tag_6_x, tag_6_y, tag_7_x, tag_7_y
    global tag_id

    if str(tag_id) == "0":
        object_center_x = tag_0_x
        object_center_y = tag_0_y
        AK.setPitchRangeMoving((int(tag_0_x)+4, int(tag_0_y), 5), -90,-90, 0, 500)
        time.sleep(2)
    elif str(tag_id) == "1":
        object_center_x = tag_1_x
        object_center_y = tag_1_y
        AK.setPitchRangeMoving((int(tag_1_x), int(tag_1_y)-4, 5), -90,-90, 0, 500)
        time.sleep(2)
    elif str(tag_id) == "2":
        object_center_x = tag_2_x
        object_center_y = tag_2_y
        AK.setPitchRangeMoving((int(tag_2_x)-4, int(tag_2_y), 5), -90,-90, 0, 500)
        time.sleep(2)
    elif str(tag_id) == "3":
        object_center_x = tag_3_x
        object_center_y = tag_3_y
        AK.setPitchRangeMoving((int(tag_3_x), int(tag_3_y)+4, 5), -90,-90, 0, 500)
        time.sleep(2)

def dropoffcalibrate():
    global object_center_x, object_center_y
    global tag_id
    global tag_4_x, tag_4_y, tag_5_x, tag_5_y, tag_6_x, tag_6_y, tag_7_x, tag_7_y
    print("test")
    if str(tag_id) == 4:
        object_center_x = tag_4_x
        object_center_y = tag_4_y
        AK.setPitchRangeMoving((int(tag_4_x)+4, int(tag_4_y), 5), -90,-90, 0, 500)
        time.sleep(2)
    elif str(tag_id) == 5:
        object_center_x = tag_5_x
        object_center_y = tag_5_y
        AK.setPitchRangeMoving((int(tag_5_x), int(tag_5_y)-4, 5), -90,-90, 0, 500)
        time.sleep(2)
    elif str(tag_id) == 6:
        object_center_x = tag_6_x
        object_center_y = tag_6_y
        AK.setPitchRangeMoving((int(tag_6_x)-4, int(tag_6_y), 5), -90,-90, 0, 500)
        time.sleep(2)
    elif str(tag_id) == 7:
        object_center_x = tag_7_x
        object_center_y = tag_7_y
        AK.setPitchRangeMoving((int(tag_7_x), int(tag_7_y)+4, 5), -90,-90, 0, 500)
        time.sleep(2)
    
def dropoff():
    AK.setPitchRangeMoving((20, 0, 8), -90,-90, 0, 500)
    time.sleep(2)
    Board.setBusServoPulse(2, 500, 500) 
    AK.setPitchRangeMoving((20, 0, 5), -90,-90, 0, 1000) 
    time.sleep(2)
    Board.setBusServoPulse(1, 0, 1500)#Release claw
    time.sleep(3)
    AK.setPitchRangeMoving((20, 0, 8), -90,-90, 0, 1000) 
    time.sleep(2)

def grabvial():
    AK.setPitchRangeMoving((int(tag_0_x)+2.5, int(tag_0_y), 5), -90,-90, 0, 500)
    time.sleep(2)
    Board.setBusServoPulse(1, 600, 1500) #Close gripper
    time.sleep(3)
    AK.setPitchRangeMoving((int(tag_0_x)+2.5, int(tag_0_y)+2.5, 10), -90,-90, 0, 500)
    time.sleep(2)
    AK.setPitchRangeMoving((20, 0, 8), -90,-90, 0, 500)
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
         for i in range(3):
               pickupcalibrate()
         
         grabvial()
         for i in range(3):        
               dropoffcalibrate()
         
         dropoff()
        
        
        
                # 夹取后，抬起
			
                # 码垛高度调整
         st=True
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
