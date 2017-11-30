# Author        :   Tjalling Haije (s1011759)
# Date          :   21-11-2017
# Course        :   Robotlab Practical, Master AI, Radboud University
# Description   :   This file makes a NAO robot randomly walk around,
#                   while reacting to touch (by default goes left), detects
#                   faces and reacts to speech commands ()

#                   At the moment the speech recognition is uncommented
#                   because it gives problems: the robot takes a
#                   full standing posture at random and loses its balance.
#                   I wasn't able to fully debug this, but to show it works
#                   seperatly I include the file SpeechRecognitionTest.py
#                   which only does the SpeechRecognition and works.
#                   To test it please uncomment line 212-214 


# How to run:
# - connect to the robotlab wifi
# - correct the IP address below
# - python run.py

import time
import sys
import naoqi
import random

from naoqi import ALModule
from naoqi import ALProxy
from naoqi import ALBroker

ip = "192.168.1.143"
port = 9559


duration = 105

postureProxy = naoqi.ALProxy("ALRobotPosture", ip ,port )
motionProxy = naoqi.ALProxy("ALMotion", ip ,port )
tts = naoqi.ALProxy("ALTextToSpeech", ip , port )
memory = ALProxy("ALMemory", ip, port)



class FaceRecognition(ALModule):

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

        self.facep = ALProxy("ALFaceDetection", ip, port)
        self.facep.subscribe("Test_Face", 500, 0.0)
        memory.subscribeToEvent("FaceDetected", self.name, "faceCall")

        print "initiliazed face recogntion"
        tts.say ("Checking for faces")



    def faceCall(self, eventName, value, subscriberIdentifier):
        memory.unsubscribeToEvent("FaceDetected", self.name)

        self.value = value
        print "Detected face"
        tts.say ("Hello handsome")

        memory.subscribeToEvent("FaceDetected", self.name, "faceCall")


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
        self.wordlist = []
        self.wordspotting = False
        self.spr = ALProxy("ALSpeechRecognition")


    def getSpeech(self, wordlist, wordspotting):
        self.response = False
        self.value = []
        self.wordlist = wordlist
        self.wordspotting = wordspotting

        self.spr.setVocabulary(self.wordlist, self.wordspotting)
        memory.subscribeToEvent("WordRecognized", self.name, "onDetect")


    def onDetect(self, keyname, value, subscriber_name):
        memory.unsubscribeToEvent("WordRecognized", self.name)
        self.spr.pause(True)

        self.response = True
        self.value = value
        print value[0]
        tts.say ("I think you said. " + value[0])

        if value[0] == "left":
            motionProxy.stopMove()
            postureProxy.goToPosture("StandInit", 0.6667)

            tts.say("Going left")

            motionProxy.moveToward(0, 0, 0.5)
            time.sleep(4)
            motionProxy.stopMove()

        elif value[0] == "right":
            motionProxy.stopMove()
            postureProxy.goToPosture("StandInit", 0.6667)

            tts.say("Going right")

            motionProxy.moveToward(0, 0, -0.5)
            time.sleep(4)
            motionProxy.stopMove()

        elif value[0] == "stop":
            tts.say("Stopping current movement")
            sleep(1)
            motionProxy.stopMove()
            postureProxy.goToPosture("StandInit", 0.6667)

        self.getSpeech(self.wordlist, self.wordspotting)


    def stop(self):
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

        tts.say("Ouch. Baby don't hurt me")

        # go left
        motionProxy.stopMove()
        tts.say("Moving left")
        motionProxy.moveToward(0, 0, 0.5)
        time.sleep(6)
        motionProxy.stopMove()

        touched_bodies = []
        for p in value:
            if p[1]:
                touched_bodies.append(p[0])
        print touched_bodies

        memory.subscribeToEvent("TouchChanged", "ReactToTouch", "onTouched")


def moveHead():
    postureProxy.goToPosture("StandInit", 0.6667)
    sleep(1)

    speed = 0.5
    joints = ["HeadYaw", "HeadPitch"]
    angles = [[-1.0, 1.0, 0], [-0.2, 0]]
    times = [[1.5, 3.0, 5.0], [1.0, 5.0]] #time in seconds
    isAbsolute = True

    tts.say("Is someone there?")

    # motionProxy.setStiffnesses("Head", 0.8)
    motionProxy.angleInterpolation(joints, angles, times, isAbsolute)


if __name__ == "__main__":
    pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)

    try:

        wordlist = ["left", "right", "stop"]

        tts.say("Starting.")

        postureProxy.goToPosture("StandInit", 0.6667)
        time.sleep(2)

        # speecher
        # Speecher = SpeechRecognition("Speecher")
        # Speecher.getSpeech(wordlist, True)
        # tts.say("You can give me commands during walking, such as left, right or stop.")

        # Face detector
        FaceDetector = FaceRecognition("FaceDetector")

        # Touch sensors
        ReactToTouch = ReactToTouch("ReactToTouch")

        # start timer
        start = time.time()
        end = time.time()

        while end - start < duration:

            time.sleep(1)

            # generate a random duration for the walk (3-7 seconds)
            walkDuration = random.randint(8, 15)

            # Make sure to stand
            postureProxy.goToPosture("StandInit", 0.6667)

            # move for some time
            motionProxy.moveToward(0.667, 0, 0)
            time.sleep(walkDuration)
            motionProxy.stopMove()

            postureProxy.goToPosture("StandInit", 0.6667)

            # moveHead()

            # move the second half
            motionProxy.moveToward(0.667, 0, 0)
            time.sleep(walkDuration * 0.5)
            motionProxy.stopMove()

            # update time
            end = time.time()


        postureProxy.goToPosture("SitRelax", 0.6667)
        motionProxy.rest()

    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"

    finally:
        print "Shutting down after sitting"
        postureProxy.goToPosture("SitRelax", 0.6667)
        motionProxy.rest()
        Speecher.stop()
        pythonBroker.shutdown()
        sys.exit(0)
