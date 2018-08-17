# USAGE
# python ball_tracking.py --video ball_tracking_example.mp4
# python ball_tracking.py

# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2

import time
import rtmidi

#################################################################################
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
        help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
        help="max buffer size")
args = vars(ap.parse_args())

#################################################################################

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()

if available_ports:
        midiout.open_port(1)

snareDrumOn = [0x90, 38, 125]
snareDrumOff = [0x90, 38, 0]
kickOn = [0x90, 36, 125]
kickOff = [0x90, 36, 0]
hihatClosedOn = [0x90, 53, 125]
hihatClosedOff = [0x90, 53, 0]
crashOn = [0x90, 77, 125]
crashOff = [0x90, 77, 0]
hihatOpenedOn = [0x90, 56, 125]
hihatOpenedOff = [0x90, 56, 0]

kickx = [i for i in range(100, 261)]
kicky = [j for j in range(420, 461)]

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
pts = deque(maxlen=args["buffer"])

redLower = (136, 87, 111)
redUpper = (180, 255, 255)
ptsr = deque(maxlen=args["buffer"])

blueLower = (14,233,154)     #NOT REALLY BLUE, orange xD
blueUpper = (24,253,234)
ptsb = deque(maxlen=args["buffer"])

# Grab the reference to the webcam
camera = cv2.VideoCapture(0)

flag = 0
flag2 = 0
# keep looping
while True:
        # grab the current frame
        (grabbed, frame) = camera.read()
        frame = cv2.flip(frame,1)

        # if we are viewing a video and we did not grab a frame,
        # then we have reached the end of the video
        if args.get("video") and not grabbed:
                break

        # resize the frame, blur it, and convert it to the HSV
        # color space
        frame = imutils.resize(frame, width=600)
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # construct a mask for the color "green", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, greenLower, greenUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        maskr = cv2.inRange(hsv, redLower, redUpper)
        maskr = cv2.erode(maskr, None, iterations = 2)
        maskr = cv2.dilate(maskr, None, iterations = 2)

        maskb = cv2.inRange(hsv, blueLower, blueUpper)
        maskb = cv2.erode(maskb, None, iterations = 2)
        maskb = cv2.dilate(maskb, None, iterations = 2)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None

        cntsr = cv2.findContours(maskr.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        centerr = None

        cntsb = cv2.findContours(maskb.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        centerb = None

        # only proceed if at least one contour was found
        if len(cnts) > 0:
                # find the largest contour in the mask, then use
                # it to compute the minimum enclosing circle and
                # centroid
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                ab = int(M["m10"] / M["m00"])
                de = int(M["m01"] / M["m00"])
                center = (ab, de)

                # only proceed if the radius meets a minimum size
                if radius > 10:
                        # draw the circle and centroid on the frame,
                        # then update the list of tracked points
                        cv2.circle(frame, (int(x), int(y)), int(radius),
                                (0, 255, 255), 2)
                        cv2.circle(frame, center, 5, (0, 0, 255), -1)


                #font=cv2.FONT_HERSHEY_SIMPLEX
                #cv2.putText(frame, center[0], (10,20), font, 0.55, (0,255,0), 1)
                print(center)

                if(flag == 1):
                        flag = 0
                        flag2 = 1

                if ab in kickx and flag == 0 and flag2 == 0:
                        if de in kicky:
                                midiout.send_message(kickOn)
                                midiout.send_message(kickOff)
                                flag = 1

                if(ab > 510 and de > 370 and flag == 0 and flag2 == 0):
                        midiout.send_message(snareDrumOn)
                        midiout.send_message(snareDrumOff)
                        flag = 1

                if(ab < 60 and y > 370 and flag == 0 and flag2 == 0):
                        midiout.send_message(crashOn)
                        midiout.send_message(crashOff)
                        flag = 1
                        
                if(flag2 == 1):
                        flag2 = 0
                # only proceed if at least one contour was found

        if len(cntsb) > 0:
                # find the largest contour in the mask, then use
                # it to compute the minimum enclosing circle and
                # centroid
                c1 = max(cntsb, key=cv2.contourArea)
                ((x1, y1), radius1) = cv2.minEnclosingCircle(c1)
                M1 = cv2.moments(c1)
                ab1 = int(M1["m10"] / M1["m00"])
                de1 = int(M1["m01"] / M1["m00"])
                center1 = (ab1, de1)

                # only proceed if the radius meets a minimum size
                if radius1 > 10:
                        # draw the circle and centroid on the frame,
                        # then update the list of tracked points
                        cv2.circle(frame, (int(x1), int(y1)), int(radius1),
                                (0, 255, 255), 2)
                        cv2.circle(frame, center1, 5, (0, 0, 255), -1)


                #font=cv2.FONT_HERSHEY_SIMPLEX
                #cv2.putText(frame, center[0], (10,20), font, 0.55, (0,255,0), 1)
                print(center)

                if(flag == 1):
                        flag = 0
                        flag2 = 1

                if(ab1 > 510 and de1 > 370 and flag == 0 and flag2 == 0):
                        midiout.send_message(snareDrumOn)
                        midiout.send_message(snareDrumOff)
                        flag = 1

                if(ab1 < 60 and y1 > 370 and flag == 0 and flag2 == 0):
                        midiout.send_message(crashOn)
                        midiout.send_message(crashOff)
                        flag = 1
                        
                if(flag2 == 1):
                        flag2 = 0

                # only proceed if at least one contour was found

                
        # update the points queue
        pts.appendleft(center)

        # loop over the set of tracked points
        for i in range(1, len(pts)):
                # if either of the tracked points are None, ignore them
                if pts[i - 1] is None or pts[i] is None:
                        continue

                # otherwise, compute the thickness of the line and
                # draw the connecting lines
                thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
                cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

        #kickBOX
        #cv2.rectangle(frame, (100,420), (260,460), (0,0,0), 3)
        

        # show the frame to our screen
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
                break

# cleanup the camera and close any open windows
del midiout
camera.release()
cv2.destroyAllWindows()
