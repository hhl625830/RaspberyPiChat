import time

import cv2
import imutils
import numpy as np
import os
from imutils.video import VideoStream, FPS
from keras.models import load_model
from rosie_eyes2 import EyeController

ecl = EyeController()

PKG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)))
DETECTOR_PATH = os.path.normpath(os.path.join(PKG_PATH, os.pardir, "detection-data"))
detector = cv2.CascadeClassifier(os.path.join(DETECTOR_PATH, 'haarcascade_frontalface_default.xml'))
model_emotion = load_model(os.path.join(DETECTOR_PATH, 'simple_CNN.530-0.65.hdf5'))

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)
img_size = 64
ad = 0.5

# start the FPS counter
fps = FPS().start()
while True:
    frame = vs.read()
    frame = imutils.resize(frame, width=400)
    (H, W) = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # opencv detector
    rects = detector.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=9, minSize=(30, 30))

    key = cv2.waitKey(1) & 0xFF
    emotion_labels = {
        0: 'angry',
        1: 'disgust',
        2: 'fear',
        3: 'happy',
        4: 'sad',
        5: 'surprise',
        6: 'neutral'}

    for i, rect in enumerate(rects):
        # dlib
        # (x, y, w, h) = face_utils.rect_to_bb(rect)
        # opencv haarcascade
        (x, y, w, h) = rect
        x1 = x
        y1 = y

        xw1 = max(int(x1 - ad * w), 0)
        yw1 = max(int(y1 - ad * h), 0)

        gray_face = gray[y:(y + h), x:(x + w)]
        gray_face = cv2.resize(gray_face, (48, 48))
        gray_face = gray_face / 255.0
        gray_face = np.expand_dims(gray_face, 0)
        gray_face = np.expand_dims(gray_face, -1)
        emotion_prediction = model_emotion.predict(gray_face)
        emotion_probability = np.max(emotion_prediction)
        emotion_label_arg = np.argmax(model_emotion.predict(gray_face))
        emotion = emotion_labels[emotion_label_arg]
        label = str(emotion)

        if label == 'angry':
            color = emotion_probability * np.asarray((255, 0, 0))
            ecl.set_fear()
        elif label == 'sad':
            color = emotion_probability * np.asarray((0, 0, 255))
            ecl.set_sadness()
        elif label == 'happy':
            color = emotion_probability * np.asarray((255, 255, 0))
            ecl.set_happy()
        elif label == 'surprise':
            color = emotion_probability * np.asarray((0, 255, 255))
            ecl.set_surprise()
        else:
            color = emotion_probability * np.asarray((0, 255, 0))
            ecl.set_nevtral()
        # color = color.astype(int)
        # color = color.tolist()
        font = cv2.FONT_HERSHEY_SIMPLEX
        # cv2.putText(frame, label, (x - 10, y - 10), font, 1, color, 2)

        # cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
        #
        # # cv2.rectangle(frame, (x, y + size[1]), (x + size[0], y), color, cv2.FILLED)

    # cv2.imshow("result", frame)

    # if the `q` key is pressed, break from the lop
    if key == ord("q"):
        break

    # update the FPS counter
    fps.update()
# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# cleanup the camera and close any open windows
cv2.destroyAllWindows()
vs.stop()
