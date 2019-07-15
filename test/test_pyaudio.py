# -*- coding:utf-8 _-*-
""" 
@author:HuHongling

@file: test_pyaudio.py 
@time: 2019/07/02
@contact: huhonglin@hwasmart.com
@site: PyAudio Example: play a WAVE file
@software: PyCharm 

"""
import pyaudio
import wave
import numpy as np


def play_wav(filename):
    filename = 'temp.wav'
    CHUNK = 1024
    wf = wave.open(filename, 'rb')
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(CHUNK)

    while data != '':
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()

    p.terminate()
