import time
import threading
import cv2 as cv
import mediapipe as mp
from PyQt5.QtCore import QThreadPool
from ctrl_relay import turn_off, turn_on
from plc.plc_thread import *

camera = cv.VideoCapture(0)

mpSolutions = mp.solutions

hands = mpSolutions.hands.Hands()
mpDraw = mpSolutions.drawing_utils

seguro_a = False
seguro_b = False
mao_lado_a = False
mao_lado_b = False
cutting_a = False
cutting_b = False
running = True


def recebe_a(tag):
    global cutting_a
    print(f"recebendo {tag}")
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

    # print(cutting_a)
    # print(cutting_b)

    draw_box_a(frame, seguro_a)
    draw_box_b(frame, seguro_b)

    draw_text(frame, "Pressione F para fechar a janela")

    cv.imshow("Safety", frame)


def draw_text(frame, text):
    width = int(camera.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv.CAP_PROP_FRAME_HEIGHT))
    font = cv.QT_FONT_NORMAL
    cv.putText(frame,
               text,
               (int(width/2)+40, height-15),
               font, 0.5,
               (255, 255, 255),
               1,
               cv.LINE_AA)


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


def read_tags_plc():
    global running, cutting_a, cutting_b
    while running:
        try:
            cortando_a, cortando_b = read_multiples(["Robo.Input.RSA", "Robo.Input.RSB"])

            cutting_a = cortando_a.value
            cutting_b = cortando_b.value
        except Exception as e:
            print(f'{e} - read_tags_plc')


if __name__ == "__main__":
    # worker = Worker_RobotCutting()
    # worker.signal.side_a.connect(print_func)
    # worker.signal.side_b.connect(print_func)
    #
    # thread = QThreadPool()
    # thread.start(worker)

    thread_plc = threading.Thread(target=read_tags_plc)
    thread_plc.start()

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
        # worker.stop()
        running = False
        turn_off()
