import time
import sys

from naoqi import ALModule
from naoqi import ALProxy
from naoqi import ALBroker

ip = "192.168.1.143" #John
port = 9559

memory = ALProxy("ALMemory", ip, port)
sonar = ALProxy("ALSonar", ip, port)

sonare.subscribe("myS")
print memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")
print memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")
sonar.unsubscribe("myS")
