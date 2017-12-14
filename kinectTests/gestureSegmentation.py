import select, socket, time, json, math
import matplotlib.pyplot as plt

ip = "192.168.1.100"
port = 1337
BUFFER_SIZE = 2048

LHAND = 7
RHAND = 11
threshold = 0.015

plotHands = True


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
def recordGestures(lx, ly, rx, ry):
    """
    Record a gesture
    """

    msg = s.recv(4)
    nbytes = int(float(msg))
    skel = fullRead(nbytes)
    jskel = json.loads(skel)

    # append the next skeleton Frame
    lx.append(jskel[LHAND]["Position"]["X"])
    ly.append(jskel[LHAND]["Position"]["Y"])
    rx.append(jskel[RHAND]["Position"]["X"])
    ry.append(jskel[RHAND]["Position"]["Y"])
    detected = detectGestures(lx, ly, rx, ry)

    # This is a right-handed coordinate system that places a Kinect at the origin with the positive z-axis extending in the direction in which the Kinect is pointed. The positive y-axis extends upward, and the positive x-axis extends to the left. Placing a Kinect on a surface that is not level (or tilting the sensor) to optimize the sensor's field of view can generate skeletons that appear to lean instead of be standing upright.
    print '(x,y,z) for the left hand is: (', jskel[LHAND]["Position"]["X"], jskel[LHAND]["Position"]["Y"] , ')'

    return detected
    # except:
    #     print "Oops error"
    #
    #     return None


def detectGestures(lx, ly, rx, ry):
    """
    Detect which gesture is being performed
    """
    gesture = None
    global plotHands


    if len(lx) > 15 and plotHands:
            print "plot that shit"
            plotGesture(lx, ly, rx, ry)
            plotHands = False

    # record atleast 10 datapoints
    if len(lx) > 10:
        # if both the X and Y distance of L and R are
        # less than the threshold, the gesture has ended
        # e.g. check last and second to last gestures for
        # difference
        # 0.00142442 0.0010911506
        LXstop = abs(abs(lx[-1]) - abs(lx[-2])) < threshold
        LYstop = abs(abs(ly[-1]) - abs(ly[-2])) < threshold
        RXstop = abs(abs(rx[-1]) - abs(rx[-2])) < threshold
        RYstop = abs(abs(ry[-1]) - abs(ry[-2])) < threshold


        if LXstop and LYstop and RXstop and RYstop:
            gesture = "stop"
            print "stop"
        else:
            print "don't stop"

        return gesture


def plotGesture(lx, ly, rx, ry):
    # don't take all the data, but from 1/3 of the data up to 2/3
    # of the data

    # begin = int( math.floor( len(rx) / 3) )
    # end = int((2 * math.floor( len(rx) / 3)) )
    begin = 0
    end = int(len(rx)-1)

    # plot the detected gesture
    plt.plot( lx[begin:end] , ly[begin:end] , 'ro-' )
    plt.plot( lx[begin] , ly[begin] , 'bo' ,ms =10)
    plt.plot( lx[end] , ly[end] , 'o' ,ms=10 , c= 'black' )
    plt.plot( rx[begin:end] , ry[begin:end] , 'g+-' )
    plt.plot( rx[begin] , ry [begin] , 'bo' ,ms =10)
    plt.plot(rx[end], ry[end],'o',ms=10, c='black')
    plt.show()

if __name__ == "__main__":
    # in case of disconnects, do this in the main loop to
    # reconnect everytime

    print "Connecting to KinectServer at ", ip
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    print "Connected, now waiting for SkelFrames"

    timeout = 0.5 #s

    lx = []
    ly = []
    rx = []
    ry = []

    while True:
        ready_read, ready_write, serror = select.select([s], [], [], timeout)
        if ready_read:
            gesture = recordGestures(lx, ly, rx, ry)

            if gesture is not None:
                # print gesture
                time.sleep(timeout)
            else:
                time.sleep(timeout)

        else:
            #nothing to read and not receiving anything
            time.sleep(timeout)
