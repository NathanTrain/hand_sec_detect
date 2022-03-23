import time

from PyQt5.QtCore import QRunnable, pyqtSignal, pyqtSlot, QObject
from plc.plc import write_tag

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
