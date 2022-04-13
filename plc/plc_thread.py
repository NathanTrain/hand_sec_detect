import time

from PyQt5.QtCore import QRunnable, pyqtSignal, pyqtSlot, QObject
from plc.plc import write_tag, read_tags

sleep_time = 0.5
stop_time = 0.1

class WorkerSignals(QObject):
    side_a = pyqtSignal(bool)
    side_b = pyqtSignal(bool)

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

class Worker_ReadTags(QRunnable):
    """Worker para receber dados do CLP referentes às tags na TagList Geral, levando esses dados à diversos locais"""

    def __init__(self):
        super(Worker_ReadTags, self).__init__()
        self.signal_ReadTags = WorkerSignals()
        self.running = True

    @pyqtSlot()
    def run(self):
        while self.running:
            try:
                cortando_a = read_tags("HMI.RobotCuttingSideA")
                cortando_b = read_tags("HMI.RobotCuttingSideB")

                self.signal_ReadTags.side_a.emit(cortando_a)
                self.signal_ReadTags.side_b.emit(cortando_b)
            except Exception as e:
                print(f'{e} - Read Tags Worker')
                # self.stop()
                # break
            time.sleep(sleep_time)

    def stop(self):
        self.running = False
        time.sleep(stop_time)
