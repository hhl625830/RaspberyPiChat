#-*- coding:utf-8 -*-  
""" 
@author:HuHongling

@file: audio_device.py 
@time: 2019/07/04
@contact: huhonglin@hwasmart.com
@site:  
@software: PyCharm 

"""
# import pyaudio
#
# p = pyaudio.PyAudio()
# for i in range(p.get_device_count()):
#     print(p.get_device_info_by_index(i))
# otherwise you can do:
# print(p.get_default_input_device_info())
import os
from pocketsphinx import AudioFile, get_model_path, get_data_path

model_path = get_model_path()
data_path = get_data_path()

config = {
    'verbose': False,
    'audio_file': os.path.join(data_path, 'goforward.raw'),
    'buffer_size': 2048,
    'no_search': False,
    'full_utt': False,
    'hmm': os.path.join(model_path, 'en-us'),
    'lm': os.path.join(model_path, 'en-us.lm.bin'),
    'dict': os.path.join(model_path, 'cmudict-en-us.dict')
}

audio = AudioFile(**config)
for phrase in audio:
    print(phrase)