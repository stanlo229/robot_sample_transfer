#!/usr/bin/python3
# coding=utf8
import sys
import cv2
import math
import time
import threading
import numpy as np
import HiwonderSDK.Board as Board
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *


AK = ArmIK()
AK.setPitchRangeMoving((0, 10, 18), 0, -30, -90, 1500)


# 人脸检测

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

# 阈值
conf_threshold = 0.6

# 模型位置
modelFile = "./models/res10_300x300_ssd_iter_140000_fp16.caffemodel"
configFile = "./models/deploy.prototxt"
net = cv2.dnn.readNetFromCaffe(configFile, modelFile)

#先将所有灯关闭
Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
Board.RGB.show()

frame_pass = True
x1=x2=y1=y2 = 0
old_time = 0

def run(img):
    global old_time
    global frame_pass
    global x1,x2,y1,y2
    
    if not frame_pass:
        frame_pass = True
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2, 8)
        x1=x2=y1=y2 = 0
        return img
    else:
        frame_pass = False
        
    img_copy = img.copy()
    img_h, img_w = img.shape[:2]
    blob = cv2.dnn.blobFromImage(img_copy, 1, (100, 100), [104, 117, 123], False, False)
    net.setInput(blob)
    detections = net.forward() #计算识别
    
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            #识别到的人了的各个坐标转换会未缩放前的坐标
            x1 = int(detections[0, 0, i, 3] * img_w)
            y1 = int(detections[0, 0, i, 4] * img_h)
            x2 = int(detections[0, 0, i, 5] * img_w)
            y2 = int(detections[0, 0, i, 6] * img_h)             
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2, 8) #将识别到的人脸框出
            if abs((x1 + x2)/2 - img_w/2) < img_w/4:
                Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 255))  #设置2个灯为绿色
                Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 255))
                Board.RGB.show()
                old_time = time.time()
        else:
            if (time.time() - old_time) > 0.5 :
                Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
                Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
                Board.RGB.show()     
    return img


if __name__ == '__main__':
    
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


