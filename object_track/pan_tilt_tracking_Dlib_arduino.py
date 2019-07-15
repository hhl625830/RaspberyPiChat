import time
import cv2

import os
import smbus

from imutils.video import VideoStream, FPS

bus = smbus.SMBus(1)
address = 0x04

def sendData(value):
    bus.write_byte(address, value)
    # bus.write_byte_data(address, 0, value)
    return -1

def readData():
    state = bus.read_byte(address)
    # number = bus.read_byte_data(address, 1)
    return state
PKG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)))

DETECTOR_PATH = os.path.normpath(os.path.join(PKG_PATH, os.pardir, "detection-data"))
detector = cv2.CascadeClassifier(os.path.join(DETECTOR_PATH, 'haarcascade_frontalface_default.xml'))
# start the video stream and wait for the camera to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)
fps = FPS().start()

while True:
    frame = vs.read()
    frame = cv2.flip(frame, 1)
    # calculate the center of the frame as this is where we will
    # try to keep the object
    (H, W) = frame.shape[:2]
    centerX = W // 2
    centerY = H // 2

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # detect all faces in the input frame
    rects = detector.detectMultiScale(gray, scaleFactor=1.05,
                                           minNeighbors=9, minSize=(30, 30),
                                           flags=cv2.CASCADE_SCALE_IMAGE)

    # check to see if a face was found
    for i, rect in enumerate(rects):
        # extract the bounding box coordinates of the face and
        # use the coordinates to determine the center of the
        # face
        (x, y, w, h) = rect
        faceX = int(x + (w / 2.0))
        faceY = int(y + (h / 2.0))
        state = readData()
        if state == 1:
            sendData(faceX)
            sendData(faceY)
            print("faceX==>{0}---faceY==>{1}".format(faceX, faceY))

        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
    cv2.imshow('FaceDetect', frame)
    key = cv2.waitKey(1) & 0xff
    if key == 27:  # press 'ESC' to quit
        break
    # update the FPS counter
    fps.update()
# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

vs.stop()
