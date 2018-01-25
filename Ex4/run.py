# Author        :   Tjalling Haije (s1011759)
# Date          :   13-12-2017
# Course        :   Robotlab Practical, Master AI, Radboud University
# Description   :   Lets NAO do a speed date by using Wit.AI for speech recognition,
#                   a chatbot for replies and random gestures inbetween.
#                   See report.txt for details
# How to run    :   fix ip variable, then: python run.py


from time import time, sleep
import random, sys, httplib, StringIO, json
from naoqi import ALModule, ALProxy, ALBroker

# our modules
import chat

# global variables
ip = "192.168.1.137"
port = 9559
duration = 120

# human likeliness settings
actionProbabilities = {"nod" : 0.05, "blink" : 0.15, "lookAway": 0.1}
movedHeadAway = False
lastHeadYaw = -1
lastHeadPitch = -1


# proxies
postureProxy = ALProxy("ALRobotPosture", ip ,port )
motionProxy = ALProxy("ALMotion", ip ,port )
tts = ALProxy("ALTextToSpeech", ip , port )
memory = ALProxy("ALMemory", ip, port)
aup = ALProxy("ALAudioPlayer", ip ,port )
LED = ALProxy("ALLeds",ip, port)


# Face tracking variables
FaceDetector = False
faceTracking = True
faceInView = False
# when is the face in the middle
threshold = 0.10
# how much do we move the head as a minimum
defaultChangeY = 0.05
defaultChangeX = 0.15
# Determines how much the minimum head movement is multiplied when the face is
# further away from the center
multiplierHeadX = 0.3
multiplierHeadY = 0.15


# disable ALAutonomousMoves bug during listening
am = ALProxy("ALAutonomousMoves", ip ,port )
am.setExpressiveListeningEnabled(False)
am.setBackgroundStrategy("none")


################################################################################
# Class for detecting faces
################################################################################
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



    def faceCall(self, eventName, value, subscriberIdentifier):
        global faceTracking
        memory.unsubscribeToEvent("FaceDetected", self.name)

        # return if we don't need to track faces
        if not faceTracking:
            memory.subscribeToEvent("FaceDetected", self.name, "faceCall")
            return

        print "Detected face"

        # see docs for value object
        # http://doc.aldebaran.com/2-1/naoqi/peopleperception/alfacedetection.html
        # Test if NAO found a nose
        try:
            noseX = value[1][0][1][7][0]
            noseY = value[1][0][1][7][1]
            print "--->Nose at: x=", noseX, " y=", noseY

            if (faceInMiddle(noseX) and faceInMiddle(noseY)):
                print "------>Face centered on nose"
                faceTracking = False
            else:
                print "------>Centering face on nose"
                centerOnFace(noseX, noseY)

        except:
            print "--->Found face but no nose"
            pass

        memory.subscribeToEvent("FaceDetected", self.name, "faceCall")




################################################################################
# Speech recognition class
################################################################################
class NaoWitSpeech(ALModule):
    def __init__(self, name):
        """For writing audio to an external service"""

        try:
            p = ALProxy(name)
            p.exit()
        except:
            pass
        ALModule.__init__(self, name)

        self.saveFile = StringIO.StringIO()
        self.ALAudioDevice = ALProxy("ALAudioDevice")
        channels = [0,1,0,0]
        self.ALAudioDevice.setClientPreferences(self.getName(), 48000, channels, 0, 0)


    def processRemote(self, nbOfInputChannels, nbOfInputSamples, timeStamp, inputBuff):
        """
            Incoming method for data, writes it to savefile. For remote use.
            Note that docstring is mandatory!
        """
        self.saveFile.write(inputBuff)


    def process(self, nbOfInputChannels, nbOfInputSamples, timeStamp, inputBuff):
        """ asda """

    def startWit(self):
        """
            Method for creating the call to wit.ai
        """
        self.headers = {'Authorization': 'Bearer TRSNYO4JDAQ7LWEHD35UI456JWPIUANE'}
        self.headers['Content-Type'] = 'audio/raw;encoding=signed-integer;bits=16;rate=48000;endian=little'


    def startAudioTest(self, duration):
        """
        subscribe for audio data.
        """
        aup.post.playFile("/usr/share/naoqi/wav/begin_reco.wav")
        self.startWit()
        self.ALAudioDevice.subscribe(self.getName())

        # waste time, and at start don't immediatly nod
        wasteTimeHumanlike(duration, ["blink", "lookAway", "nod"])

        self.ALAudioDevice.unsubscribe(self.getName())
        aup.post.playFile("/usr/share/naoqi/wav/end_reco.wav")
        self.startUpload(self.saveFile)


    def startUpload(self, datafile):
        """
        Start upload of speechfile.
        """
        conn = httplib.HTTPSConnection("api.wit.ai")
        conn.request("POST", "/speech", datafile.getvalue(), self.headers)
        response = conn.getresponse()
        data = response.read()
        self.reply = data


################################################################################
# Looking / sensing functions
################################################################################
def faceInMiddle(coord):
    if (abs(coord) - threshold > 0):
        return False
    return True

# Try to center on a face
def centerOnFace(x, y):
    # headyaw, headpitch
    headChange = [1, 1]

    multiplHeadX = abs(x / multiplierHeadX)
    multiplHeadY = abs(y / multiplierHeadY)
    if multiplHeadX == 0:
        multiplHeadX = 1
    if multiplHeadY == 0:
        multiplHeadY = 1

    # look left
    if not faceInMiddle(x) and x > 0:
        headChange[0] = headChange[0] * 1 * multiplHeadX
    # look right
    elif not faceInMiddle(x) and x < 0:
        headChange[0] = headChange[0] * -1 * multiplHeadX

    # look down
    if not faceInMiddle(y) and y > 0:
        headChange[1] = headChange[1] * 1 * multiplHeadY
    # look up
    elif not faceInMiddle(y) and y < 0:
        headChange[1] = headChange[1] * -1 * multiplHeadY

    # move the head to the new coordinates
    moveHead(headChange)


# look left look right
def lookAround():
    print("Looking around")
    speed = 0.5
    joints = ["HeadYaw", "HeadPitch"]
    angles = [[-1.0, 1.0, 0], [-0.2, 0]]
    times = [[1.5, 3.0, 5.0], [1.0, 5.0]] #time in seconds
    isAbsolute = True
    motionProxy.angleInterpolation(joints, angles, times, isAbsolute)


# look a relative amount to the current head posture in a certain direction
def moveHead(headChange):
    [headChangeX, headChangeY] = headChange
    print "---------->Head change:", headChange

    speed = 0.5
    joints = ["HeadYaw", "HeadPitch"]
    isAbsolute = False
    times = [[0.3], [0.3]] #time in seconds

    # We move the head a default amount horizontal/vertical, which is adapted
    # by how far the head is from the middle (further = larger headmovement)
    angles = [[defaultChangeX * headChangeX], [defaultChangeY * headChangeY]]
    motionProxy.angleInterpolation(joints, angles, times, isAbsolute)



################################################################################
# Human likeliness functions
################################################################################
def decision(probability):
    return random.random() < probability

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
    angles = [-0.25, 0.15, -0.15, 0.05]
    motionProxy.angleInterpolation(joints, angles, times, isAbsolute)
    blinkEyes()

# move the head away, or back to the user
def lookAway():
    global movedHeadAway, lastHeadYaw,lastHeadPitch

    speed = 0.5
    joints = ["HeadYaw", "HeadPitch"]
    times = [1.0, 1.0] #time in seconds
    isAbsolute = False

    angles = [-lastHeadYaw, -lastHeadPitch]

    # move the head away
    if not movedHeadAway:
        lastHeadYaw = random.uniform(-0.7, 0.7)
        lastHeadPitch = random.uniform(-0.2, 0.4)
        angles = [lastHeadYaw, lastHeadPitch]
        movedHeadAway = True
    # otherwise move the head back to the middle
    else:
        movedHeadAway = False

    print("looking away/back")
    motionProxy.angleInterpolation(joints, angles, times, isAbsolute)
    blinkEyes()


# This function does a fancy sleep of duration x in small steps, and can do a
# random action such as blink, nod, or looking away during the sleep to waste time
def wasteTimeHumanlike(duration, actions):
    start = time()
    end = time()

    print ("Wasting time human like for %.1f seconds" % duration)

    # Loop untill the duration has passed
    while end - start < duration:
        actionDone = False
        random.shuffle(actions)

        # decide for each possible action randomly if we do it, we only execute
        # max one action each loop
        for action in actions:

            # get the probability of this action
            p = actionProbabilities[action]

            # randomly decide if we do this action, and break the for loop if so
            if decision(p):
                actionDone = True
                print "--->Do action:", action

                if action == "blink":
                    blinkEyes()
                elif action == "nod":
                    nodHead()
                elif action == "lookAway":
                    lookAway()
                break
        # if we did no action this loop, do a sleep
        if not actionDone:
            sleep(0.15)

        end = time()


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

    # face detection
    FaceDetector = FaceRecognition("FaceDetector")

    # setup chatbot
    chat.test()

if __name__ == "__main__":
    setup()
    blinkEyes()

    # start timer
    start = time()
    end = time()

    try:

        # print "--3--"
        # wasteTimeHumanlike(3.0, ["blink", "lookAway", "nod"])
        # sleep(1)
        #
        # print "--3--"
        # wasteTimeHumanlike(3.0, ["blink", "lookAway", "nod"])
        # sleep(1)
        #
        # print "--3--"
        # wasteTimeHumanlike(3.0, ["blink", "lookAway", "nod"])
        # sleep(1)
        #
        # return

        print "Searching for face"
        # first focus on face before continuing
        # while faceTracking:
        #     # (maybe) blink eyes, and sleep otherwise
        #     wasteTimeHumanlike(0.25, ["blink"])
        # print "Face found"

        tts.say("Hello, my name is Alice.")
        blinkEyes()
        tts.say("What is your name?")
        blinkEyes()

        while end - start < duration:
            # Record audio, and send it to Wit.AI.
            # Bugfix: rewrite the class to prevent recordings with slow motion speech
            WittyNao = NaoWitSpeech("WittyNao")
            WittyNao.startAudioTest(3)
            wit_response = WittyNao.reply
            resp = json.loads(wit_response)

            # Check if we got a reponse from Wit.AI, get a reply from our
            # chatbot if so and say it
            if len(resp) == 3:
                print "User:", resp['_text']
                reply = chat.talk(resp['_text'])
                print "Chat reply: ", reply
                tts.say(str(reply))
            else:
                print "No response:", resp
                tts.say("Sorry I didn't get that")

            # waste some time for the user to think
            wasteTimeHumanlike(1.0, ["blink", "lookAway"])

            # update time
            end = time()

        # End
        blinkEyes()
        tts.say("Unfortunatly our speeddate has to come to an end. It was nice talking to you.")
        blinkEyes()
        sleep(0.2)
        blinkEyes()

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
