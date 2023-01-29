import cv2 as cv
import numpy as np
import pyautogui
import HandTrackingModule as htm
import time
# import autopy
import pyautogui as PyGUI
from pynput.keyboard import Key, Controller
import math
# Volume control imp library
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


##########################
wCam, hCam = 640, 480
frameR = 100
smoothening = 5
###########################
cap = cv.VideoCapture(0)
prvlocX, prevlocY = 0, 0
currlocX, currlocY = 0, 0

cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0
detector = htm.handDetector(maxHands=1)
wScr, hScr = PyGUI.size()

vol = 0
volBar = 400
volPer = 0
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = (volume.GetVolumeRange())
minVol = volRange[0]
maxVol = volRange[1]

while True:
    # 1 Find the hand landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    # 2.Get the tip of the middle finger
    if len(lmList) != 0:

        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        # print(x1, y1, x2, y2)

        # Get the tip of the thumb finger
        x5, y5 = lmList[4][1:]

        # 3.Check which fingers are up
        fingers = detector.fingersUp()
        # print(fingers)
        cv.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

        # 4. Only Index Finger: Moving Mode
        if fingers[1] == 1 and fingers[2] == 0:
            # 5.Convert Coordinates
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

            # 6. Smoothen the value
            currlocX = prvlocX + (x3 - prvlocX) / smoothening
            currlocY = prevlocY + (y3 - prevlocY) / smoothening

            # 7. Move Mouse
            # PyGUI.moveTo(100, 100, 2, PyGUI.easeOutQuad)  # start fast, end slow
            # PyGUI.moveTo((wScr - currlocX), currlocY, PyGUI.easeOutQuad)  # start fast, end slow
            PyGUI.moveTo((wScr - currlocX), currlocY)
            cv.circle(img, (x1, y1), 15, (255, 0, 255), cv.FILLED)
            prvlocX, prevlocY = currlocX, currlocY

        # 8. Both Index and Middle fingers are up:Clicking None
        if fingers[1] == 1 and fingers[2] == 1:
            # 9.find distance between fingers
            length, img, lineInfo = detector.findDistance(fingers[1], fingers[2], img)
            # print(length)
            # 10.clicking mouse if distance is short(left)
            if length < 10:
                cv.circle(img, (lineInfo[4], lineInfo[5]), 10, (0, 255, 0), cv.FILLED)
                PyGUI.click(clicks=1, interval=0.25)

        # 11. Right click

        if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:
            PyGUI.click(button='right', clicks=1, interval=0.25)

        # 12. Scrolling(up and down)
        if fingers[0] == 1 and fingers[1] == 0 and fingers[2] == 0:
            # Convert the corrdinates
            x6 = np.interp(x5, (frameR, wCam - frameR), (0, wScr))
            y6 = np.interp(y5, (frameR, wCam - frameR), (0, wScr))
            print(x6, y6)
            # scroll down
            if (x6 < 1200 and y6 < 1050):
                pyautogui.scroll(-20)
            # Scroll up
            elif (x6 < 1200 and y6 > 1050):
                pyautogui.scroll(20)

        # Tab Switching
        keyboard = Controller()
        if fingers[1] == 1 and fingers[4] == 1 and fingers[2] == 0:
            keyboard.press(Key.cmd)
            keyboard.press(Key.tab)
            keyboard.release(Key.cmd)
            keyboard.release(Key.tab)
            time.sleep(1)

        # volume control
        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0:
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
            # Volume Range -65-0
            vol = np.interp(length, [50, 300], [minVol, maxVol])
            volBar = np.interp(length, [50, 300], [400, 150])
            volPer = np.interp(length, [50, 300], [0, 100])
            # print(int(volBar), vol)
            volume.SetMasterVolumeLevel(vol, None)

        # # Brightness Control
        #
        # if fingers[0] == 1 and fingers[2] == 1:
        #     x1, y1 = lmList[4][1], lmList[4][2]
        #     x2, y2 = lmList[12][1], lmList[12][2]
        #
        #     cv.circle(img, (x1, y1), 4, (255, 0, 0), cv.FILLED)
        #     cv.circle(img, (x2, y2), 4, (255, 0, 0), cv.FILLED)
        #     cv.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
        #
        #     length = math.hypot(x2 - x1, y2 - y1)
        #     print(length)

        #     bright = np.interp(length, [15, 220], [0, 100])
        #     print(bright, length)
        #     sbc.set_brightness(int(bright))
        #
        # if (length < 50):
        #     cv.circle(img, (cx, cy), 10, (0, 255, 255), cv.FILLED)

        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
            time.sleep(2)

    # 11. Frame rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv.putText(img, str(int(fps)), (20, 80), cv.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 3)

    # 12. Display
    cv.imshow("Image", img)

    if cv.waitKey(20) == ord('d'):
        break

cap.release()
cv.destroyAllWindows()
