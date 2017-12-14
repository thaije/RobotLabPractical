import json

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
