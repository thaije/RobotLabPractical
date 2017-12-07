from time import time, sleep
import random, sys

from naoqi import ALModule, ALProxy, ALBroker

ip = "192.168.1.102"
port = 9559

duration = 200

# proxies
postureProxy = ALProxy("ALRobotPosture", ip ,port )
motionProxy = ALProxy("ALMotion", ip ,port )
tts = ALProxy("ALTextToSpeech", ip , port )
memory = ALProxy("ALMemory", ip, port)
FaceDetector = False


# Face tracking variables
faceTracking = True
faceInView = False
# when is the face in the middle
threshold = 0.05
# how much do we move the head as a minimum
defaultChangeY = 0.05
defaultChangeX = 0.1
# Determines how much the minimum head movement is multiplied when the face is
# further away from the center
multiplierHeadX = 0.05
multiplierHeadY = 0.03



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

            centerOnFace(noseX, noseY)
        except:
            print "missed nose"
            pass

        memory.subscribeToEvent("FaceDetected", self.name, "faceCall")



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
    multiplHeady = abs(y / multiplierHeadY)

    # look left
    if faceInMiddle(x) and x > 0:
        headChange[0] = headChange[0] * 1 * multiplHeadX
    # look right
    elif faceInMiddle(x) and x < 0:
        headChange[0] = headChange[0] * -1 * multiplHeadX

    # look down
    if faceInMiddle(y) and y > 0:
        headChange[1] = headChange[1] * 1 * multiplHeady
    # look up
    elif faceInMiddle(y) and y < 0:
        headChange[1] = headChange[1] * -1 * multiplHeady

    # move the head to the new coordinates
    moveHead(headChange)


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
def moveHead([headChangeX, headChangeY]):
    speed = 0.5
    joints = ["HeadYaw", "HeadPitch"]
    isAbsolute = False
    times = [[0.3], [0.3]] #time in seconds

    # We move the head a default amount horizontal/vertical, which is adapted
    # by how far the head is from the middle (further = larger headmovement)
    angles = [[defaultChangeX * headChangeX], [defaultChangeY * headChangeY]]

    print "Looking ", direction
    motionProxy.angleInterpolation(joints, angles, times, isAbsolute)



################################################################################
# Main functions
################################################################################
def setup():
    global pythonBroker, FaceDetector

    # Set robot to default posture
    motionProxy.setStiffnesses("Head", 0.8)
    # postureProxy.goToPosture("StandInit", 0.6667)
    # sleep(2)

    pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)

    # face detection
    FaceDetector = FaceRecognition("FaceDetector")


def main():
    global FaceDetector
    setup()

    # start timer
    start = time()
    end = time()

    try:
        while end - start < duration:

            # lookAround()

            sleep(0.5)

            # update time
            end = time()

        say("This was my presentation")

    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
    except Exception, e:
        print "Unexpected error:", sys.exc_info()[0] , ": ", str(e)
    finally:
        print("Shutting down after sitting")
        # postureProxy.goToPosture("SitRelax", 0.6667)
        motionProxy.rest()
        pythonBroker.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    main()
