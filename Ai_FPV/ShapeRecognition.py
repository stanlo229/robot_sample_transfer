#!/usr/bin/python3
# coding=utf8
import sys
import cv2
import math
import time
import threading
import numpy as np
import HiwonderSDK.tm1640 as tm
import RPi.GPIO as GPIO
import HiwonderSDK.Board
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

AK = ArmIK()
AK.setPitchRangeMoving((0, 10, 3), -90, -30, -90, 1500)

color_range = {
'red': [(0, 101, 177), (255, 255, 255)], 
'green': [(47, 0, 135), (255, 119, 255)], 
'blue': [(0, 0, 0), (255, 255, 115)], 
'black': [(0, 0, 0), (41, 255, 136)], 
'white': [(193, 0, 0), (255, 250, 255)], 
}
## 初始化引脚模式
fanPin1 = 22
fanPin2 = 24
GPIO.setup(fanPin1, GPIO.OUT) #设置引脚为输出模式
GPIO.setup(fanPin2, GPIO.OUT)


if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)
    
range_rgb = {
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'green': (0, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}

# 找出面积最大的轮廓
# 参数为要比较的轮廓的列表
def getAreaMaxContour(contours):
    contour_area_temp = 0
    contour_area_max = 0
    area_max_contour = None

    for c in contours:  # 历遍所有轮廓
        contour_area_temp = math.fabs(cv2.contourArea(c))  # 计算轮廓面积
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp > 50:  # 只有在面积大于50时，最大面积的轮廓才是有效的，以过滤干扰
                area_max_contour = c

    return area_max_contour, contour_area_max  # 返回最大的轮廓

shape_length = 0

def move():
    global shape_length
    
    while True:
        if shape_length == 3:
            print('三角形')
            ## 显示'三角形'
            tm.display_buf = (0x80, 0xc0, 0xa0, 0x90, 0x88, 0x84, 0x82, 0x81,
                              0x81, 0x82, 0x84,0x88, 0x90, 0xa0, 0xc0, 0x80)
            tm.update_display()
            
        elif shape_length == 4:
            print('矩形')
            ## 显示'矩形'
            tm.display_buf = (0x00, 0x00, 0x00, 0x00, 0xff, 0x81, 0x81, 0x81,
                              0x81, 0x81, 0x81,0xff, 0x00, 0x00, 0x00, 0x00)
            tm.update_display()
            
        elif shape_length >= 6:           
            print('圆')
            ## 显示'圆形'
            tm.display_buf = (0x00, 0x00, 0x00, 0x00, 0x1c, 0x22, 0x41, 0x41,
                              0x41, 0x22, 0x1c,0x00, 0x00, 0x00, 0x00, 0x00)
            tm.update_display()
            
        time.sleep(0.01)
       
        
# 运行子线程
th = threading.Thread(target=move)
th.setDaemon(True)
th.start()

shape_list = []
action_finish = True

if __name__ == '__main__':
    
    cap = cv2.VideoCapture(-1)
    while True:
        ret,img = cap.read()
        if ret:
            img_copy = img.copy()
            img_h, img_w = img.shape[:2]
            frame_gb = cv2.GaussianBlur(img_copy, (3, 3), 3)      
            frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # 将图像转换到LAB空间
            max_area = 0
            color_area_max = None    
            areaMaxContour_max = 0

            if action_finish:
                for i in color_range:
                    if i != 'white':
                        frame_mask = cv2.inRange(frame_lab, color_range[i][0], color_range[i][1])  #对原图像和掩模进行位运算
                        opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6,6),np.uint8))  #开运算
                        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6,6),np.uint8)) #闭运算
                        contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  #找出轮廓
                        areaMaxContour, area_max = getAreaMaxContour(contours)  #找出最大轮廓
                        if areaMaxContour is not None:
                            if area_max > max_area:#找最大面积
                                max_area = area_max
                                color_area_max = i
                                areaMaxContour_max = areaMaxContour
            if max_area > 200:                   
                cv2.drawContours(img, areaMaxContour_max, -1, (0, 0, 255), 2)
                # 识别形状
                # 周长  0.035 根据识别情况修改，识别越好，越小
                epsilon = 0.035 * cv2.arcLength(areaMaxContour_max, True)
                # 轮廓相似
                approx = cv2.approxPolyDP(areaMaxContour_max, epsilon, True)
                shape_list.append(len(approx))
                if len(shape_list) == 30:
                    shape_length = int(round(np.mean(shape_list)))                            
                    shape_list = []
                    print(shape_length)
                    
            frame_resize = cv2.resize(img, (320, 240))
            cv2.imshow('frame', frame_resize)
            key = cv2.waitKey(1)
            if key == 27:
                break
        else:
            time.sleep(0.01)
    my_camera.camera_close()
    cv2.destroyAllWindows()

