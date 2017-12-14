import select, socket, time

ip = "192.168.1.100"
port = 1337

if __name__ == "__main__":
    # in case of disconnects, do this in the main loop to
    # reconnect everytime

    print "Connecting to KinectServer at ", self.ip
    s = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
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
                print gesture
                time.sleep(timeout)
            else:
                time.sleep(timeout)

        else:
            #nothing to read and not receiving anything
            time.sleep(timeout)

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
    nbytes = int(msg)
    skel = fullRead(nbytes)
    jskel = json.loads(skel)

    # append the next skeleton Frame
    lx.append(skel[LHAND]["Position"]["X"])
    ly.append(skel[LHAND]["Position"]["Y"])
    rx.append(skel[RHAND]["Position"]["X"])
    ry.append(skel[RHAND]["Position"]["Y"])
    detected = detectGestures(lx, ly, rx, ry)
    return detected


def detectGestures(lx, ly, rx, ry):
    """
    Detect which gesture is being performed
    """
    gesture = None
    # record atleast 10 datapoints
    if len(lx) > 10:
        # if both the X and Y distance of L and R are
        # less than the threshold, the gesture has ended

        # e.g. check last and second to last gestures for
        # difference
        LXstop =
        LYstop =
        RXstop =
        RYstop =

        if LXstop and LYstop and RXstop and RYstop:
            gesture = "stop"

        return gesture
