
import time
import sys

from naoqi import ALModule
from naoqi import ALProxy
from naoqi import ALBroker

ip = "192.168.1.102"
port = 9559

memory = ALProxy("ALMemory", ip, port)
tts = ALProxy("ALTextToSpeech", ip, port)

# memory = ALProxy("ALMemory", ip, port)
# tts = ALProxy("ALTextToSpeech", ip, port)
#
#
# pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)
# # facep = ALProxy("ALFaceDetection", ip, port)
# # facep.subscribe("Test_Face", 500, 0.0)
#
# # val = memoryProxy.getData(memValue, 0)
#
# memory.subscribeToEvent("FaceDetected", "face", "faceCall")

def faceCall( eventName, value, subscriberIdentifier):
    print value
    print "Detected face"
    tts.say ("I see a face")
    memory.unsubscribeToEvent("FaceDetected", "face")
    pythonBroker.shutdown()


def main():

    pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)
    memory.subscribeToEvent("FaceDetected", "face", "faceCall")

    print "subscribed"
    tts.say("Starting")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"
        pythonBroker.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    main()
