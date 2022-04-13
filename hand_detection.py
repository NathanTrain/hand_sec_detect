import time
import cv2 as cv
import mediapipe as mp
from PyQt5.QtCore import QThreadPool
from ctrl_relay import turn_off, turn_on
from plc.plc_thread import Worker_ReadTags

camera = cv.VideoCapture(1)

mpHands = mp.solutions.hands
hands = mpHands.Hands()

mpDraw = mp.solutions.drawing_utils

seguro_a = False
seguro_b = False
mao_lado_a = False
mao_lado_b = False
cutting_a = False
cutting_b = False


def recebe_a(tag):
    global cutting_a
    cutting_a = tag


def recebe_b(tag):
    global cutting_b
    cutting_b = tag


def detect_hand():
    global seguro_a, seguro_b, mao_lado_a, mao_lado_b, cutting_a, cutting_b

    success, frame = camera.read()
    if not success:
        raise ConnectionError("Camera não conectada")
    imgRGB = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    frame.flags.writeable = False
    imgRGB.flags.writeable = False
    results = hands.process(imgRGB)

    if not cutting_a and not cutting_b:
        seguro_a = True
        seguro_b = True

    if results.multi_hand_landmarks:
        for handCoord in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(frame, handCoord)
            if cutting_a and seguro_a:
                for lm in handCoord.landmark:
                    if lm.x >= 0.5 and not mao_lado_a:
                        seguro_a = False
                        mao_lado_a = True
                        print("---- mão detectada no lado A ----")
            if cutting_b and seguro_b:
                for lm in handCoord.landmark:
                    if lm.x <= 0.5 and not mao_lado_b:
                        seguro_b = False
                        mao_lado_b = True
                        print("---- mão detectada no lado B ----")
    elif not results.multi_hand_landmarks:
        if not seguro_a:
            seguro_a = True
            mao_lado_a = False
            print("Seguro A")
        if not seguro_b:
            seguro_b = True
            mao_lado_b = False
            print("Seguro B")

    if seguro_a and seguro_b:
        turn_on()
    else:
        turn_off()

    draw_box_a(frame, seguro_a)
    draw_box_b(frame, seguro_b)

    cv.imshow("Safety", frame)


def draw_box_a(frame, seguro):
    width = int(camera.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv.CAP_PROP_FRAME_HEIGHT))
    red = (0, 0, 255)
    green = (0, 255, 0)
    start_a = (int(width/2)+1, 0)
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


if __name__ == "__main__":
    worker = Worker_ReadTags()
    worker.signal_ReadTags.side_a.connect(recebe_a)
    worker.signal_ReadTags.side_b.connect(recebe_b)

    thread = QThreadPool()
    thread.start(worker)

    try:
        turn_on()
        while True:
            detect_hand()
            if cv.waitKey(20) & 0xFF == ord("f"):
                break
        camera.release()
        cv.destroyAllWindows()
        cv.waitKey(0)
    except Exception as e:
        print(e)
    finally:
        worker.stop()
        turn_off()
