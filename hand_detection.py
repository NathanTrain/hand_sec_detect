from plc.plc_thread import *

from PyQt5.QtCore import QThreadPool

cam_externa = cv.VideoCapture(1)

mpHands = mp.solutions.hands
hands = mpHands.Hands()

mpDraw = mp.solutions.drawing_utils

thread_a = QThreadPool()
thread_b = QThreadPool()

seguro_a = False
seguro_b = False
mao_lado_a = False
mao_lado_b = False

def send_a(signal: bool):
    worker_a = WriteWorker("Safety_SideA",  signal)
    thread_a.start(worker_a)

def send_b(signal: bool):
    worker_b = WriteWorker("Safety_SideB",  signal)
    thread_b.start(worker_b)

def detect_hand_cam1():
    global seguro_a, seguro_b, mao_lado_a, mao_lado_b
    success, frame = cam_externa.read()
    # imgRGB = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    frame.flags.writeable = False
    # imgRGB.flags.writeable = False
    results = hands.process(frame)

    if results.multi_hand_landmarks and seguro_a:
        for handCoord in results.multi_hand_landmarks:
            for index, lm in enumerate(handCoord.landmark):
                if lm.x >= 0.5 and not mao_lado_a:
                    seguro_a = False
                    mao_lado_a = True
            if mao_lado_a:
                worker_false_a = Worker_False("Safety_SideA")
                thread_a.start(worker_false_a)
                print("---- mão detectada no lado A ----")
            mpDraw.draw_landmarks(frame, handCoord)
    elif not results.multi_hand_landmarks and not seguro_a:
        seguro_a = True
        mao_lado_a = False
        worker_true_a = Worker_True("Safety_SideA")
        thread_a.start(worker_true_a)
        print("Seguro B")

    if results.multi_hand_landmarks and seguro_b:
        for handCoord in results.multi_hand_landmarks:
            for index, lm in enumerate(handCoord.landmark):
                if lm.x <= 0.5 and not mao_lado_b:
                    seguro_b = False
                    mao_lado_b = True
            if mao_lado_b:
                worker_false_b = Worker_False("Safety_SideB")
                thread_b.start(worker_false_b)
                print("---- mão detectada no lado B ----")
            mpDraw.draw_landmarks(frame, handCoord)
    elif not results.multi_hand_landmarks and not seguro_b:
        seguro_b = True
        mao_lado_b = False
        worker_true_b = Worker_True("Safety_SideB")
        thread_b.start(worker_true_b)
        print("Seguro A")

    if results.multi_hand_landmarks:
        for handCoord in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(frame, handCoord)

    cv.imshow("Safety", frame)
    cv.waitKey(1)


# worker_cam.signal_a.result.connect(lambda signal: send_a(signal))
# worker_cam.signal_b.result.connect(lambda signal: send_b(signal))

while True:
    detect_hand_cam1()
    if cv.waitKey(20) & 0xFF == ord("f"):
        break

# webcam_pc.release()
# cam_externa.release()
# cv.destroyAllWindows()

cv.waitKey(0)
