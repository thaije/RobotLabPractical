# -*- encoding: UTF-8 -*-
# say My (body-part) is touched when receiving a touch event

import time
import sys
import naoqi

from naoqi import ALModule
from naoqi import ALProxy
from naoqi import ALBroker

# global variable to store the react to touch module instance
ReactToTouch = None

ip = "192.168.1.143"
port = 9559

global tts
global memory
tts = ALProxy("ALTextToSpeech", ip, port)
memory = ALProxy("ALMemory", ip, port)

class ReactToTouch(ALModule):

    def __init__(self, name):
        #We need t o u n s u b s c r i b e from any p r o x i e s s t i l l on t h e NAO t o p r e v e n t e r
        try:
            p = ALProxy(name)
            print "Proxy already exists, exiting"
            p.exit()
        except:
            print "Error but passing"
            pass
        ALModule.__init__(self, name)

        # No need f o r IP and p o r t h e r e b e c a u s e
        # we have our Python b r o k e r c o n n e c t e d t o NAOqi b r o k e r

        # create a proxy to ALTextToSpeech for later use
        self.tts = ALProxy("ALTextToSpeech")

        #subscribe to touchChanged event:
        memory.subscribeToEvent("TouchChanged", name, "onTouched")
        self.footTouched = False



    def onTouched(self, strVarName, value):
        memory.unsubscribeToEvent("TouchChanged", name)

        touched_bodies = []
        for p in value:
            if p[1]:
                touched_bodies.append(p[0])
        self.say(touched_bodies)

        # susbcribe again to the event
        memory.subscribeToEvent("TouchChanged", name, "onTouched")

    def say(self, bodies):
        if (bodies == []):
            return

        sentence = "My " + bodies[0]
        for b in bodies[1:]:
            sentences = sentences + " and my " + b
        if (len(bodies) > 1):
            sentences = sentences + " are"
        else:
            sentence = sentence + " is"
        sentence = sentence + " touched."

        self.tts.say(sentence)
        print(bodies)


if __name__ == "__main__":
    pythonBroker = ALBroker ("pythonBroker" ,"0.0.0.0" ,9600 , ip , port)
    yourname = ReactToTouch("ReactToTouch")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt :
        print
        print "Interrupted by user, shutting down"
        pythonBroker.shutdown()
        sys.exit(0)
