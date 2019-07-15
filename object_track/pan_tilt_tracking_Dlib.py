import time
import cv2
import dlib
import os
import pan_title
from imutils.video import VideoStream, FPS
from rosie_eyes2 import EyeController

last_btm_degree = 100  # 最近一次底部舵机的角度值记录
last_top_degree = 110  # 最近一次顶部舵机的角度值记录
pth = pan_title.PanTilt()
ecl = EyeController()
pan_pin = 23
tilt_pin = 18
top_kp = -10  # 舵机的Kp系数
btm_kp = 12
offset_dead_block = 0.1  # 设置偏移量的死区


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

    return int(next_top_degree)


def set_servos(pan, tlt):
    global pan_pin
    global tilt_pin
    pth.pan(pan_pin, pan)
    if pan > 100:
        ecl.set_watch_right()
    elif pan < 100:
        ecl.set_watch_left()
    else:
        ecl.set_nevtral()
    pth.tilt(tilt_pin, tlt)
    if tlt > 105:
        ecl.set_watch_top()
    elif tlt < 105:
        ecl.set_watch_bottom()
    else:
        ecl.set_nevtral()


# start the video stream and wait for the camera to warm up
print("[INFO] starting video stream...")
pth.pan(pan_pin, last_btm_degree)
pth.tilt(tilt_pin, last_top_degree)
vs = VideoStream(src=0).start()
time.sleep(2.0)
fps = FPS().start()
# initialize the object center finder
inH = 300
inW = 0
hogFaceDetector = dlib.get_frontal_face_detector()
while True:
    frame = vs.read()
    frame = cv2.flip(frame, 1)
    frameDlibHog = frame.copy()
    key = cv2.waitKey(1) & 0xff
    (H, W) = frame.shape[:2]
    if not inW:
        inW = int((W / H) * inH)
    scaleHeight = H / inH
    scaleWidth = W / inW
    frameDlibHogSmall = cv2.resize(frameDlibHog, (inW, inH))
    frameDlibHogSmall = cv2.cvtColor(frameDlibHogSmall, cv2.COLOR_BGR2RGB)
    faceRects = hogFaceDetector(frameDlibHogSmall, 0)

    for faceRect in faceRects:
        cvRect = [int(faceRect.left() * scaleWidth), int(faceRect.top() * scaleHeight),
                  int(faceRect.right() * scaleWidth), int(faceRect.bottom() * scaleHeight)]
        # cv2.rectangle(frameDlibHog, (cvRect[0], cvRect[1]), (cvRect[2], cvRect[3]), (0, 255, 0),
        #               int(round(H / 150)), 4)
        if cvRect is not None:
            (Fx, Fy, Fw, Fh) = cvRect
            face_x = float(Fx + Fw / 2.0)
            face_y = float(Fy + Fh / 2.0)
            center = (face_x, face_y)
            (offset_x, offset_y) = calculate_offset(W, H, center)

            next_btm_degree = btm_servo_control(offset_x)
            next_top_degree = top_servo_control(offset_y)
            # 舵机转动
            set_servos(next_btm_degree, next_top_degree)
            # 更新角度值
            last_btm_degree = next_btm_degree
            last_top_degree = next_top_degree

    # cv2.imshow('FaceDetect', frameDlibHog)

    if key == 27:  # press 'ESC' to quit
        break
    # update the FPS counter
    fps.update()
# stop the timer and display FPS information
pth.servo_stop()
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
vs.stop()
