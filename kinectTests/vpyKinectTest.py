from visual import *
import vpykinect

vpykinect.draw_sensor(frame())
skeleton = vpykinect.Skeleton(frame(visible=False))
while True:
    rate(30)
    skeleton.frame.visible = skeleton.update()
