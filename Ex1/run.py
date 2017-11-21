import time
from random import *
import naoqi

ip = "192.168.1.138"
port = 9559
duration = 100

# list of behaviours and postures
behaviours = shuffle(["pointAndWalk", "robotDance", "wave", "break", "randomPosture", "randomPosture", "lookAround"])
postures = shuffle(["sit", "Crouch"])

# random behaviours:
# - Mime: oh no a wall, just kidding


def doBehaviour(behaviour):
    global postures
    [postureProxy, motionProxy, tts] = proxies

    if behaviour is "pointAndWalk":
        rightJoints = [ "RShoulderPitch", "RHand"]
        angles = [ 0.0, 1]
        times = [ 1.0, 1.0]
        isAbsolute = True
        motionProxy.setStiffnesses(leftJoints, 0.8 )
        motionProxy.angleInterpolation(leftJoints, angles, times, isAbsolute)
        tts.say ("That looks interesting, let's go there")
        time.sleep(2.0)
        tts.say ("Or maybe not")

    if behaviour is "robotDance":
        tts.say ("How you look my robot dance")
        joints = [ "LShoulderRoll", "LElbowRoll"]
        angles = [ 1.3, [-1.5, -1.25, -1.5, -1.25]]
        times = [ 1.0, [-1.5, 2.0, 3.0, 4.0]]
        isAbsolute = True
        motionProxy.setStiffnesses(leftJoints, 0.8 )
        motionProxy.angleInterpolation(leftJoints, angles, times, isAbsolute)


    if behaviour is "wave":
        rightJoints = [ "RShoulderPitch", "LShoulderRoll"]
        angles = [ 1.57, [-0.3, 0.3, -0.3, 0.3]]
        times = [ 1.0, [2.0, 2.5, 3.0, 3.5]]
        isAbsolute = True
        motionProxy.setStiffnesses(leftJoints, 0.8 )
        motionProxy.angleInterpolation(leftJoints, angles, times, isAbsolute)
        tts.say ("Hello")


    if behaviour is "break":
        tts.say ("Time for a break")
        motionProxy.rest()
        tts.say ("Okay let's continue")
        # joints = ["Head"]
        # motionProxy.setStiffnesses(joints, 0.8)

    if behaviour is "randomPosture":
        tts.say ("Time for a random posture")
        # do the first posture from the list and remove it afterwards
        postureProxy.goToPosture(postures[0] ,0.6667)
        del postures[0]

    if behaviour is "lookAround":
        # move left, right and go back to center
        speed = 0.5
        joints = "HeadYaw"
        angles = [-2.0, 2.0, 0]
        times = [1.0, 2.0, 4.0]
        isAbsolute = True
        motionProxy.setStiffnesses("Head", 0.8)
        motionProxy.angleInterpolation(joints, angles, times, isAbsolute)
        tts.say ("Interesting")



def main():
    postureProxy = naoqi.ALProxy("ALRobotPosture", ip ,port )
    motionProxy = naoqi.ALProxy("ALMotion", ip ,port )
    tts = naoqi.ALProxy("ALTextToSpeech", ip , port )
    proxies = [postureProxy, motionProxy, tts]

    # define the list so we can edit them
    global behaviours

    # start timer
    start = time.time()
    end = time.time()

    # continue with the presentation for 100 seconds
    while end - start < duration:

        # Make sure to stand
        postureProxy.goToPosture("Standing", 0.6667)

        # walk in random direction for a random duration
        X = random() * 2 -1
        Y = random() * 2 -1
        Theta = random() * 2 -1
        MotionProxy.moveToward(X, Y, Theta)

        # sleep and stop
        time.sleep(randint(2, 7))
        motionProxy.stopMove()

        # do a random behaviour, and delete it from the list
        doBehaviour(behaviours[0], proxies)
        del behaviours[0]

        # update time
        end = time.time()

    tts.say("This was my demonstration")




if __name__ == "__main__":
    main()
