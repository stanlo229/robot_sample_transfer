#Own Code
from AprilTagTrack import *
from ArmIK.ArmMoveIK import *
import time
import cv2
import numpy
import math
import sys

if __name__ == '__main__':
    
    cap = cv2.VideoCapture(1)
    
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