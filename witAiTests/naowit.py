global NaoWit

import httplib, StringIO, json
from naoqi import ALBroker, ALProxy, ALModule
from time import sleep

ip = "192.168.1.143"
port = 9559

aup = ALProxy("ALAudioPlayer", ip ,port )


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
        self.startWit()
        print "starting.."
        aup.post.playFile("/usr/share/naoqi/wav/begin_reco.wav")

        self.ALAudioDevice.subscribe(self.getName())
        sleep(duration)
        self.ALAudioDevice.unsubscribe(self.getName())

        print "ended"
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




if __name__ == "__main__":
    pythonBroker = ALBroker("PythonBroker", "0.0.0.0", 9600, ip, port)
    # variable and string has to be a unique name
    # WittyNao = NaoWitSpeech("WittyNao")

    while True:

        WittyNao = NaoWitSpeech("WittyNao")
        WittyNao.startAudioTest(3)
        wit_response = WittyNao.reply
        resp = json.loads(wit_response)
        print resp
        print "--------------------"

        # break
        sleep(2)
