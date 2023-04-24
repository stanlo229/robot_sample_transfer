#!/usr/bin/env python3
# encoding: utf-8
# 4自由度机械臂逆运动学：给定相应的坐标（X,Y,Z），以及俯仰角，计算出每个关节转动的角度 4 degrees of freedom mechanical arm inverse kinematics: given the corresponding coordinates (X, Y, Z), and the pitch angle, calculate the angle of rotation of each joint
# 2020/07/20 Aiden
import logging
from math import *

# CRITICAL, ERROR, WARNING, INFO, DEBUG
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class IK:
    # 舵机从下往上数 Servo counting from bottom to top
    # 公用参数，即4自由度机械臂的连杆参数 Common parameters, that is, the connecting rod parameters of the 4-DOF manipulator
    l1 = 6.10    #机械臂底盘中心到第二个舵机中心轴的距离6.10cm The distance from the center of the robotic arm chassis to the central axis of the second servo is 6.10cm
    l2 = 10.16   #第二个舵机到第三个舵机的距离10.16cm The distance from the second servo to the third servo is 10.16cm
    l3 = 9.64    #第三个舵机到第四个舵机的距离9.64cm The distance from the third servo to the fourth servo is 9.64cm
    l4 = 0.00    #这里不做具体赋值，根据初始化时的选择进行重新赋值 There is no specific assignment here, and reassignment is made according to the selection during initialization

    # 气泵款特有参数 Specific parameters of the air pump
    l5 = 4.70  #第四个舵机到吸嘴正上方的距离4.70cm The distance from the fourth servo to the top of the suction nozzle is 4.70cm
    l6 = 4.46  #吸嘴正上方到吸嘴的距离4.46cm The distance from the top of the nozzle to the nozzle is 4.46cm
    alpha = degrees(atan(l6 / l5))  #计算l5和l4的夹角 Calculate the angle between l5 and l4

    def __init__(self, arm_type): #根据不同款的夹持器，适配参数 Adapt parameters according to different types of grippers
        self.arm_type = arm_type
        if self.arm_type == 'pump': #如果是气泵款机械臂 If it is an air pump type robotic arm
            self.l4 = sqrt(pow(self.l5, 2) + pow(self.l6, 2))  #第四个舵机到吸嘴作为第四个连杆 The fourth servo to the nozzle as the fourth link
        elif self.arm_type == 'arm':
            self.l4 = 16.65  #第四个舵机到机械臂末端的距离16.6cm， 机械臂末端是指爪子完全闭合时 The distance from the fourth servo to the end of the mechanical arm is 16.6cm, and the end of the mechanical arm refers to when the claw is fully closed

    def setLinkLength(self, L1=l1, L2=l2, L3=l3, L4=l4, L5=l5, L6=l6):
        # 更改机械臂的连杆长度，为了适配相同结构不同长度的机械臂 Change the length of the connecting rod of the robot arm, in order to adapt to the robot arm of different lengths with the same structure
        self.l1 = L1
        self.l2 = L2
        self.l3 = L3
        self.l4 = L4
        self.l5 = L5
        self.l6 = L6
        if self.arm_type == 'pump':
            self.l4 = sqrt(pow(self.l5, 2) + pow(self.l6, 2))
            self.alpha = degrees(atan(self.l6 / self.l5))

    def getLinkLength(self):
        # 获取当前设置的连杆长度 Get the currently set link length
        if self.arm_type == 'pump':
            return {"L1":self.l1, "L2":self.l2, "L3":self.l3, "L4":self.l4, "L5":self.l5, "L6":self.l6}
        else:
            return {"L1":self.l1, "L2":self.l2, "L3":self.l3, "L4":self.l4}

    def getRotationAngle(self, coordinate_data, Alpha):
        # 给定指定坐标和俯仰角，返回每个关节应该旋转的角度，如果无解返回False Given the specified coordinates and pitch angle, return the angle that each joint should rotate, if there is no solution, return False
        # coordinate_data为夹持器末端坐标，坐标单位cm， 以元组形式传入，例如(0, 5, 10) coordinate_data is the coordinates of the end of the gripper, the coordinate unit is cm, and it is passed in as a tuple, for example (0, 5, 10)
        # Alpha为夹持器与水平面的夹角，单位度  Alpha is the angle between the gripper and the horizontal plane, in degrees

        # 设夹持器末端为P(X, Y, Z), 坐标原点为O, 原点为云台中心在地面的投影， P点在地面的投影为P_  Set the end of the gripper as P(X, Y, Z), the origin of the coordinates as O, the origin as the projection of the center of the gimbal on the ground, and the projection of point P on the ground as P_
        # l1与l2的交点为A, l2与l3的交点为B，l3与l4的交点为C The intersection of l1 and l2 is A, the intersection of l2 and l3 is B, and the intersection of l3 and l4 is C
        # CD与PD垂直，CD与z轴垂直，则俯仰角Alpha为DC与PC的夹角, AE垂直DP_， 且E在DP_上， CF垂直AE，且F在AE上 CD is perpendicular to PD, CD is perpendicular to z axis, then the pitch angle Alpha is the angle between DC and PC, AE is perpendicular to DP_, and E is on DP_, CF is perpendicular to AE, and F is on AE
        # 夹角表示：例如AB和BC的夹角表示为ABC Angle representation: For example, the angle between AB and BC is expressed as ABC
        X, Y, Z = coordinate_data
        if self.arm_type == 'pump':
            Alpha -= self.alpha
        #求底座旋转角度 Find the rotation angle of the base
        theta6 = degrees(atan2(Y, X))
 
        P_O = sqrt(X*X + Y*Y) #P_到原点O距离 P_to the origin O distance
        CD = self.l4 * cos(radians(Alpha))
        PD = self.l4 * sin(radians(Alpha)) #当俯仰角为正时，PD为正，当俯仰角为负时，PD为负 When the pitch angle is positive, PD is positive; when the pitch angle is negative, PD is negative
        AF = P_O - CD
        CF = Z - self.l1 - PD
        AC = sqrt(pow(AF, 2) + pow(CF, 2))
        if round(CF, 4) < -self.l1:
            logger.debug('高度低于0, CF(%s)<l1(%s)', CF, -self.l1)
            return False
        if self.l2 + self.l3 < round(AC, 4): #两边之和小于第三边 The sum of the two sides is less than the third side
            logger.debug('不能构成连杆结构, l2(%s) + l3(%s) < AC(%s)', self.l2, self.l3, AC)
            return False

        #求theat4
        cos_ABC = round(-(pow(AC, 2)- pow(self.l2, 2) - pow(self.l3, 2))/(2*self.l2*self.l3), 4) #余弦定理 cosine law
        if abs(cos_ABC) > 1:
            logger.debug('不能构成连杆结构, abs(cos_ABC(%s)) > 1', cos_ABC)
            return False
        ABC = acos(cos_ABC) #反三角算出弧度 inverse trigonometric arcs
        theta4 = 180.0 - degrees(ABC)

        #求theta5
        CAF = acos(AF / AC)
        cos_BAC = round((pow(AC, 2) + pow(self.l2, 2) - pow(self.l3, 2))/(2*self.l2*AC), 4) #余弦定理cosine law
        if abs(cos_BAC) > 1:
            logger.debug('不能构成连杆结构, abs(cos_BAC(%s)) > 1', cos_BAC)
            return False
        if CF < 0:
            zf_flag = -1
        else:
            zf_flag = 1
        theta5 = degrees(CAF * zf_flag + acos(cos_BAC))

        #求theta3
        theta3 = Alpha - theta5 + theta4
        if self.arm_type == 'pump':
            theta3 += self.alpha

        return {"theta3":theta3, "theta4":theta4, "theta5":theta5, "theta6":theta6} # 有解时返回角度字典 Returns a dictionary of angles when there is a solution
            
if __name__ == '__main__':
    ik = IK('arm')
    ik.setLinkLength(L1=ik.l1 + 0.89, L4=ik.l4 - 0.3)
    print('连杆长度：', ik.getLinkLength())
    print(ik.getRotationAngle((0, 0, ik.l1 + ik.l2 + ik.l3 + ik.l4), 90))
