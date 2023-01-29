import cv2 as cv
import numpy as np
import pyautogui
import HandTrackingModule as htm
import time
import screen_brightness_control as sbc
import math


#############################
wCam, hCam = 640, 480
##############################

cap = cv.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
vol = 0
volBar = 400
volPer = 0
detector = htm.handDetector(detectionCon=0.7)


while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv.circle(img, (x1, y1), 10, (255, 0, 255), cv.FILLED)
        cv.circle(img, (x2, y2), 10, (255, 0, 255), cv.FILLED)
        cv.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv.circle(img, (cx, cy), 10, (255, 0, 255), cv.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)

        # print(length)

        # Hand range  50-300
        # Brigtness Range -65-0
        bright = np.interp(length, [15, 220], [0, 100])
        print(bright, length)
        sbc.set_brightness(int(bright))

        if (length < 50):
            cv.circle(img, (cx, cy), 10, (0, 255, 255), cv.FILLED)

    cv.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    cv.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv.FILLED)
    cv.putText(img, f'per: {int(volPer)}%', (40, 450), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv.putText(img, f'FPS: {int(fps)}', (40, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
    cv.imshow('image', img)
    if cv.waitKey(1) == ord('d'):
        break

cap.release()
cv.destroyAllWindows()


# # Brightness Control
#
#         if fingers[0] == 1 and fingers[2] == 1:
#             x1, y1 = lmList[4][1], lmList[4][2]
#             x2, y2 = lmList[12][1], lmList[12][2]
#
#             cv.circle(img, (x1, y1), 4, (255, 0, 0), cv.FILLED)
#             cv.circle(img, (x2, y2), 4, (255, 0, 0), cv.FILLED)
#             cv.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
#
#             length = math.hypot(x2 - x1, y2 - y1)
#             print(length)
#
#             bright = np.interp(length, [15, 220], [0, 100])
#             print(bright, length)
#             sbc.set_brightness(int(bright))
#
#         if (length < 50):
#             cv.circle(img, (cx, cy), 10, (0, 255, 255), cv.FILLED)
#
#
#      cTime = time.time()
#     fps = 1 / (cTime - pTime)
#     pTime = cTime
#
#     cv.putText(img, f'FPS: {int(fps)}', (40, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
#     cv.imshow('image', img)
#     if cv.waitKey(1) == ord('d'):
#         break
#
# cap.release()
# cv.destroyAllWindows()