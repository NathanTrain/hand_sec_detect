import cv2 as cv
import mediapipe as mp
from tests.hid_test import *
from PyQt5.QtCore import QThreadPool

camera = cv.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()

mpDraw = mp.solutions.drawing_utils

seguro_a = False
seguro_b = False
mao_lado_a = False
mao_lado_b = False

def detect_hand():
    global seguro_a, seguro_b, mao_lado_a, mao_lado_b
    success, frame = camera.read()
    if not success:
        raise ConnectionError("Camera não conectada")
    imgRGB = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    frame.flags.writeable = False
    imgRGB.flags.writeable = False
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handCoord in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(frame, handCoord)
            if seguro_a:
                for lm in handCoord.landmark:
                    if lm.x >= 0.5 and not mao_lado_a:
                        seguro_a = False
                        mao_lado_a = True
                        disable_relay()
                        print("---- mão detectada no lado A ----")
            if seguro_b:
                for lm in handCoord.landmark:
                    if lm.x <= 0.5 and not mao_lado_b:
                        seguro_b = False
                        mao_lado_b = True
                        print("---- mão detectada no lado B ----")
    elif not results.multi_hand_landmarks:
        if not seguro_a:
            seguro_a = True
            mao_lado_a = False
            enable_relay()
            print("Seguro A")
        if not seguro_b:
            seguro_b = True
            mao_lado_b = False
            print("Seguro B")

    draw_box_a(frame, seguro_a)
    draw_box_b(frame, seguro_b)

    cv.imshow("Safety", frame)

def draw_box_a(frame, seguro):
    width = int(camera.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv.CAP_PROP_FRAME_HEIGHT))
    red = (0, 0, 255)
    green = (0, 255, 0)
    start_a = (int(width/2)+1
               , 0)
    end_a = (width, height)

    if seguro:
        cv.rectangle(frame, start_a, end_a, green, thickness=2)
    else:
        cv.rectangle(frame, start_a, end_a, red, thickness=2)

def draw_box_b(frame, seguro):
    width = int(camera.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv.CAP_PROP_FRAME_HEIGHT))
    red = (0, 0, 255)
    green = (0, 255, 0)
    start_b = (0, 0)
    end_b = (int(width/2)-1, height)

    if seguro:
        cv.rectangle(frame, start_b, end_b, green, thickness=2)
    else:
        cv.rectangle(frame, start_b, end_b, red, thickness=2)


while True:
    try:
        detect_hand()
        if cv.waitKey(20) & 0xFF == ord("f"):
            break
    except ConnectionError as e:
        print(f"--- Erro de conexão: {e} ---")
        break

camera.release()
cv.destroyAllWindows()

cv.waitKey(0)
