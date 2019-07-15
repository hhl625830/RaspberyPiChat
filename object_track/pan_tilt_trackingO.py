# import necessary packages
import time

import cv2
import imutils
import os
import pan_title
from imutils.video import VideoStream, FPS
from rosie_eyes2 import EyeController

offset_dead_block = 0.1
# define the range for the motors

IDLE = 2000  # Timeout servo after command
SERVOD = "/home/pi/PiBits/ServoBlaster/user/servod"  # Location of servod
pth = pan_title.PanTilt()
last_pan_degree = 100  # 最近一次底部舵机的角度值记录
last_tilt_degree = 105  # 最近一次顶部舵机的角度值记录
pan_pin = 23
tilt_pin = 18
PKG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)))
DETECTOR_PATH = os.path.normpath(os.path.join(PKG_PATH, os.pardir, "detection-data"))
detector_data = os.path.join(DETECTOR_PATH, 'haarcascade_frontalface_default.xml')
tilt_kp = -10
pan_kp = 10
ecl = EyeController()


def initialize():
    cmd = ("sudo %s --idle-timeout=%s" % (SERVOD, IDLE))
    os.system(cmd)
    pth.pan(last_pan_degree)
    pth.tilt(last_tilt_degree)
    ecl.clear()


def get_offset(obj_x, obj_y, center_x, center_y):
    move_x = float(obj_x / center_x - 0.5) * 2
    move_y = float(obj_y / center_y - 0.5) * 2
    return (move_x, move_y)


def servo_degree_pan(offset_x):
    global offset_dead_block
    global pan_kp  # 控制舵机旋转的比例系数
    global last_pan_degree  # 上一次顶部舵机的角度

    # 设置最小阈值
    if abs(offset_x) < offset_dead_block:
        offset_x = 0

    # offset范围在-50到50左右
    delta_degree = offset_x * pan_kp
    # 计算得到新的底部舵机角度
    next_pan_degree = last_pan_degree + delta_degree

    return next_pan_degree


def servo_degree_tilt(offset_y):
    global offset_dead_block  # 偏移量死区大小
    global tilt_kp  # 控制舵机旋转的比例系数
    global last_tilt_degree  # 上一次底部舵机的角度

    # 如果偏移量小于阈值就不相应
    if abs(offset_y) < offset_dead_block:
        offset_y = 0
    # offset_y *= -1
    # offset范围在-50到50左右
    delta_degree = offset_y * tilt_kp
    # 新的顶部舵机角度
    next_tilt_degree = last_tilt_degree + delta_degree

    return next_tilt_degree


def in_range(val, start, end):
    # determine the input vale is in the supplied range
    return (val >= start and val <= end)


def set_servos(pan, tlt):
    global pan_pin
    global tilt_pin
    # if the pan angle is within the range, pan
    if in_range(pan, 5, 175):
        pth.servo_one(pan_pin, pan)
        if pan > 100:
            ecl.set_watch_right()
        elif pan <100:
            ecl.set_watch_left()
        else:
            ecl.set_nevtral()

    # if the tilt angle is within the range, tilt
    if in_range(tlt, 5, 175):
        pth.servo_two(tilt_pin, tlt)
        if tlt > 105:
            ecl.set_watch_top()
        elif tlt < 105:
            ecl.set_watch_bottom()
        else:
            ecl.set_nevtral()


# start the video stream and wait for the camera to warm up
print("[INFO] starting video stream...")
pth.pan(pan_pin, last_pan_degree)
pth.tilt(tilt_pin, last_tilt_degree)
vs = VideoStream(src=0).start()
time.sleep(2.0)
fps = FPS().start()
# initialize the object center finder

face_detection = cv2.CascadeClassifier(detector_data)

initialize()
# loop indefinitely
while True:
    # grab the frame from the threaded video stream and flip it
    # vertically (since our camera was upside down)
    frame = vs.read()
    frame = cv2.flip(frame, 1)
    frame = imutils.resize(frame, width=400)

    # calculate the center of the frame as this is where we will
    # try to keep the object
    (H, W) = frame.shape[:2]
    key = cv2.waitKey(1) & 0xff

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_detection.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=9, minSize=(30, 30),
                                            flags=cv2.CASCADE_SCALE_IMAGE)

    if len(faces) > 0:
        faces = sorted(faces, reverse=True, key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]

        (fX, fY, fW, fH) = faces
        cv2.rectangle(frame, (fX, fY), (fX + fW, fY + fH), (0, 255, 0), 2)
        face_x = float(fX + fW / 2.0)
        face_y = float(fY + fH / 2.0)
        (offset_x, offset_y) = get_offset(face_x, face_y, W, H)
        next_pan_degree = servo_degree_pan(offset_x)
        next_tilt_degree = servo_degree_tilt(offset_y)

        set_servos(next_pan_degree, next_tilt_degree)

    # display the frame to the screen
    cv2.imshow("Pan-Tilt Face Tracking", frame)

    if key == 27:  # press 'ESC' to quit

        break
    # update the FPS counter
    fps.update()
# stop the timer and display FPS information
fps.stop()
pth.servo_stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
cv2.destroyAllWindows()
vs.stop()
