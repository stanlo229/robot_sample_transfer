#!/usr/bin/python3
# coding=utf8
import os
import sys
import cv2
import math
import time
import numpy as np
import HiwonderSDK.Board as Board
import HiwonderSDK.Misc as Misc
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

AK = ArmIK()
__finger = 0
__t1 = 0
__step = 0
__count = 0
__get_finger = False

# 初始位置
def initMove():
    Board.setBusServoPulse(1, 500, 800)
    Board.setBusServoPulse(2, 500, 800)
    AK.setPitchRangeMoving((0, 10, 18), 0,-90, 0, 1500)

def reset():
    global __finger, __t1, __step, __count, __get_finger
    __finger = 0
    __t1 = 0
    __step = 0
    __count = 0
    __get_finger = False
    

def init():
    reset()
    initMove()

class Point(object):  # 一个坐标点
    x = 0
    y = 0

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class Line(object):  # 一条线
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

def GetCrossAngle(l1, l2):
    '''
    求两直线之间的夹角
    :param l1:
    :param l2:
    :return:
    '''
    arr_0 = np.array([(l1.p2.x - l1.p1.x), (l1.p2.y - l1.p1.y)])
    arr_1 = np.array([(l2.p2.x - l2.p1.x), (l2.p2.y - l2.p1.y)])
    cos_value = (float(arr_0.dot(arr_1)) / (np.sqrt(arr_0.dot(arr_0))
                                            * np.sqrt(arr_1.dot(arr_1))))   # 注意转成浮点数运算
    return np.arccos(cos_value) * (180/np.pi)

def distance(start, end):
    """
    计算两点的距离
    :param start: 开始点
    :param end: 结束点
    :return: 返回两点之间的距离
    """
    s_x, s_y = start
    e_x, e_y = end
    x = s_x - e_x
    y = s_y - e_y
    return math.sqrt((x**2)+(y**2))

def image_process(image, rw, rh):  # hsv
    '''
    # 光线影响，请修改 cb的范围
    # 正常黄种人的Cr分量大约在140~160之间
    识别肤色
    :param image: 图像
    :return: 识别后的二值图像
    '''
    frame_resize = cv2.resize(image, (rw, rh), interpolation=cv2.INTER_CUBIC)
    YUV = cv2.cvtColor(frame_resize, cv2.COLOR_BGR2YCR_CB)  # 将图片转化为YCrCb
    _, Cr, _ = cv2.split(YUV)  # 分割YCrCb
    Cr = cv2.GaussianBlur(Cr, (5, 5), 0)
    
    _, Cr = cv2.threshold(Cr, 135, 160, cv2.THRESH_BINARY +
                          cv2.THRESH_OTSU)  # OTSU 二值化

    # 开运算，去除噪点
    open_element = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opend = cv2.morphologyEx(Cr, cv2.MORPH_OPEN, open_element)
    # 腐蚀
    kernel = np.ones((3, 3), np.uint8)
    erosion = cv2.erode(opend, kernel, iterations=3)

    return erosion

def get_defects_far(defects, contours, img):
    '''
    获取凸包中最远的点
    '''
    if defects is None and contours is None:
        return None
    far_list = []
    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        start = tuple(contours[s][0])
        end = tuple(contours[e][0])
        far = tuple(contours[f][0])
        # 求两点之间的距离
        a = distance(start, end)
        b = distance(start, far)
        c = distance(end, far)
        # 求出手指之间的角度
        angle = math.acos((b ** 2 + c ** 2 - a ** 2) /
                          (2 * b * c)) * 180 / math.pi
        # 手指之间的角度一般不会大于100度
        # 小于90度
        if angle <= 75:  # 90:
            # cv.circle(img, far, 10, [0, 0, 255], 1)
            far_list.append(far)
    return far_list

def get_max_coutour(cou, max_area):
    '''
    找出最大的轮廓
    根据面积来计算，找到最大后，判断是否小于最小面积，如果小于侧放弃
    :param cou: 轮廓
    :return: 返回最大轮廓
    '''
    max_coutours = 0
    r_c = None
    if len(cou) < 1:
        return None
    else:
        for c in cou:
            # 计算面积
            temp_coutours = math.fabs(cv2.contourArea(c))
            if temp_coutours > max_coutours:
                max_coutours = temp_coutours
                cc = c
        # 判断所有轮廓中最大的面积
        if max_coutours > max_area:
            r_c = cc
        return r_c

def find_contours(binary, max_area):
    '''
    CV_RETR_EXTERNAL - 只提取最外层的轮廓
    CV_RETR_LIST - 提取所有轮廓，并且放置在 list 中
    CV_RETR_CCOMP - 提取所有轮廓，并且将其组织为两层的 hierarchy: 顶层为连通域的外围边界，次层为洞的内层边界。
    CV_RETR_TREE - 提取所有轮廓，并且重构嵌套轮廓的全部 hierarchy
    method  逼近方法 (对所有节点, 不包括使用内部逼近的 CV_RETR_RUNS).
    CV_CHAIN_CODE - Freeman 链码的输出轮廓. 其它方法输出多边形(定点序列).
    CV_CHAIN_APPROX_NONE - 将所有点由链码形式翻译(转化）为点序列形式
    CV_CHAIN_APPROX_SIMPLE - 压缩水平、垂直和对角分割，即函数只保留末端的象素点;
    CV_CHAIN_APPROX_TC89_L1,
    CV_CHAIN_APPROX_TC89_KCOS - 应用 Teh-Chin 链逼近算法. CV_LINK_RUNS - 通过连接为 1 的水平碎片使用完全不同的轮廓提取算法
    :param binary: 传入的二值图像
    :return: 返回最大轮廓
    '''
    # 找出所有轮廓
    contours = cv2.findContours(
        binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]
    # 返回最大轮廓
    return get_max_coutour(contours, max_area)

def get_hand_number(binary_image, contours, rw, rh, rgb_image):
    '''
    :param binary_image:
    :param rgb_image:
    :return:
    '''
    # # 2、找出手指尖的位置
    # # 查找轮廓，返回最大轮廓
    x = 0
    y = 0
    coord_list = []
    new_hand_list = []  # 获取最终的手指间坐标

    if contours is not None:
        # 周长  0.035 根据识别情况修改，识别越好，越小
        epsilon = 0.020 * cv2.arcLength(contours, True)
        # 轮廓相似
        approx = cv2.approxPolyDP(contours, epsilon, True)
        # cv2.approxPolyDP()的参数2(epsilon)是一个距离值，表示多边形的轮廓接近实际轮廓的程度，值越小，越精确；参数3表示是否闭合
        # cv2.polylines(rgb_image, [approx], True, (0, 255, 0), 1)#画多边形

        if approx.shape[0] >= 3:  # 有三个点以上#多边形最小为三角形，三角形需要三个点
            approx_list = []
            for j in range(approx.shape[0]):  # 将多边形所有的点储存在一个列表里
                # cv2.circle(rgb_image, (approx[j][0][0],approx[j][0][1]), 5, [255, 0, 0], -1)
                approx_list.append(approx[j][0])
            approx_list.append(approx[0][0])    # 在末尾添加第一个点
            approx_list.append(approx[1][0])    # 在末尾添加第二个点

            for i in range(1, len(approx_list) - 1):
                p1 = Point(approx_list[i - 1][0],
                           approx_list[i - 1][1])    # 声明一个点
                p2 = Point(approx_list[i][0], approx_list[i][1])
                p3 = Point(approx_list[i + 1][0], approx_list[i + 1][1])
                line1 = Line(p1, p2)    # 声明一条直线
                line2 = Line(p2, p3)
                angle = GetCrossAngle(line1, line2)     # 获取两条直线的夹角
                angle = 180 - angle     #
                # print angle
                if angle < 42:  # 求出两线相交的角度，并小于37度的
                    #cv2.circle(rgb_image, tuple(approx_list[i]), 5, [255, 0, 0], -1)
                    coord_list.append(tuple(approx_list[i]))

        ##############################################################################
        # 去除手指间的点
        # 1、获取凸包缺陷点，最远点点
        #cv2.drawContours(rgb_image, contours, -1, (255, 0, 0), 1)
        try:
            hull = cv2.convexHull(contours, returnPoints=False)
            # 找凸包缺陷点 。返回的数据， 【起点，终点， 最远的点， 到最远点的近似距离】
            defects = cv2.convexityDefects(contours, hull)
            # 返回手指间的点
            hand_coord = get_defects_far(defects, contours, rgb_image)
        except:
            return rgb_image, 0
        
        # 2、从coord_list 去除最远点
        alike_flag = False
        if len(coord_list) > 0:
            for l in range(len(coord_list)):
                for k in range(len(hand_coord)):
                    if (-10 <= coord_list[l][0] - hand_coord[k][0] <= 10 and
                            -10 <= coord_list[l][1] - hand_coord[k][1] <= 10):    # 最比较X,Y轴, 相近的去除
                        alike_flag = True
                        break   #
                if alike_flag is False:
                    new_hand_list.append(coord_list[l])
                alike_flag = False
            # 获取指尖的坐标列表并显示
            for i in new_hand_list:
                j = list(tuple(i))
                j[0] = int(Misc.map(j[0], 0, rw, 0, 640))
                j[1] = int(Misc.map(j[1], 0, rh, 0, 480))
                cv2.circle(rgb_image, (j[0], j[1]), 20, [0, 255, 255], -1)
    fingers = len(new_hand_list)

    return rgb_image, fingers


def run(img, debug=False):

    global __act_map, __get_finger
    global __step, __count, __finger

    binary = image_process(img, 320, 240)
    contours = find_contours(binary, 3000)
    img, finger = get_hand_number(binary, contours, 320, 240, img)
    if not __get_finger:
        if finger == __finger:
            __count += 1
        else:
            __count = 0
        __finger = finger
        
    cv2.putText(img, "Finger(s):%d" % __finger, (50, 480 - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 2)#将识别到的手指个数写在图片上
    
    return img 



if __name__ == '__main__':
    
    init()
    cap = cv2.VideoCapture(-1) #读取摄像头
    
    while True:
        ret, img = cap.read()
        if ret:
            frame = img.copy()
            Frame = run(frame)           
            frame_resize = cv2.resize(Frame, (320, 240))
            cv2.imshow('frame', frame_resize)
            key = cv2.waitKey(1)
            if key == 27:
                break
        else:
            time.sleep(0.01)
    cv2.destroyAllWindows()
