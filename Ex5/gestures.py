import operator


def checkGestures(confidenceThresholdGest, leftHand, rightHand, leftShoulder, rightShoulder, leftElbow, rightElbow, head):
    # check gestures
    haltConf = halt(leftHand, rightHand, leftShoulder, rightShoulder, leftElbow, rightElbow, head)
    mapCheckConf = mapCheck(leftHand, rightHand, leftShoulder, rightShoulder, leftElbow, rightElbow, head)
    dtConf = doubleTime(leftHand, rightHand, leftShoulder, rightShoulder, leftElbow, rightElbow, head)

    # make a dictionary of the gestures with their confidence, and get the most likely gesture
    gestures = {'Halt': haltConf, 'MapCheck': mapCheckConf, 'DoubleTime': dtConf}
    highestProbableGest = max(gestures.iteritems(), key=operator.itemgetter(1))[0]

    print "Gestures:"
    print gestures
    print "highestProbableGest:", highestProbableGest, " value:", gestures.get(highestProbableGest)

    # if the gesture has a confidence higher than our threshold, return it
    if gestures.get(highestProbableGest) > confidenceThresholdGest:
        return highestProbableGest

    return "notrecognized"


# check for the halt gesture
def halt(leftHand, rightHand, leftShoulder, rightShoulder, leftElbow, rightElbow, head):
    yThreshold = 0.06
    xThreshold = 0.09
    confidence = 0

    print "Check halt gesture"

    # loop through the framesp
    for i in range(1, len(leftHand[0])):
        constrain1 = abs(leftElbow[1][i] - leftShoulder[1][i]) # left elbow X ~ left shoulder X
        constrain2 = abs(leftHand[0][i] - leftElbow[0][i]) # left hand Y ~ left elbow Y
        print "--> Frame %d, Elb / Sh aligned %.3f , Hand / elbow aligned %.3f" % (i, constrain1, constrain2)

        # check if satisfies the constrains
        if constrain1 < yThreshold and constrain2 < xThreshold:
            confidence = confidence + 1
            print "----> Confidence +1"

    print "--> Confidence:", confidence , " frames ", len(leftHand[0]), " conf2 ", float(confidence) / len(leftHand[0])

    return float(confidence) / len(leftHand[0])


# check for the mapcheck gesture
def mapCheck(leftHand, rightHand, leftShoulder, rightShoulder, leftElbow, rightElbow, head):
    confidence = 0
    xThreshold = 0.08
    yThreshold = 0.20


    print "Checking mapcheck gesture"

    for i in range(1, len(leftHand[0])):
        constrain1 = leftHand[0][i] > leftElbow[0][i] # leftHandX > leftElbowX
        constrain2 = abs(leftHand[0][i] - rightHand[0][i]) # leftHandX ~ rightHandX
        constrain3 = abs(leftHand[1][i] - rightHand[1][i]) # leftHandY ~ rightHandY
        # constrain4 = rightHand[0][i] > rightElbow[0][i] # rightHandX > rightElbow
        constrain4 = True

        print "--> Frame ", i , " Constrains:", constrain1, constrain2, constrain3, constrain4

        if constrain1 and constrain2 < yThreshold and constrain3 < yThreshold and constrain4:
            confidence += 1
            print "----> Confidence +1"

    print "--> confidence:", confidence , " frames ", len(leftHand[0]), " conf2 ", float(confidence) / len(leftHand[0])

    return float(confidence) / len(leftHand[0])


# double time gesture
def doubleTime(leftHand, rightHand, leftShoulder, rightShoulder, leftElbow, rightElbow, head):
    confidence = 0
    xThreshold = 0.12

    neededRepetitions = 3
    previousMovement = False
    repetitions = 0

    print "Checking doubletime gesture"

    for i in range(1, len(leftHand[0])):
        constrain1 = leftHand[1][i] > leftElbow[1][i] # leftHandY > leftHandElbow
        constrain2 = abs(leftHand[0][i] - leftElbow[0][i]) < xThreshold # leftHandX ~ leftElbowX
        constrain3a = leftElbow[1][i] > leftShoulder[1][i] # leftElbowY > leftShoulderY
        constrain3b = leftElbow[1][i] < leftShoulder[1][i] # leftElbowY < leftShoulderY
        print "--> Frame ", i , " Constrains:", constrain1, constrain2, constrain3a, constrain3b

        # check our two default constrains
        if not constrain1 or not constrain2:
            continue

        # check the motion
        if (not previousMovement and constrain3a) or (previousMovement == "down" and constrain3a):
            previousMovement = "up"
            print "----> Up"
        elif (not previousMovement and constrain3b) or (previousMovement == "up" and constrain3b):
            previousMovement = "down"
            repetitions += 1
            print "----> Down. Repetitions +1"

    # calc confidence
    if repetitions > neededRepetitions:
        confidence = 1.0
    else:
        confidence = float(repetitions) / neededRepetitions

    print "--> Repetitions:", repetitions , " frames ", len(leftHand[0]), " conf2 ", confidence

    return confidence
