from time import sleep
import sys
import naoqi

from naoqi import ALModule, ALProxy, ALBroker

#ReactToTouch = None

ip = "192.168.1.103"
port = 9559

memory = ALProxy("ALMemory", ip, port)
asl = ALProxy("ALSoundLocalization", ip, port)

# http://doc.aldebaran.com/2-1/naoqi/audio/alsoundlocalization.html
# http://doc.aldebaran.com/2-1/naoqi/audio/alsoundlocalization-api.html#alsoundlocalization-api
class AudioLocalization(ALModule):

    def __init__(self, name):
        try:
            p = ALProxy(name)
            p.exit()
        except:
            pass
        ALModule.__init__(self,name)
        # self.asl = ALProxy("ALAudioSourceLocalization")
        self.name = name
        memory.subscribeToEvent("SoundLocated", name, "onSoundLocated")


    def onSoundLocated(self, eventName, value, subscriberIdentifier):
        memory.unsubscribeToEvent("SoundLocated", self.name)

        print value

        memory.subscribeToEvent("SoundLocated", self.name, "onSoundLocated")


if __name__ == "__main__":
    pythonBroker = ALBroker("pythonBroker", "0.0.0.0", 9559, ip, port)
    LocalizeAudio = AudioLocalization("LocalizeAudio")

    try:
        while True:
            sleep(0.5)

    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
    finally:
        pythonBroker.shutdown()
        sys.exit(0)
