from time import time, sleep
import random, sys, httplib, StringIO, json
from naoqi import ALModule, ALProxy, ALBroker
from time import sleep

# our modules
import chat

# global variables
ip = "192.168.1.143"
port = 9559
duration = 200

# human likeliness settings
pBlinkHeadsearching = 0.1
pBlinkGeneral = 0.1

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
        memory.unsubscribeToEvent("FaceDetected", self.name)

        global faceTracking

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
            print "Nose: x=", noseX, " y=", noseY

            if (faceInMiddle(noseX) and faceInMiddle(noseY)):
                print "face centered"
                faceTracking = False
            else:
                print "centering face"
                centerOnFace(noseX, noseY)

        except:
            print "missed nose"
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
        # sleep(duration)
        sleepAndBlink(duration, pBlinkGeneral)
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
        print data




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

    print "face in middle x:",  faceInMiddle(x)
    print "face in middle y:", faceInMiddle(y)

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
    # -x = left,  +x right
    # -y = top, +y = bottom



# look left look right
def lookAround():
    print("looking around")
    speed = 0.5
    joints = ["HeadYaw", "HeadPitch"]
    angles = [[-1.0, 1.0, 0], [-0.2, 0]]
    times = [[1.5, 3.0, 5.0], [1.0, 5.0]] #time in seconds
    isAbsolute = True
    motionProxy.angleInterpolation(joints, angles, times, isAbsolute)


# look a relative amount to the current head posture in a certain direction
def moveHead(headChange):
    [headChangeX, headChangeY] = headChange

    print "Head change:", headChange

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

# sleep and blink at some random points during the waiting
def sleepAndBlink(duration, probability):
    start = time()
    end = time()

    # keep on sleeping / blinking untill the duration has passed
    while end - start < duration:
        if decision(probability):
            blinkEyes()
        else:
            sleep(0.15)

################################################################################
# Main functions
################################################################################
def setup():
    global pythonBroker, FaceDetector, WittyNao

    # Set robot to default posture
    motionProxy.setStiffnesses("Head", 0.8)
    postureProxy.goToPosture("Sit", 0.6667)
    sleep(2)

    pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)

    # face detection
    FaceDetector = FaceRecognition("FaceDetector")

    # setup chatbot
    chat.test()

def main():
    global FaceDetector, WittyNao
    setup()
    blinkEyes()

    # start timer
    start = time()
    end = time()

    try:
        while faceTracking:
            # (maybe) blink eyes, and sleep otherwise
            sleepAndBlink(0.15, pBlinkHeadsearching)
            print "searching for face"

        tts.say("Hello, my name is Alice. What is your name?")

        while end - start < duration:
            sleepAndBlink(1.0, pBlinkGeneral)

            # Record audio, and send it to Wit.AI.
            # Bugfix: rewrite the class to prevent recordings with slow moted speech
            WittyNao = NaoWitSpeech("WittyNao")
            WittyNao.startAudioTest(3)
            wit_response = WittyNao.reply
            resp = json.loads(wit_response)

            # Check if we got a reponse from Wit.AI, get a reply from our
            # chatbot if so, and say it
            if len(resp) == 3:
                # print resp['_text']
                reply = chat.talk(resp['_text'])
                print "Chat reply: ", reply
                tts.say(str(reply))
            else:
                print "No response:", resp
                tts.say("Sorry I didn't get that")

            # update time
            end = time()

        tts.say("Unfortunatly our speeddate has to come to an end. It was nice talking to you.")

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
