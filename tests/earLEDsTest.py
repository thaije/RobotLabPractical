import sys
from naoqi import ALProxy
ip = "192.168.1.102"
port = 9559

try:
    proxy = ALProxy("ALLeds", ip, port)
except Exception, e:
    print "Could not create proxy to ALLeds"
    print "Error was: ", # -*- coding: utf-8 -*-
    sys.exit(1)

name = 'EarLeds'
red = 1.0
green = 0.0
blue = 0.0
duration = 0.5
proxy.fadeRGB(name, red, green, blue, duration)
