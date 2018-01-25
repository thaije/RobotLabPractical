# Author        :   Tjalling Haije (s1011759)
# Date          :   19-12-2017
# Course        :   Robotlab Practical, Master AI, Radboud University
# Description   :   Lets NAO execute an exam for military gestures. Please see
#                   report.txt for details.
# How to run    :   Fix ip variable, then: python run.py

from time import time, sleep
import random, sys
from naoqi import ALModule, ALProxy, ALBroker

# our modules
from gestureRecognition import *

# global variables
ip = "192.168.1.102"
port = 9559

# proxies
postureProxy = ALProxy("ALRobotPosture", ip ,port )
motionProxy = ALProxy("ALMotion", ip ,port )
tts = ALProxy("ALTextToSpeech", ip , port )
memory = ALProxy("ALMemory", ip, port)
aup = ALProxy("ALAudioPlayer", ip ,port )
LED = ALProxy("ALLeds",ip, port)


################################################################################
# Communication functions
################################################################################
# blink eyes based on a probability to keep it random
def blinkEyes():
    LED.off("FaceLeds")
    sleep(0.15)
    LED.on("FaceLeds")

# nod head
def nodHead():
    speed = 0.5
    joints = "HeadPitch"
    isAbsolute = False
    times = [0.4, 0.8, 1.2, 1.6 ] #time in seconds
    angles = [-0.25, 0.15, -0.25, 0.05]
    motionProxy.angleInterpolation(joints, angles, times, isAbsolute)
    blinkEyes()


# nod head no
def nodHeadNo():
    speed = 0.5
    joints = "HeadYaw"
    isAbsolute = False
    times = [0.4, 0.8, 1.2, 1.6 ] #time in seconds
    angles = [-0.25, 0.15, -0.20, 0.05]
    motionProxy.angleInterpolation(joints, angles, times, isAbsolute)
    blinkEyes()


# introduction to the game
def intro():
    blinkEyes()
    tts.say("Hello Private. My name is Lieutenant Jarvis and I will guide you through the military exam for combat gestures.")
    tts.say("First. What is your name?")
    blinkEyes()
    blinkEyes()
    sleep(0.5)

    aup.post.playFile("/usr/share/naoqi/wav/begin_reco.wav")
    sleep(2)
    aup.post.playFile("/usr/share/naoqi/wav/end_reco.wav")
    sleep(1)
    blinkEyes()
    tts.say("Okay. Private Ryan. The three movements which will be tested are the following.")
    blinkEyes()
    blinkEyes()

    tts.say("First move is called: Halt")
    doHalt()
    sleep(1)

    tts.say("Second gesture is called: Map check")
    doMapCheck()
    blinkEyes()
    sleep(1)

    tts.say("Third gesture is called: Double-time")
    doDoubleTime()
    sleep(1)

################################################################################
# Gesture examples functions
################################################################################
def doHalt():
    print "halt"

def doMapCheck():
    print "mapcheck"

def doDoubleTime():
    print "double time"

################################################################################
# Main functions
################################################################################
def setup():
    global pythonBroker, FaceDetector

    # Set robot to default posture
    postureProxy.goToPosture("Sit", 0.6667)
    motionProxy.rest()
    motionProxy.setStiffnesses("Head", 0.8)

    pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)


def main():
    setup()
    # intro()

    gestures = ["Halt", "MapCheck", "DoubleTime"]
    try:

        tts.say("Now the exam will start. Stand ready before the camera.")
        blinkEyes()
        blinkEyes()
        sleep(2)
        blinkEyes()

        score = 0
        # loop through our gestures
        for g in gestures:
            tts.say("Show me the gesture:" + g)
            sleep(2)

            index = 0

            # Try to recognize the gesture, and give the user 1 retry if false
            while index < 2:
                blinkEyes()
                index += 1
                response = recognizeGestures()

                blinkEyes()
                if response == g:
                    score += 1
                    nodHead()
                    tts.say("Well done.")
                    break

                if response == "notrecognized":
                    nodHeadNo()
                    tts.say("I didn't recognize that")
                else:
                    nodHeadNo()
                    tts.say("That was the wrong gesture " + g)

                if index == 1:
                    tts.say("Let's try one more time. Get ready")
                    sleep(2)
                    tts.say("Start")

        # looped through all the gestures
        blinkEyes()
        tts.say("That was the exam.")
        sleep(0.5)

        # check score and give user feedback
        tts.say("Your score is. " + str(score) + ". Out of 3.")
        blinkEyes()
        if score == 3:
            tts.say("So you passed! Congratulations")
        else:
            tts.say("You didn't pass! Better luck next time")


    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
    except Exception, e:
        print "Unexpected error:", sys.exc_info()[0] , ": ", str(e)
    finally:
        print("Shutting down after sitting")
        postureProxy.goToPosture("Sit", 0.6667)
        motionProxy.rest()
        pythonBroker.shutdown()
        sys.exit(0)



if __name__ == "__main__":
    main()
