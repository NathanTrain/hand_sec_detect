import time

from PyQt5.QtCore import QRunnable, pyqtSignal, pyqtSlot, QObject
from plc.plc import *

sleep_time = 0.1
stop_time = 0.1

class Signal(QObject):
    side_a = pyqtSignal(object)
    side_b = pyqtSignal(object)

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

class Worker_RobotCutting(QRunnable):
    """Worker para receber dados do CLP referentes às tags na TagList Geral, levando esses dados à diversos locais"""

    def __init__(self):
        super(Worker_RobotCutting, self).__init__()
        self.signal = Signal()
        self.running = True

    @pyqtSlot()
    def run(self):
        while self.running:
            try:
                cortando_a, cortando_b = read_multiples(["Robo.Input.RSA", "Robo.Input.RSB"])

                self.signal.side_a.emit(cortando_a)
                self.signal.side_b.emit(cortando_b)
            except Exception as e:
                print(f'{e} - Read Tags Worker')
            time.sleep(sleep_time)

    def stop(self):
        self.running = False
        time.sleep(stop_time)
