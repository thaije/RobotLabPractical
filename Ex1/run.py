# Author        :   Tjalling Haije (s1011759)
# Date          :   21-11-2017
# Course        :   Robotlab Practical, Master AI, Radboud University
# Description   :   This file makes a NAO robot randomly walk around, 
#                   do a number of actions in random order, and say a number
#                   of sentences in a random order.

# How to run:
# - connect to the robotlab wifi
# - correct the IP address below
# - python run.py


import time
import random
import naoqi

ip = "192.168.1.143"
port = 9559
duration = 105

# list of behaviours, postures and sentences
behaviours = ["pointAndWalk", "robotDance", "wave", "randomPosture", "randomPosture", "lookAround", "squats"]
postures = ["Stand", "Crouch"]
random.shuffle(postures)
sentences = ["Walking, walking", "When can I have a break?", "My joints are feeling a little stiff today", "Why is my camera disabled?", "Come to daddy", "Walking, walking"]

# Ideas for extra behaviours:
# - Mime: oh no a wall, just kidding


# Execute a behaviour
def doBehaviour(behaviour, proxies):
    # global postures

    [postureProxy, motionProxy, tts] = proxies

    if behaviour is "pointAndWalk":
        joints = [ "RShoulderPitch", "RHand"]
        angles = [ 0.0, 1]
        times = [ 1.0, 1.0]
        isAbsolute = True
        motionProxy.setStiffnesses(joints, 0.8 )
        motionProxy.angleInterpolation(joints, angles, times, isAbsolute)
        tts.say ("That looks interesting, let's go there")
        time.sleep(1.0)
        tts.say ("Or maybe not")


    if behaviour is "robotDance":
        tts.say ("How you like my new move. I call it. The Robot.")
        # raise arm
        joints = [ "LShoulderPitch", "LShoulderRoll"]
        angles = [ 2.08, 1.3]
        times = [ 1.0, 1.0]
        isAbsolute = True
        motionProxy.setStiffnesses(joints, 0.8 )
        motionProxy.angleInterpolation(joints, angles, times, isAbsolute)

        # set elbow at righ anle
        joints = ["LElbowRoll"]
        angles = [ -1.4]
        times = [ 1.0]
        isAbsolute = True
        motionProxy.setStiffnesses(joints, 0.8 )
        motionProxy.angleInterpolation(joints, angles, times, isAbsolute)

        # turn head
        speed = 0.5
        joints = ["HeadYaw", "HeadPitch"]
        angles = [1.5, 0.4]
        times = [1.0, 1.0]
        isAbsolute = True
        motionProxy.setStiffnesses("Head", 0.8)
        motionProxy.angleInterpolation(joints, angles, times, isAbsolute)

        # move elbow
        joints = ["LElbowRoll"]
        angles = [ [-1.5, -1.15, -1.54, -1.15, -1.54]]
        times = [ [1.5, 2.0, 2.5, 3.0, 3.5]]
        isAbsolute = True
        motionProxy.setStiffnesses(joints, 0.8 )
        motionProxy.angleInterpolation(joints, angles, times, isAbsolute)


    if behaviour is "wave":
        # raise arm
        joints = [ "RShoulderRoll" , "RShoulderPitch" , "RElbowYaw" ,
        "RElbowRoll" , "RWristYaw",  "RHand" ]
        angles = [ -0.15 , -1.0 , -0.3 , -0.5 , -0.1, 1.0]
        times = [ 1.0, 1.0 , 1.0 , 1.0 , 1.0 , 1.0]
        isAbsolute = True
        motionProxy.setStiffnesses(joints, 0.8 )
        motionProxy.angleInterpolation(joints, angles, times, isAbsolute)

        tts.say ("Hello")
        # wave
        joints = [ "RShoulderRoll" ]
        angles = [ -0.3 , 0.2, -0.3, 0.2]
        times = [ 1.0 , 1.5, 2.0, 2.5]
        isAbsolute = True
        motionProxy.setStiffnesses(joints, 0.8 )
        motionProxy.angleInterpolation(joints, angles, times, isAbsolute)


    if behaviour is "break":
        tts.say ("Time for a break")
        postureProxy.goToPosture("Sit" ,0.6667)
        time.sleep(1.0)
        tts.say ("Okay let's continue")


    if behaviour is "squats":
        tts.say ("Let's do some squats")
        postureProxy.goToPosture("Crouch" ,0.6667)
        postureProxy.goToPosture("StandZero" ,0.6667)
        postureProxy.goToPosture("Crouch" ,0.6667)
        postureProxy.goToPosture("StandZero" ,0.6667)
        tts.say ("Never skip leg day")
        postureProxy.goToPosture("Crouch" ,0.6667)
        postureProxy.goToPosture("StandZero" ,0.6667)


    if behaviour is "randomPosture":
        tts.say ("Time for a random posture")

        # do the first posture from the list and remove it afterwards
        print("Doing posture %s" % postures[0])
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

# Generate a shuffled list of all behaviours
def getBehaviourList():
    # define the list so we can edit them
    localbehaviours = behaviours
    random.shuffle(localbehaviours)
    return localbehaviours

def main():
    # set proxies
    postureProxy = naoqi.ALProxy("ALRobotPosture", ip ,port )
    motionProxy = naoqi.ALProxy("ALMotion", ip ,port )
    tts = naoqi.ALProxy("ALTextToSpeech", ip , port )
    proxies = [postureProxy, motionProxy, tts]

    # define the list so we can edit them
    localbehaviours = getBehaviourList()

    # start timer
    start = time.time()
    end = time.time()


    postureProxy.goToPosture("Stand" ,0.6667)

    # continue with the presentation untill the maximum length has been reached
    while end - start < duration:

        # reset the list if it is empty and all behaviours have been done
        if len(localbehaviours) is 0:
            localbehaviours = getBehaviourList()

        # generate a random duration for the walk (3-7 seconds)
        walkDuration = random.randint(3, 7)

        # Make sure to stand
        postureProxy.goToPosture("StandInit", 0.6667)

        # walk in random direction for a random duration
        X = random.random() * 2 -1
        Y = random.random() * 2 -1
        Theta = random.random() * 2 -1
        motionProxy.moveToward(X, Y, Theta)

        print ("walk for %d seconds" % walkDuration)

        # Say a random sentence during the walk and sleep for the duration of the
        # walk
        time.sleep(walkDuration * 0.5)
        randomS = random.randint(0, len(sentences) - 1)
        tts.say (sentences[randomS])
        print (sentences[randomS])
        time.sleep(walkDuration * 0.5)

        # stop walking
        motionProxy.stopMove()

        # do a random behaviour, and delete it from the list
        postureProxy.goToPosture("StandInit", 0.6667)
        print("Do behaviour %s" % localbehaviours[0])
        doBehaviour(behaviours[0], proxies)
        del localbehaviours[0]
        print(localbehaviours)
        print("\n")

        # update time
        end = time.time()

    tts.say("This was my demonstration")

    postureProxy.goToPosture("StandInit" ,0.6667)
    motionProxy.rest()



if __name__ == "__main__":
    main()
