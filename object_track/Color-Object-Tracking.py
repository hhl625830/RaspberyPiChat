# -*- coding:utf-8 _*-
""" 
@author:HuHongling

@file: Color-Object-Tracking.py 
@time: 2019/06/24
@contact: huhonglin@hwasmart.com
@site:  
@software: PyCharm 

"""
import time

import pan_title
from imutils.video import VideoStream, FPS
from rosie_eyes2 import EyeController

last_btm_degree = 100  # 最近一次底部舵机的角度值记录
last_top_degree = 110  # 最近一次顶部舵机的角度值记录
pth = pan_title.PanTilt()
ecl = EyeController()

top_kp = -10  # 舵机的Kp系数
btm_kp = 10
offset_dead_block = 0.5  # 设置偏移量的死区


def calculate_offset(img_width, img_height, center):
    '''
    计算人脸在画面中的偏移量
    偏移量的取值范围： [-1, 1]
    '''
    (face_x, face_y) = center
    # 人脸在画面中心X轴上的偏移量
    offset_x = float(face_x / img_width - 0.5) * 2
    # 人脸在画面中心Y轴上的偏移量
    offset_y = float(face_y / img_height - 0.5) * 2

    return (offset_x, offset_y)


def btm_servo_control(offset_x):
    '''
    底部舵机的比例控制
    这里舵机使用开环控制
    '''
    global offset_dead_block  # 偏移量死区大小
    global btm_kp  # 控制舵机旋转的比例系数
    global last_btm_degree  # 上一次底部舵机的角度

    # 设置最小阈值
    if abs(offset_x) < offset_dead_block:
        offset_x = 0

    # offset范围在-50到50左右
    delta_degree = offset_x * btm_kp
    # 计算得到新的底部舵机角度
    next_btm_degree = last_btm_degree + delta_degree
    if next_btm_degree < 30:
        next_btm_degree = 30

    elif next_btm_degree > 150:
        next_btm_degree = 150

    return int(next_btm_degree)


def top_servo_control(offset_y):
    '''
    顶部舵机的比例控制
    这里舵机使用开环控制
    '''
    global offset_dead_block
    global top_kp  # 控制舵机旋转的比例系数
    global last_top_degree  # 上一次顶部舵机的角度

    # 如果偏移量小于阈值就不相应
    if abs(offset_y) < offset_dead_block:
        offset_y = 0

    # offset_y *= -1
    # offset范围在-50到50左右
    delta_degree = offset_y * top_kp
    # 新的顶部舵机角度
    next_top_degree = last_top_degree + delta_degree
    if next_top_degree < 45:
        next_top_degree = 45
    elif next_top_degree > 145:
        next_top_degree = 145
    return int(next_top_degree)


def set_servos(pan, tlt):
    pth.pan(pan)
    if pan > 100:
        ecl.set_watch_right()
    elif pan < 100:
        ecl.set_watch_left()
    else:
        ecl.set_nevtral()
    pth.tilt(tlt)
    if tlt > 105:
        ecl.set_watch_top()
    elif tlt < 105:
        ecl.set_watch_bottom()
    else:
        ecl.set_nevtral()


import numpy as np

import imutils
import cv2

# construct the argument parse and parse the arguments


# define the lower and upper boundaries of the colors in the HSV color space
lower = {'red': (166, 84, 141), 'green': (66, 122, 129), 'blue': (97, 100, 117), 'yellow': (23, 59, 119),
         'orange': (0, 50, 80)}  # assign new item lower['blue'] = (93, 10, 0)
upper = {'red': (186, 255, 255), 'green': (86, 255, 255), 'blue': (117, 255, 255), 'yellow': (54, 255, 255),
         'orange': (20, 255, 255)}

# define standard colors for circle around the object
colors = {'red': (0, 0, 255), 'green': (0, 255, 0), 'blue': (255, 0, 0), 'yellow': (0, 255, 217),
          'orange': (0, 140, 255)}

# pts = deque(maxlen=args["buffer"])

# if a video path was not supplied, grab the reference


set_servos(last_btm_degree, last_top_degree)
vs = VideoStream(src=0).start()
time.sleep(2.0)
fps = FPS().start()
# keep looping
while True:
    # grab the current frame
    frame = vs.read()
    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=400)
    frame = cv2.flip(frame, 1)
    (H, W) = frame.shape[:2]
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    # for each color in dictionary check object in frame
    for key, value in upper.items():
        # construct a mask for the color from dictionary`1, then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        kernel = np.ones((9, 9), np.uint8)
        mask = cv2.inRange(hsv, lower[key], upper[key])
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None

        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size. Correct this value for your obect's size
            if radius > 5:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                if key == 'green':
                    (offset_x, offset_y) = calculate_offset(W, H, center)
                    next_btm_degree = btm_servo_control(offset_x)
                    # print("pan", next_btm_degree)

                    next_top_degree = top_servo_control(offset_y)
                    # print("tilt", next_top_degree)
                    set_servos(next_btm_degree, next_top_degree)

                    # 更新角度值
                    last_btm_degree = next_btm_degree
                    last_top_degree = next_top_degree

                    cv2.circle(frame, (int(x), int(y)), int(radius), colors[key], 2)
                    # draw the circle and centroid on the frame,
                    # then update the list of tracked points

                    # cv2.circle(frame, center, 5, (0, 0, 255), -1)
                    # cv2.putText(frame, key + " ball", (int(x - radius), int(y - radius)), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    #             colors[key], 2)

    # show the frame to our screen
    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1) & 0xFF
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break
    # update the FPS counter
    fps.update()
# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
# cleanup the camera and close any open windows
vs.stop()
cv2.destroyAllWindows()
