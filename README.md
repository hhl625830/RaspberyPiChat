# RaspberyPiChat
Raspberry pi snowbot baidu ASR

hello python

本项目初步实现基于树莓派的离线语音Snowboy热词唤醒和树莓派语音交互


**1**  Before we get started with setting up the Snowboy Hotword detection on our Raspberry Pi, we
       must first ensure that we have our audio configured correctly
       we will be achieving this by creating a configuration for the audio driver. Before we do this,
       we must retrieve the card and device numbers fo both our audio output and our microphone input
      
       ~~1A~~ local your micophone
            arecord -l
            
            pi@raspberrypi:~ $ arecord -l
            **** List of CAPTURE Hardware Devices ****
            card 1: Camera [USB 2.0 PC Camera], device 0: USB Audio [USB Audio]
              Subdevices: 1/1
              Subdevice #0: subdevice #0
              
            card 1          Card#(Microphone)
            device 0        USB Device Name
            device 0        Device #
            
       ~~1B~~ local the speaker
            aplay-l
           
            **** List of PLAYBACK Hardware Devices ****
            card 0: ALSA [bcm2835 ALSA], device 0: bcm2835 ALSA [bcm2835 ALSA]
              Subdevices: 7/7
              Subdevice #0: subdevice #0
              Subdevice #1: subdevice #1
              Subdevice #2: subdevice #2
              Subdevice #3: subdevice #3
              Subdevice #4: subdevice #4
              Subdevice #5: subdevice #5
              Subdevice #6: subdevice #6
            card 0: ALSA [bcm2835 ALSA], device 1: bcm2835 IEC958/HDMI [bcm2835 IEC958/HDMI]
              Subdevices: 1/1
              Subdevice #0: subdevice #0
            card 2: Device [USB2.0 Device], device 0: USB Audio [USB Audio]
              Subdevices: 1/1
              Subdevice #0: subdevice #0
              
              
            card 2          Card#(Speaker/Headphone)
            [USB2.0 Device] USB Device Name
            device 0        Device #
      
**2**  Now all the values that we need to configure our audio driver we can 
       go ahead and create the .asoundrc file.
       
       nano /home/pi/.asoundrc
       
       
**3**  in this file. we need to enter the following configuration lines, Thess will set up our audio driver
        by telling it the specific devices that it should be utilizing
        
        pcm.!default {
          type asym
          capture.pcm "mic"
          playback.pcm "speaker"
        }
        pcm.speaker {
          type plug
          slave {
            pcm "hw:1,0"
          }
        }
        pcm.mic {
          type plug
          slave {
            pcm "hw:0,1"
          }
        }          

**4**   test your playback
        speaker-test -t wav -c 2
        
        ####
        speaker-test 1.1.3

        Playback device is default
        Stream parameters are 48000Hz, S16_LE, 2 channels
        WAV file(s)
        Rate set to 48000Hz (requested 48000Hz)
        Buffer size range from 96 to 262144
        Period size range from 48 to 131072
        Using max buffer size 262144
        Periods = 4
        was set period_size = 65536
        was set buffer_size = 262144
         0 - Front Left
         1 - Front Right
        Time per period = 5.548007
         0 - Front Left
         1 - Front Right
        Time per period = 5.599825
         0 - Front Left
         1 - Front Right
        #####
        您应该能够听到您的扬声器/耳机上的测试音频样本。
        You should be able to hear a sample test audio on your speaker/headset.
        
**5**   test you Recording Device(Microphone)

        录音5秒
        arecord --format=S16_LE --duration=5 --rate=16000 --file-type=raw out.raw
        或者
        arecord -d 3 temp.wav
        播放录音文件 你可以用下面的命令
        aplay --format=S16_LE --rate=16000 out.raw
        或
        aplay temp.wav 
        
**6**   Microphone and Speaker Volume Control
        
        alsamixer
        
**7**   install pyaudio
        
        sudo apt-get update && sudo apt-get upgrade -y      
        sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev python3-pyaudio -y
        git clone http://people.csail.mit.edu/hubert/git/pyaudio.git
        cd pyaudio
        python setup.py install
        
**8**   Finally, we can download Snowboy itself to our Raspberry Pi, To do this use the following
        command on your Raspberry Pi to grab the latest compiled version for the Raspberry Pi
        
        
        Install swig
        wget http://hahack-1253537070.file.myqcloud.com/misc/swig-3.0.10.tar.gz
        tar xvf swig-3.0.10.tar.gz
        cd swig-3.0.10
        sudo apt-get -y update
        sudo apt-get install -y libpcre3 libpcre3-dev
        ./configure --prefix=/usr --without-clisp --without-maximum-compile-warnings
        make
        make install
        install -v -m755 -d /usr/share/doc/swig-3.0.10
        sudo cp -v -R Doc/* /usr/share/doc/swig-3.0.10
        sudo apt-get install -y libatlas-base-dev
        
        wget -O snowboy.tar.bz2 https://go.pimylifeup.com/napoRs/snowboy
        tar xvjr snowboy.tar.bz2
        
        mv rpi-arm-raspbian-8.0-1.1.1/ snowboy/
        cd snowboy
        
        













