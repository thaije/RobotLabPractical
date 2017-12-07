from naoqi import ALProxy
from time import sleep

ip = "192.168.1.102"
port = 9559


aup = ALProxy("ALAudioPlayer", ip ,port )

fileId = aup.post.playFile("/usr/share/naoqi/wav/begin_reco.wav")

sleep(2.0)

fileId = aup.post.playFile("/usr/share/naoqi/wav/end_reco.wav")
