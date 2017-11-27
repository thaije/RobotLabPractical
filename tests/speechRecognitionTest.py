import time
import sys

from naoqi import ALModule
from naoqi import ALProxy
from naoqi import ALBroker

ip = "192.168.1.103"
port = 9559

memory = ALProxy("ALMemory", ip, port)
tts = ALProxy("ALTextToSpeech", ip, port)

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
        self.response = True
        self.value = value
        print value[0]
        # tts.say ("Did you say " + value[0] + "?")

        memory.unsubscribeToEvent("WordRecognized", self.name)
        self.spr.pause(True)


    def stop(self):
        memory.unsubscribeToEvent("WordRecognized", self.name)
        self.spr.pause(True)

if __name__ == "__main__":

    # asr = ALProxy("ALSpeechRecognition", ip, port)
    # asr.pause(True)

    pythonBroker = ALBroker("pythonBroker","0.0.0.0", 9600, ip, port)
    Speecher = SpeechRecognition("Speecher")
    # Speecher.getSpeech(["left", "right", "stop", "test"], True)

    try:
        while True:
            Speecher.getSpeech(["left", "right", "stop", "test"], True)
            print "Starting speech recognition"
            while Speecher.response is False:
                time.sleep(1)

    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
        Speecher.stop()
        pythonBroker.shutdown()
        sys.exit(0)
