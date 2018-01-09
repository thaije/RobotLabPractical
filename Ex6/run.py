import multiprocessing, Queue, signal, sys
from time import sleep
from naoqi import ALProxy
import camera

ip = "192.168.1.143"
port = 9559

# camera variables
resolution = 1
resolutionX = 320
resolutionY = 240
ballThreshold = 25
foundBall = False
videoProxy = False
cam = False

# proxies
postureProxy = ALProxy("ALRobotPosture", ip ,port )
motionProxy = ALProxy("ALMotion", ip ,port )
tts = ALProxy("ALTextToSpeech", ip , port )
memory = ALProxy("ALMemory", ip, port)
LED = ALProxy("ALLeds", ip, port)
# global aud
# aud = False
# aud = ALProxy("ALAudioDevice", ip ,port )
# aud.enableEnergyComputation()

# general variables
walkSpeed = 0.6

# declare global variables
movement = None
ballDetection = None
volumeLevel = None
exitProcess = False
audioVolume = False
ballLocation = False # -1=not found, 0=centered, 1=top, 2=right, 3=bottom, 4=left
movementQueue = False

################################################################################
# Ball searching and looking / sensing functions
################################################################################
def ballDetection(exitProcess, ballLocation):
    name = multiprocessing.current_process().name
    print name, " Starting"

    # video processing
    videoProxy, cam = camera.setupCamera(ip, port)

    while not exitProcess.value:
        # get and process a camera frame
        image = camera.getFrame(videoProxy, cam)
        if image is not False:
            # Check if we can find a ball, and publish the location if so
            ballDet = camera.findBall(image)
            onBallDetect(ballDet, ballLocation)
        else:
            ballLocation.value = -1

    print name, " Exiting"

def onBallDetect(ballDetection, ballLocation):
    if ballDetection is False:
        # announce we lost the ball
        if ballLocation.value > -1:
            ballLocation.value = -1
            tts.say("Lost ball")
    else:
        # Announce that we found the ball if we hadn't already
        print("Found ball at ", ballDetection[0],  ballDetection[1]), ". Publishing location"
        findBallLocation(ballDetection[0], ballDetection[1], ballLocation)


# Save in a variable where the ball is to center the ball (with a certain threshold)
def findBallLocation(x, y, ballLocation):
    if x > (resolutionX/2 + ballThreshold):
        ballLocation.value(2)
    elif x < (resolutionX/2 - ballThreshold):
        ballLocation.value(4)
    elif y > (resolutionY/2 + ballThreshold):
        ballLocation.value(3)
    elif y < (resolutionY/2 - ballThreshold):
        ballLocation.value(1)



################################################################################
# Movement thread
################################################################################
# Movement codes: head up = 1, head right = 2, head down = 3, head left = 4, look around = 5, wander = 6, stop = -1
def movement(exitProcess, movementQueue):
    name = multiprocessing.current_process().name
    print name, " Starting"

    time_out = 0.3
    walking = False
    lookingAround = False

    while not exitProcess.value:
        try:
            # get msg from queue.
            msg = movementQueue.get(True, time_out)
            # print "from movement queue received ", msg

            # -1 = stop order
            if msg == -1: #
                motionProxy.stopMove()
                walking = False
                postureProxy.goToPosture("StandInit", 0.6667)
            # 6 = wander around order
            elif msg == 6:
                if not walking:
                    walking = True
                    motionProxy.moveToward(walkSpeed, 0, 0)
            # look around order
            elif msg == 5:
                lookAround()
            elif msg == 1:
                look("up")
            elif msg == 2:
                look("right")
            elif msg == 3:
                look("down")
            elif msg == 4:
                look("left")

        # if time_out over, throw queue.empty exception
        except Queue.Empty:
            # if no msg has been added to the queue within time_out
            # seconds do this
            print name, " no movement order"
            sleep(0.2)
        except:
            print "Got other error in movement thread loop"

    print name, " Exiting"

# look a relative amount to the current head posture in a certain direction
def look(direction):
    speed = 0.5
    joints = ["HeadYaw", "HeadPitch"]
    isAbsolute = False
    times = [[0.1], [0.1]] #time in seconds

    # yaw = 0 # left (2) right (-2)
    # pitch = 0 # up(-0.6) down (0.5)
    if direction is "right":
        angles = [[-0.3], [0]]
    elif direction is "left":
        angles = [[0.3], [0]]
    elif direction is "up":
        angles = [[0], [-0.2]]
    elif direction is "down":
        angles = [[0], [0.2]]

    print "Looking ", direction
    motionProxy.angleInterpolation(joints, angles, times, isAbsolute)

# look left look right
def lookAround():
    print("looking around")
    speed = 0.5
    joints = ["HeadYaw", "HeadPitch"]
    angles = [[-1.0, 1.0, 0], [-0.2, 0]]
    times = [[1.5, 3.0, 5.0], [1.0, 5.0]] #time in seconds
    isAbsolute = True
    motionProxy.angleInterpolation(joints, angles, times, isAbsolute)
    return True

################################################################################
# Volume measurement thread
################################################################################
def volumeLevel(exitProcess, audioVolume):
    name = multiprocessing.current_process().name
    print name, " Starting"
    i = 0

    aud = ALProxy("ALAudioDevice", ip ,port )
    aud.enableEnergyComputation()

    while not exitProcess.value:
        audioLevels = [aud.getFrontMicEnergy(), aud.getRightMicEnergy(), aud.getRearMicEnergy(), aud.getLeftMicEnergy()]
        audioVolume.value = max(audioLevels)
        # audioVolume.value = 5000
        print "wr1 Audio level is: " , audioVolume.value
        sleep(0.5)

    print name, " Exiting"


################################################################################
# Communication functions
################################################################################
def changeLeds(intensity, color):
    if intensity > 10000:
        intensity = 1.0
    elif intensity < 1000:
        intensity = 0
    else:
        intensity = intensity / 10000.0

    print "Changing face leds to intensity ", intensity, " and color", color
    name = 'FaceLeds'
    red = intensity if color == "red" else 0.0
    blue = intensity if color == "blue" else 0.0
    green = intensity if color == "green" else 0.0
    duration = 0.2
    LED.fadeRGB(name, red, green, blue, duration)


################################################################################
# General functions
################################################################################
def setup():
    global volumeLevel, ballDetection, movement, exitProcess, audioVolume, ballLocation, movementQueue

    manager = multiprocessing.Manager()
    exitProcess = manager.Value('i', False)
    audioVolume = manager.Value('i', 0)
    ballLocation = manager.Value('i', -1)
    # movementQueue = multiprocessing.Queue()

    print "setting up threads"
    volumeLevel = multiprocessing.Process(name = "volume-measurement-proc", target=volumeLevel, args=(exitProcess, audioVolume,))
    # ballDetection = multiprocessing.Process(name = "ball-detection-proc", target=ballDetection, args=(exitProcess, ballLocation))
    # movement = multiprocessing.Process(name = "movement-proc", target=movement, args=(exitProcess, movementQueue))

def main():
    setup()

    global exitProcess, movementQueue, audioVolume, ballLocation


    try:
        # start other threads
        volumeLevel.start()
        # ballDetection.start()
        # movement.start()

        ballFound = False
        t=1
        while t < 10:

            # print "Volumelevel is:", audioVolume.value
            # changeLeds(audioVolume.value, "red")

            print "Volumelevel is:", audioVolume.value
            
            # give command to look around while the ball is not found
            if ballLocation == -1:
                # movementQueue.value = 5
                print "Volumelevel is:", audioVolume.value
                # changeLeds(volumeLevel, "red")
                if ballFound:
                    ballFound = False

            # if found give command to center head on ball
            if ballLocation > -1:
                # save in local variable and stop movement if ball was't found yet
                if not ballFound:
                    # motionProxy.stopMove()
                    # movementQueue.value = -1
                    ballFound = True

                # ball centerd, nothing to do
                if ballLocation == 0:
                    # changeLeds(audioVolume.value, "green")
                    pass

                # if not centered yet, center
                elif ballLocation > 0:
                    # movementQueue.value = ballLocation
                    # changeLeds(audioVolume.value, "blue")
                    pass

            sleep(0.2)
            t += 0.2

        exitProcess.value = True
        sleep(1)

    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
    except Exception, e:
        print "Unexpected error:", sys.exc_info()[0] , ": ", str(e)
    finally:
        print("Shutting down after sitting")
        exitProcess.value = True
        # postureProxy.goToPosture("Sit", 0.6667)
        motionProxy.rest()
        # clean up other threads
        volumeLevel.join()
        # ballDetection.join()
        # movement.join()
        print  "Is volMeasr alive?", volumeLevel.is_alive()
        # print "Is ballDet alive?", ballDetection.is_alive()
        # print "Is movement alive?", movement.is_alive()
        sys.exit(0)


if __name__ == "__main__":
    main()
