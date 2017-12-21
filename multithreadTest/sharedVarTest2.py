import multiprocessing, Queue, time, signal, sys

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

def writer1(queue, exitProcess):
    name = multiprocessing.current_process().name
    print name, " Starting"

    while not exitProcess.value:
        time.sleep(0.5)
        print "writer1 data:" , exitProcess.value

    print name, " Exiting"


def writer2(queue, exitProcess):
    name = multiprocessing.current_process().name
    print name, " Starting"

    while not exitProcess.value:
        time.sleep(0.5)
        print "writer2 data:" , exitProcess.value
    print name, " Exiting"


def setup():
    global q1, q2, writer1, writer2, reader, exitProcess

    manager = multiprocessing.Manager()
    exitProcess = manager.Value('i', False)

    print "Main val:", exitProcess.value

    print "setup"
    q1 = multiprocessing.Queue()
    writer1 = multiprocessing.Process(name = "writer1-proc", target=writer1, args=(q1,exitProcess))
    writer2 = multiprocessing.Process(name = "writer2-proc", target=writer2, args=(q1,exitProcess))


def exit():
    global exitProcess
    exitProcess.value = True

def main():
    setup()

    global exitProcess

    try:
        writer1.start()
        writer2.start()
        t=1
        while t < 4:
            time.sleep(1)
            print "sleeping " , exitProcess.value
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
        writer1.join()
        writer2.join()
        print  "Is wr1 alive?", writer1.is_alive()
        print "Is wr2 alive?", writer2.is_alive()
        # pythonBroker.shutdown()
        sys.exit(0)



if __name__ == "__main__":
    main()
