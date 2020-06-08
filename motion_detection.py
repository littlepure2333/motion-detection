# imports
import os,sys,time
import numpy as np
import cv2

# init camera
camera = cv2.VideoCapture("example.mp4") ### <<<=== SET THE CORRECT CAMERA NUMBER
camera.set(3,1280)             # set frame width
camera.set(4,720)              # set frame height
time.sleep(0.5)
print(camera.get(3),camera.get(4))

# master frame
master = None

# save video
fourcc = cv2.VideoWriter_fourcc(*'MP4V')  # 保存视频的编码
out = cv2.VideoWriter('output1.mp4',fourcc, 30.0, (640,720))

while True:

    # grab a frame
    (grabbed,frame0) = camera.read()
    
    # end of feed
    if not grabbed:
        break

    # gray frame
    frame1 = cv2.cvtColor(frame0,cv2.COLOR_BGR2GRAY)

    # blur frame
    kernel_gaussian = (5,5)
    frame2 = cv2.GaussianBlur(frame1,kernel_gaussian,0)
    frame2 = frame1.copy()

    # initialize master
    if master is None:
        master = frame2
        continue

    # delta frame
    frame3 = cv2.absdiff(master,frame2)

    # threshold frame: binaryzation
    frame4 = cv2.threshold(frame3,10,255,cv2.THRESH_BINARY)[1]

    # dilate the thresholded image to fill in holes
    kernel = np.ones((2,2),np.uint8)
    frame5 = cv2.erode(frame4,kernel,iterations=1)
    frame5 = cv2.dilate(frame5,kernel,iterations=3)

    # find contours on thresholded image
    contours,hierarchy = cv2.findContours(frame5.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    # make coutour frame
    frame6 = frame0.copy()

    # target contours
    targets = []

    # loop over the contours
    for c in contours:
        
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < 500:
                continue

        # contour data
        M = cv2.moments(c)#;print( M )
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        x,y,w,h = cv2.boundingRect(c)
        rx = x+int(w/2)
        ry = y+int(h/2)
        ca = cv2.contourArea(c)

        # plot contours
        cv2.drawContours(frame6,[c],0,(0,0,255),2)
        cv2.rectangle(frame6,(x,y),(x+w,y+h),(0,255,0),2)
        cv2.circle(frame6,(cx,cy),2,(0,0,255),2)
        cv2.circle(frame6,(rx,ry),2,(0,255,0),2)

        # save target contours
        targets.append((cx,cy,ca))

    # make target
    mx = 0
    my = 0
    if targets:
        
        # average centroid adjusted for contour size
        #area = 0
        #for x,y,a in targets:
        #    mx += x*a
        #    my += y*a
        #    area += a
        #mx = int(round(mx/area,0))
        #my = int(round(my/area,0))

        # centroid of largest contour
        area = 0
        for x,y,a in targets:
            if a > area:
                mx = x
                my = y
                area = a
        

    # plot target
    tr = 50
    frame7 = frame0.copy()
    if targets:
        cv2.circle(frame7,(mx,my),tr,(0,0,255,0),2)
        cv2.line(frame7,(mx-tr,my),(mx+tr,my),(0,0,255,0),2)
        cv2.line(frame7,(mx,my-tr),(mx,my+tr),(0,0,255,0),2)
    
    # update master
    master = frame2

    # display
    width =640
    length = 360
    position_x = 400
    position_y = 50

    # cv2.namedWindow("Frame0: Raw",0)
    # cv2.resizeWindow("Frame0: Raw", width, length)
    # cv2.moveWindow("Frame0: Raw", position_x, position_y)
    # cv2.namedWindow("Frame5: Dialated",0)
    # cv2.resizeWindow("Frame5: Dialated", width, length)
    # cv2.moveWindow("Frame5: Dialated",position_x, position_y + length)

    # cv2.imshow("Frame0: Raw",frame0)
    # cv2.imshow("Frame1: Gray",frame1)
    # cv2.imshow("Frame2: Blur",frame2)
    # cv2.imshow("Frame3: Delta",frame3)
    # cv2.imshow("Frame4: Threshold",frame4)
    # cv2.imshow("Frame5: Dialated",frame5)
    # cv2.imshow("Frame6: Contours",frame6)
    # cv2.imshow("Frame7: Target",frame7)

    imgc = cv2.cvtColor(frame5,cv2.COLOR_GRAY2BGR)
    both = np.concatenate((frame0,imgc), axis=0)   #1 : horz, 0 : Vert. 
    cv2.namedWindow("motion detection",0)
    # cv2.resizeWindow("motion detection", 640, 720)

    x, y = both.shape[0:2]
    both_resize = cv2.resize(both, (int(y / 3), int(x / 3)))
    out.write(both_resize)
    cv2.imshow('motion detection',both)

    # key delay and action
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key != 255:
        print('key:',[chr(key)])

# release camera
camera.release()

# release VideoWriter
out.release()

# close all windows
cv2.destroyAllWindows()
