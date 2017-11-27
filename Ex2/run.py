import time
import sys
import naoqi
import random

from naoqi import ALModule
from naoqi import ALProxy
from naoqi import ALBroker

ip = "192.168.1.103"
port = 9559


duration = 105

postureProxy = naoqi.ALProxy("ALRobotPosture", ip ,port )
motionProxy = naoqi.ALProxy("ALMotion", ip ,port )
tts = naoqi.ALProxy("ALTextToSpeech", ip , port )
memory = ALProxy("ALMemory", ip, port)


# class FaceDetection(ALModule)
#     def __init__(self, name):
#         try:
#             p = ALProxy(name)
#             p.exit()
#         except:
#             pass
#
#         ALModule.__init__(self, name)
#         self.response = False
#         self.value = []
#         self.name = name
#
#     def getFace(self):
#         facep.subscribe("Test_Face", 500, 0.0)
#         memory.subscribeToEvent("FaceDetected", self.name, "faceCall")
#         self.response = False
#
#     def faceCall(self, eventName, value, subscriberIdentifier):
#         self.response = True
#         self.value = value
#         print value
#         tts.say ("I see a face")
#         memory.unsubscribeToEvent("FaceDetected", self.name)


class SpeechRecognition(ALModule):

    def __init__(self, name):
        try:
            p = ALProxy(name)
            p.exit()
        except:
            pass

        ALModule.__init__(self, name)
        self.response = False
        self.value = []
        self.name = name
        self.spr = ALProxy("ALSpeechRecognition")

    def getSpeech(self, wordlist, wordspotting):
        self.response = False
        self.value = []
        self.spr.setVocabulary(wordlist, wordspotting)
        memory.subscribeToEvent("WordRecognized", self.name, "onDetect")

    def onDetect(self, keyname, value, subscriber_name):

        if value == "left":
            motionProxy.stopMove()
            motionProxy.moveToward(0, 0, 0.5)
            time.sleep(6)
            motionProxy.stopMove()

        elif value == "right":
            motionProxy.stopMove()
            motionProxy.moveToward(0, 0, -0.5)
            time.sleep(6)
            motionProxy.stopMove()

        elif value == "stop":
            motionProxy.stopMove()

        self.response = True
        self.value = value
        print value
        memory.unsubscribeToEvent("WordRecognized", self.name)
        self.spr.pause(True)


class ReactToTouch(ALModule):

    def __init__(self, name):
        try:
            p = ALProxy(name)
            p.exit()
        except:
            pass
        ALModule.__init__(self,name)

        memory.subscribeToEvent("TouchChanged", name, "onTouched")
        self.footTouched = False

    def onTouched(self, strVarName, value):
        memory.unsubscribeToEvent("TouchChanged", "ReactToTouch")

        tts.say ("Ouch. Baby don't hurt me")

        # go left
        motionProxy.stopMove()
        motionProxy.moveToward(0, 0, 0.5)
        time.sleep(6)
        motionProxy.stopMove()

        touched_bodies = []
        for p in value:
            if p[1]:
                touched_bodies.append(p[0])
        print touched_bodies

        memory.subscribeToEvent("TouchChanged", "ReactToTouch", "onTouched")




if __name__ == "__main__":
    pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)

    # speecher
    Speecher = SpeechRecognition("Speecher")

    # Face detector
    # FaceDetector = FaceDetection("FaceDetector")

    # Touch sensors
    ReactToTouch = ReactToTouch("ReactToTouch")

    # start timer
    start = time.time()
    end = time.time()

    postureProxy.goToPosture("StandInit", 0.6667)


    while end - start < duration:

        time.sleep(1)

        # generate a random duration for the walk (3-7 seconds)
        walkDuration = random.randint(8, 15)

        # Make sure to stand
        postureProxy.goToPosture("StandInit", 0.6667)

        # move for some time
        motionProxy.moveToward(0.667, 0, 0)
        time.sleep(walkDuration * 0.5)
        motionProxy.stopMove()

        # Ask for feedback
        print "Please give me an commando, such as left, right or stop"
        tts.say("Please give me an commando. Such as left, right or stop")
        Speecher.getSpeech(["left", "right", "stop"], True)
        while Speecher.response is False:
            time.sleep(1)
        print "Heard commando, continuing"

        # move the second half
        motionProxy.moveToward(0.667, 0, 0)
        time.sleep(walkDuration * 0.5)
        motionProxy.stopMove()

        # # look for faces
        # FaceDetector.getFace()
        # while FaceDetector.response is False:
        #     time.sleep(1)
        #     print "Found face, continuing"

        # update time
        end = time.time()

    postureProxy.goToPosture("StandInit", 0.6667)
    motionProxy.rest()
