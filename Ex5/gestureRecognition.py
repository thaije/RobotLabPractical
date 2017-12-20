# Author        :   Tjalling Haije (s1011759)
# Date          :   19-12-2017
# Course        :   Robotlab Practical, Master AI, Radboud University
# Description   :   This file receives and records the skeleton data from the
#                   kinect, and checks for any recognized gestures
# How to run    :   Please run run.py instead

import select, socket, time, json, math
import matplotlib.pyplot as plt
from gestures import *

ip = "192.168.1.100"
port = 1337
BUFFER_SIZE = 2048

LHAND = 7
RHAND = 11
LELBOW = 5
RELBOW = 9
HEAD = 3
RSHOULDER = 8
LSHOULDER = 4

confidenceThresholdGest = 0.5
thresholdStillMoving = 0.025
plotHands = False
s = False

# read in full buffer
def fullRead(nbytes):
    chuncks = []
    bytes_read = 0

    while bytes_read < nbytes:
        chunck = s.recv(min(nbytes - bytes_read, BUFFER_SIZE))
        if chunck == ' ':
            raise RuntimeError("Socket connection to KinectServer broken")

        chuncks.append(chunck)
        bytes_read += len(chunck)
    # Read s.error to check for socket errors

    return ' '.join(chuncks)



# record gesture
def recordGestures(leftHand, rightHand, leftShoulder, rightShoulder, leftElbow, rightElbow, head):
    """
    Record a gesture
    """
    # try to connect to Kinect server, and skip in case of any connection errors
    try:
        msg = s.recv(4)
        nbytes = int(float(msg))
        skel = fullRead(nbytes)
        jskel = json.loads(skel)
    except:
        print "Error decoding json, skipping"
        return None
        pass

    # leftHand, rightHand, leftShoulder, rightShoulder, leftElbow, rightElbow, head
    # Append the joint data of the next skeleton frame to the corresponding list
    # lefthand
    leftHand[0].append(jskel[LHAND]["Position"]["X"])
    leftHand[1].append(jskel[LHAND]["Position"]["Y"])
    # righthand
    rightHand[0].append(jskel[RHAND]["Position"]["X"])
    rightHand[1].append(jskel[RHAND]["Position"]["Y"])
    # leftshoulder
    leftShoulder[0].append(jskel[LSHOULDER]["Position"]["X"])
    leftShoulder[1].append(jskel[LSHOULDER]["Position"]["Y"])
    # rightshoulder
    rightShoulder[0].append(jskel[RSHOULDER]["Position"]["X"])
    rightShoulder[1].append(jskel[RSHOULDER]["Position"]["Y"])
    # leftelbow
    leftElbow[0].append(jskel[LELBOW]["Position"]["X"])
    leftElbow[1].append(jskel[LELBOW]["Position"]["Y"])
    # rightelbow
    rightElbow[0].append(jskel[RELBOW]["Position"]["X"])
    rightElbow[1].append(jskel[RELBOW]["Position"]["Y"])
    # head
    head[0].append(jskel[LELBOW]["Position"]["X"])
    head[1].append(jskel[LELBOW]["Position"]["Y"])

    # check if any gestures detected
    detected = detectGestures(leftHand, rightHand, leftShoulder, rightShoulder, leftElbow, rightElbow, head)

    # print some handy skeleton joint coordinates
    print '---'
    print "LHand:", jskel[LHAND]["Position"]["X"], jskel[LHAND]["Position"]["Y"], " RHAND:", jskel[RHAND]["Position"]["X"], jskel[RHAND]["Position"]["Y"]
    print "Lelbow:", jskel[LELBOW]["Position"]["X"], jskel[LELBOW]["Position"]["Y"], " Relbow:", jskel[RELBOW]["Position"]["X"], jskel[RELBOW]["Position"]["Y"]
    print "Lshoulder:", jskel[LSHOULDER]["Position"]["X"], jskel[LSHOULDER]["Position"]["Y"], " Rshoulder:", jskel[RSHOULDER]["Position"]["X"], jskel[RSHOULDER]["Position"]["Y"]

    return detected


def detectGestures(leftHand, rightHand, leftShoulder, rightShoulder, leftElbow, rightElbow, head):
    """
    Detect which gesture is being performed
    """
    gesture = None
    global plotHands

    if len(leftHand[0]) > 10 and plotHands:
        print "plot"
        plotGesture(leftHand[0], leftHand[1], rightHand[0], rightHand[1])
        plotHands = False

    print "Datapoints:", len(leftHand[0])

    # record atleast 10 datapoints
    if len(leftHand[0]) > 10 or len(leftHand[0]) > 25:
        # Start checking for gestures when the user stops moving its hands
        # e.g. check last and second to last gestures for difference
        LXstop = abs(abs(leftHand[0][-1]) - abs(leftHand[0][-2])) < thresholdStillMoving
        LYstop = abs(abs(leftHand[1][-1]) - abs(leftHand[1][-2])) < thresholdStillMoving
        RXstop = abs(abs(rightHand[0][-1]) - abs(rightHand[0][-2])) < thresholdStillMoving
        RYstop = abs(abs(rightHand[1][-1]) - abs(rightHand[1][-2])) < thresholdStillMoving

        if LXstop and LYstop and RXstop and RYstop:
            print "Stopped, checking gestures"
            # call checkGestures from different file
            gesture = checkGestures(confidenceThresholdGest, leftHand, rightHand, leftShoulder, rightShoulder, leftElbow, rightElbow, head)
            print "stop"
        else:
            print "Hands still moving"

    return gesture


def plotGesture(lx, ly, rx, ry):
    # don't take all the data, but from 1/3 of the data up to 2/3
    # of the data
    # begin = int( math.floor( len(rx) / 3) )
    # end = int((2 * math.floor( len(rx) / 3)) )

    # take all data
    begin = 0
    end = int(len(rx)-1)

    # plot the hand joint coordinates
    plt.plot( lx[begin:end] , ly[begin:end] , 'ro-' )
    plt.plot( lx[begin] , ly[begin] , 'bo' ,ms =10)
    plt.plot( lx[end] , ly[end] , 'o' ,ms=10 , c= 'black' )
    plt.plot( rx[begin:end] , ry[begin:end] , 'g+-' )
    plt.plot( rx[begin] , ry [begin] , 'bo' ,ms =10)
    plt.plot( rx[end], ry[end],'o',ms=10, c='black')
    plt.show()


def recognizeGestures():
    global s

    # in case of disconnects, do this in the main loop to
    # reconnect everytime
    print "Connecting to KinectServer at ", ip
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    print "Connected, now waiting for SkelFrames"

    timeout = 0.5 #s

    # Syntax: Joint = [x, y]
    leftHand = [[], []]
    rightHand = [[], []]
    leftShoulder = [[], []]
    rightShoulder = [[], []]
    leftElbow = [[], []]
    rightElbow = [[], []]
    head = [[], []]
    # leftHand, rightHand, leftShoulder, rightShoulder, leftElbow, rightElbow, head

    while True:
        ready_read, ready_write, serror = select.select([s], [], [], timeout)
        if ready_read:
            gesture = recordGestures(leftHand, rightHand, leftShoulder, rightShoulder, leftElbow, rightElbow, head)

            if gesture is not None:
                return gesture
                break;
            else:
                time.sleep(timeout)
        else:
            #nothing to read and not receiving anything
            time.sleep(timeout)


# uncomment and run this file directly for testing
# if __name__ == "__main__":
#     from time import sleep
#     sleep(2)
#     response = recognizeGestures()
