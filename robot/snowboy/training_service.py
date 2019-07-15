# -*- coding: utf-8 -*-

# @Time    : 2019/4/3 13:45
# @Author  : HuHongLin
# @Project : hwasmart-robot
# @FileName: training_service.py
# @Software: PyCharm

import sys
import base64
import requests


def get_wave(fname):
    with open(fname, 'rb') as infile:
        return str(base64.b64encode(infile.read()).decode("utf-8"))


endpoint = "https://snowboy.kitt.ai/api/v1/train/"


############# MODIFY THE FOLLOWING #############
token = "6d6d71ce16fa47ccefc82579f258f50120ed2f32"
hotword_name = "小新"
language = "cn"
age_group = "20_29"
gender = "M"
microphone = "RaspberrtPi microphone"
############### END OF MODIFY ##################

if __name__ == "__main__":
    try:
        [_, wav1, wav2, wav3, out] = sys.argv
    except ValueError:
        print("Usage: %s wave_file1 wave_file2 wave_file3 out_model_name" % sys.argv[0])
        sys.exit()

    data = {
        "name": hotword_name,
        "language": language,
        "age_group": age_group,
        "gender": gender,
        "microphone": microphone,
        "token": token,
        "voice_samples": [
            {"wave": get_wave(wav1)},
            {"wave": get_wave(wav2)},
            {"wave": get_wave(wav3)}
        ]
    }

    response = requests.post(endpoint, json=data)
    if response.ok:
        with open(out, "w") as outfile:
            outfile.write(response.content)
        print("Saved model to '%s'." % out)
    else:
        print("Request failed.")
        print(response.text)