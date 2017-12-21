import multiprocessing, Queue, time, signal, sys
from naoqi import ALProxy

ip = "192.168.1.102"
port = 9559

# proxies

# if ball found:
#     stop movement
#     center on ball
#
# while not ball:
#     look around

# check volume level
# check camera for ball and send ballTrue / location
# move head if no ball, center on ball if ball

q1 = None
q2 = None
writer1 = None
writer2 = None
reader = None
exitProcess = False
audioVolume = False

################################################################################
# Volume measurement
################################################################################
def volumeLevel(queue, exitProcess, audioVolume):
    aud = ALProxy("ALAudioDevice", ip ,port )
    aud.enableEnergyComputation()

    name = multiprocessing.current_process().name
    print name, " Starting"
    i = 0

    while not exitProcess.value:
        audioLevels = [aud.getFrontMicEnergy(), aud.getRightMicEnergy(), aud.getRearMicEnergy(), aud.getLeftMicEnergy()]
        audioVolume.value = max(audioLevels)
        print "wr1 Audio level is: " , audioVolume.value
        time.sleep(0.5)

    print name, " Exiting"


################################################################################
# Ball tracking
################################################################################
def writer2(queue, exitProcess):
    name = multiprocessing.current_process().name
    print name, " Starting"

    while not exitProcess.value:
        time.sleep(0.5)
        # print "writer2 data:" , exitProcess.value
    print name, " Exiting"


################################################################################
# Communication functions
################################################################################
def changeEarLeds(intensity):
    name = 'EarLeds'
    red = 0.0
    green = 0.0
    blue = intensity
    duration = 0.5
    LED.fadeRGB(name, red, green, blue, duration)


################################################################################
# General functions
################################################################################
def setup():
    global q1, q2, volumeLevel, writer2, reader, exitProcess, audioVolume

    manager = multiprocessing.Manager()
    exitProcess = manager.Value('i', False)
    audioVolume = manager.Value('i', 0)

    print "Main val:", exitProcess.value

    print "setup"
    q1 = multiprocessing.Queue()
    volumeLevel = multiprocessing.Process(name = "writer1-proc", target=volumeLevel, args=(q1,exitProcess, audioVolume))
    writer2 = multiprocessing.Process(name = "writer2-proc", target=writer2, args=(q1,exitProcess))


def main():
    setup()

    global exitProcess

    try:
        volumeLevel.start()
        writer2.start()
        t=1
        while t < 10:
            # print "Volume level: ", audioVolume.value
            time.sleep(1)
            t += 1

        exitProcess.value = True
        time.sleep(1)

    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
    except Exception, e:
        print "Unexpected error:", sys.exc_info()[0] , ": ", str(e)
    finally:
        print("Shutting down after sitting")
        exitProcess.value = True
        time.sleep(0.5)
        volumeLevel.join()
        writer2.join()
        print  "Is wr1 alive?", volumeLevel.is_alive()
        print "Is wr2 alive?", writer2.is_alive()
        sys.exit(0)


if __name__ == "__main__":
    main()
