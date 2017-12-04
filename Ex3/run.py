# Author        :   Tjalling Haije (s1011759)
# Date          :   21-11-2017
# Course        :   Robotlab Practical, Master AI, Radboud University
# Description   :
# How to run    :   fix IP, then: python run.py
# TODO          :   - add sonar

from time import time, sleep
import random
import naoqi
import camera
import ReactToTouch.ReactToTouch as ReactToTouch
import FaceRecognition.FaceRecognition as FaceRecognition
import SpeechRecognition.SpeechRecognition as SpeechRecognition

ip = "192.168.1.143"
port = 9559

duration = 105

# walking variables
walkSpeed = 0.6
turnSpeed = 0.5
blocked = False
walking = False

# camera variables
resolution = 1
resolutionX = 320
resolutionY = 240
ballThreshold = 50
foundBall = False
videoProxy = False
cam = False

# speech recognition variables
wordlist = ["left", "right", "stop", "start"]

# proxies
postureProxy = naoqi.ALProxy("ALRobotPosture", ip ,port )
motionProxy = naoqi.ALProxy("ALMotion", ip ,port )
tts = naoqi.ALProxy("ALTextToSpeech", ip , port )
memory = ALProxy("ALMemory", ip, port)
ReactToTouch = False
Speecher = False

################################################################################
# Class for recognizing speech
################################################################################
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

        global blocked
        if value[0] is "stop":
            say("Command received, stopping")
            stopWalking()
            blocked = True
            say(str)

        if value[0] is "left":
            say("Looking left")
            look("left")

        if value[0] is "right":
            say("Looking right")
            look("right")

        if value[0] is "start" and not walking:
            say("starting")
            initRandomWalk()

        self.getSpeech(self.wordlist, self.wordspotting)

    def stop(self):
        memory.unsubscribeToEvent("WordRecognized", self.name)
        self.spr.pause(True)



################################################################################
# Class for catching touch events
################################################################################
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

        # if touch is leftFoot or touch is rightFoot:
        say("Oh no my foot hit something, avoiding")
        avoid(True)
        initRandomWalk()

        touched_bodies = []
        for p in value:
            if p[1]:
                touched_bodies.append(p[0])
        print touched_bodies

        memory.subscribeToEvent("TouchChanged", "ReactToTouch", "onTouched")



################################################################################
# Locomotion functions
################################################################################
def initRandomWalk():
    say("Continuing")
    motionProxy.moveToward(walkSpeed, 0, 0)
    global walking, blocked
    walking = True
    blocked = False


def stopWalking():
    motionProxy.stopMove()
    global walking
    walking = False


def turn(theta, direction):
    global walking
    walking = True

    # turn in which direction
    if direction is "left":
        motionProxy.moveToward(0, 0, turnSpeed * 1)
    elif direction is "random":
        leftRight = random.choice([-1, 1])
        motionProxy.moveToward(0, 0, turnSpeed * leftRight)
    elif direction is "right":
        motionProxy.moveToward(0, 0, turnSpeed * -1)

    # turn x degrees = wait n seconds
    if theta is 45:
        sleep(4)
    stopMovement()


def backwards():
    stopWalking()

    global walking
    walking = True
    motionProxy.moveToward(-1 * walkSpeed, 0, 0)
    sleep(4)
    stopWalking()


def avoid(backward):
    # block the main loop
    global blocked
    blocked = True

    if backward:
        backwards()
    turn(45, "random")
    initRandomWalk()

################################################################################
# Ball and looking functions
################################################################################
def onBallDetect(ballDetection):
    global foundBall

    if ballDetection is False:
        # announce we lost the ball
        if foundBall:
            foundBall = False
            say("Lost ball")
    else:
        # Announce that we found the ball
        if not foundBall:
            foundBall = True
            say("Ball found")
        # center on the ball
        say("Centering on ball")
        centerOnBall(ballDetection[0], ballDetection[1])


# Try to center the ball (with a certain threshold)
def centerOnBall(x, y):
    if x > (xResolution/2 + ballThreshold):
        look("left")
    elif x < (xResolution/2 - ballThreshold):
        look("right")
    elif y > (yResolution/2 + ballThreshold):
        look("up")
    elif y < (yResolution/2 - ballThreshold):
        look("down")


# look left look right
def lookAround():
    speed = 0.5
    joints = ["HeadYaw", "HeadPitch"]
    angles = [[-1.0, 1.0, 0], [-0.2, 0]]
    times = [[1.5, 3.0, 5.0], [1.0, 5.0]] #time in seconds
    isAbsolute = True
    motionProxy.angleInterpolation(joints, angles, times, isAbsolute)


# look a relative amount to the current head posture in a certain direction
def look(direction):
    speed = 0.5
    joints = ["HeadYaw", "HeadPitch"]
    isAbsolute = False
    times = [[0.5], [0.5]] #time in seconds

    # yaw = 0 # left (2) right (-2)
    # pitch = 0 # up(-0.6) down (-0.5)
    if direction is "left":
        angles = [[-0.3], [0]]
    if direction is "right":
        angles = [[0.3], [0]]
    elif direction is "up":
        angles = [[0], [-0.2]]
    elif direction is "down":
        angles = [[0], [0.2]]

    print "Looking ", direction
    motionProxy.angleInterpolation(joints, angles, times, isAbsolute)


def say(str):
    tts.say(str)
    print(str)

# def onSonarDetect():
#     avoid(False)
#     say("I sensed an object with sonar, avoiding")


################################################################################
# Main functions
################################################################################
def setup():
    global videoProxy, cam, ReactToTouch, Speecher

    pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)

    # video processing
    videoProxy, cam = camera.setupCamera(ip, port)

    # # speecher
    # Speecher = SpeechRecognition("Speecher")
    # Speecher.getSpeech(wordlist, True)
    # say("You can give me commands during walking, such as start, left, right or stop.")
    #
    # # Touch sensors
    # ReactToTouch = ReactToTouch("ReactToTouch")

    # Set robot to default posture
    postureProxy.goToPosture("StandInit", 0.6667)
    time.sleep(2)


def main():
    global videoProxy, cam
    setup()

    # start timer
    start = time()
    end = time()

    try:
        while end - start < duration:

            # get and process a camera frame
            image = camera.getFrame()
            if image:
                # Check if we can find a ball, and point the head towards it if so
                ballDetected(camera.findBall(image))

            # close the video proxy and end the script if escape is pressed
            if cv2.waitKey(33) == 27:
                videoProxy.unsubscribe(cam)
                break;

            # start a random walk
            if not walking and not blocked:
                initRandomWalk()

            # look around if we are not doing much special
            if not blocked and foundBall:
                # look around
                lookAround()

            # update time
            end = time()

    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
    finally:
        say("Shutting down after sitting")
        videoProxy.unsubscribe(cam)
        postureProxy.goToPosture("SitRelax", 0.6667)
        motionProxy.rest()
        Speecher.stop()
        pythonBroker.shutdown()
        sys.exit(0)
