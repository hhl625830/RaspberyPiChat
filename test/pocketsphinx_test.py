# -*- coding:utf-8 -*-
""" 
@author:HuHongling

@file: pocketsphinx_test.py 
@time: 2019/07/03
@contact: huhonglin@hwasmart.com
@site:  
@software: PyCharm 

"""
import os
from pocketsphinx import LiveSpeech, get_model_path
import test.test_pyaudio as p

model_path = get_model_path()
print(model_path)
speech = LiveSpeech(
    verbose=False,
    sampling_rate=16000,
    buffer_size=2048,
    no_search=False,
    full_utt=False,
    hmm=os.path.join(model_path, 'zh_cn.cd_cont_5000'),
    lm=os.path.join(model_path, 'zh_cn.lm.bin'),
    dic=os.path.join(model_path, 'zh_cn.dic')
)

for phrase in speech:
    print('phrase', phrase)
    print(type(phrase))
    print(phrase.segments(detailed=True))
    # if str(phrase) in ['XIAOXIN', 'XIAOXINTONGXUE', 'XIAOXIN', 'XIAOYIN']:
    #     print("正确识别唤醒")
    #     p.play_wav('temp.wav')
