import time
import cv2 as cv
import mediapipe as mp

from PyQt5.QtCore import QThreadPool, QRunnable, pyqtSignal, pyqtSlot, QObject
from plc import write_tag

sleep_time = 0.5
stop_time = 0.1

class WorkerSignals(QObject):
    result = pyqtSignal(bool)

class Worker_True(QRunnable):
    def __init__(self, tag:str):
        super(Worker_True, self).__init__()
        self.tag = tag

    @pyqtSlot()
    def run(self):
        try:
            write_tag(self.tag, True)
        except Exception as e:
            print(e)
        time.sleep(sleep_time)

class Worker_False(QRunnable):
    def __init__(self, tag:str):
        super(Worker_False, self).__init__()
        self.tag = tag

    @pyqtSlot()
    def run(self):
        try:
            write_tag(self.tag, False)
        except Exception as e:
            print(e)
        time.sleep(sleep_time)

class CamWorker(QRunnable):
    def __init__(self):
        super(CamWorker, self).__init__()
        self.running = True
        self.signal_a = WorkerSignals()
        self.signal_b = WorkerSignals()

        self.cam_externa = cv.VideoCapture(1)
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands()
        self.mpDraw = mp.solutions.drawing_utils

    @pyqtSlot()
    def run(self):
        while self.running:
            self.detect_hand_cam1()
        time.sleep(sleep_time)

    def detect_hand_cam1(self):
        success, frame = self.cam_externa.read()
        imgRGB = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = self.hands.process(imgRGB)

        if results.multi_hand_landmarks:
            for handCoord in results.multi_hand_landmarks:
                for index, lm in enumerate(handCoord.landmark):
                    if lm.x >= 0.5:
                        self.signal_a.result.emit(False)
                        print("---- mão detectada no lado A ----")
                    elif lm.x <= 0.5:
                        self.signal_b.result.emit(False)
                        print("---- mão detectada no lado B ----")
                self.mpDraw.draw_landmarks(frame, handCoord)
        else:
            self.signal_a.result.emit(True)
            self.signal_b.result.emit(True)
            print("Seguro")

        cv.imshow("Safety", frame)
