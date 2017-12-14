import json

#https://msdn.microsoft.com/en-us/library/hh973078.aspx

skel = [{"Position":{"X":0.0263176821,"Y":-0.293897241,"Z":1.47734642},"JointType":0,"TrackingState":2},{"Position":{"X":0.0258045644,"Y":-0.245612919,"Z":1.54023755},"JointType":1,"TrackingState":2},{"Position":{"X":0.0342774838,"Y":0.086984545,"Z":1.5889349},"JointType":2,"TrackingState":2},{"Position":{"X":0.040720515,"Y":0.297637522,"Z":1.61813128},"JointType":3,"TrackingState":2},{"Position":{"X":-0.124490023,"Y":-0.0506821126,"Z":1.54561412},"JointType":4,"TrackingState":2},{"Position":{"X":-0.2171076,"Y":-0.296775579,"Z":1.48629},"JointType":5,"TrackingState":2},{"Position":{"X":-0.2592508,"Y":-0.4874916,"Z":1.37116218},"JointType":6,"TrackingState":2},{"Position":{"X":-0.253850818,"Y":-0.50473,"Z":1.358071},"JointType":7,"TrackingState":2},{"Position":{"X":0.195302278,"Y":-0.0622153133,"Z":1.56900489},"JointType":8,"TrackingState":2},{"Position":{"X":0.2594749,"Y":-0.315852523,"Z":1.53005981},"JointType":9,"TrackingState":2},{"Position":{"X":0.2963324,"Y":-0.526519656,"Z":1.4634763},"JointType":10,"TrackingState":2},{"Position":{"X":0.2999261,"Y":-0.5446723,"Z":1.44429362},"JointType":11,"TrackingState":2},{"Position":{"X":-0.0469788536,"Y":-0.355066,"Z":1.44653487},"JointType":12,"TrackingState":2},{"Position":{"X":0.209694088,"Y":-0.6469022,"Z":1.2796104},"JointType":13,"TrackingState":1},{"Position":{"X":0.400512159,"Y":-0.8638616,"Z":1.14005673},"JointType":14,"TrackingState":1},{"Position":{"X":0.427664876,"Y":-0.8628219,"Z":1.05179381},"JointType":15,"TrackingState":1},{"Position":{"X":0.09594117,"Y":-0.367337137,"Z":1.46276116},"JointType":16,"TrackingState":2},{"Position":{"X":0.4081967,"Y":-0.6288127,"Z":1.54479373},"JointType":17,"TrackingState":1},{"Position":{"X":0.6403364,"Y":-0.82320106,"Z":1.5903219},"JointType":18,"TrackingState":1},{"Position":{"X":0.698987067,"Y":-0.8385953,"Z":1.52066708},"JointType":19,"TrackingState":1}]

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
