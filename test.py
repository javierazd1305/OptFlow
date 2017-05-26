import cv2
import imutils
import numpy as np
from ballClass import *
import time


def draw_flow(img, flow, step=6):
    suma = 0
    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    h, w = img.shape[:2]  # the size of the input image
    y, x = np.mgrid[step / 2:h:step, step /
                    2:w:step].reshape(2, -1).astype(int)  # Create two vectors [8-h/2][h/2-h]
    fx, fy = flow[y, x].T  # apply Optflow opencv
    # Now the move
    lines = np.vstack([x, y, x + fx, y + fy]).T.reshape(-1, 2, 2)
    lines = np.int32(lines + 1.5)
    minDist = 100000
    minimo = []
    menores = []
    for i in lines:
        # i[0] es la posicion
        # i[1] es el punto hacia donde ha cambiado
        if (i[0] != i[1]).all():
            # dibujar todos los movimientos
            # cv2.circle(vis, (i[0][0], i[0][1]), 4, (255, 255, 0), -1)
            diff = np.subtract(i[1], i[0])
            diff = np.absolute(diff)
            diff = np.sum(diff)
            if diff > 5:
                menores.append(i[0])
                # movimientos mayores a un threshold
                cv2.circle(vis, (i[0][0], i[0][1]), 4, (255, 0, 0), -1)
                ballClass(i[0][0], i[0][1])

    # cv2.polylines(vis, lines, 0, (0, 255, 0))
    prom = np.mean(menores, axis=0)
    # print menores
    try:
        cv2.circle(vis, (int(prom[0]), int(prom[1])), 10, (125, 12, 255), -1)
    except:
        pass
    for (x1, y1), (x2, y2) in lines:
        cv2.circle(vis, (x1, y1), 1, (0, 255, 0), -1)  # dibujar la malla
    return vis


cap = cv2.VideoCapture("video.avi")
#cap = cv2.VideoCapture(0)
ret, prev = cap.read()
prev = imutils.resize(prev, width=500, height=500)
prevgray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
start_time = time.time()
while 1:
    ballClass.registry = []
    ret, image = cap.read()
    image = imutils.resize(image, width=500, height=500)
    image_1 = image.copy()
    cv2.setMouseCallback('Frame', obtener_punto)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    flow = cv2.calcOpticalFlowFarneback(
        prevgray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    vis = draw_flow(gray, flow)
    clusters, newPoints, members = ballClass.wrapper()
    ballClass.drawClusters(image, clusters, newPoints, members)
    ballClass.trackClusters(clusters, image_1, time.time())
    drawAreas(image_1)
    # ballClass.drawOnlycluster(image_1)
    cv2.imshow("Frame", image)
    #cv2.imshow('flow', vis)
    cv2.imshow('clusters', image_1)
    prevgray = gray

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
