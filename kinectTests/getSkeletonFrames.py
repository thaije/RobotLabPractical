import socket, time, json

# receives nothing untill gesture data (i.e. standing in
# front of kinect) is generated
# Frames are sampled at 30hz

ip = "192.168.1.100"
port = 1337
BUFFER_SIZE = 2048

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


def decodeSkeletonData(skel):
    LHAND = 7
    RHAND = 11

    jskel = json.loads(skel)
    lx = jskel[LHAND]['Position']['X']
    ly = jskel[LHAND]['Position']['Y']
    lz = jskel[LHAND]['Position']['Z']
    rx = jskel[RHAND]['Position']['X']
    ry = jskel[RHAND]['Position']['Y']
    rz = jskel[RHAND]['Position']['Z']

    print '(x,y,z) for the left hand is: (', lx, ly, lz, ')'

# explenation of position points
# seen as from center of Kinect
#https://msdn.microsoft.com/en-us/library/hh973078.aspx

if __name__ == "__main__":
    print "connecting to KinectServer at: ", ip
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    print "connected, now waiting for SkelFrames"

    tstart = time.time()
    while True:
        msg = s.recv(4) # 4bytes = integer
        nbytes = int(float(msg))
        t = time.time()
        # skel = s.recv(nbytes)
        skel = fullRead(nbytes)
        print (1000 * (t - tstart)) # timestamp in milliseconds
        # print skel
        decodeSkeletonData(skel)
