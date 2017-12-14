import socket, time

# receives nothing untill gesture data (i.e. standing in
# front of kinect) is generated
# Frames are sampled at 30hz

ip = "192.168.1.100"
port = 1337

print "connecting to KinectServer at: ", ip
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ip, port))
print "connected, now waiting for SkelFrames"

tstart = time.time()
while True:
    msg = s.recv(4) # 4bytes = integer
    nbytes = int(msg)
    t = time.time()
    skel = s.recv(nbytes)
    # skel = fullRead(2048)
    print 1000 * (t - tstart) # time in milliseconds
    print skel

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
