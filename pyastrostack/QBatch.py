from . Batch import Batch
from . QFrame import QFrame
from PyQt4.QtGui import QWidget
#from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import *


class QBatch(Batch, QWidget):
    """
    QBatch is a PyQt4 aware extension of Batch. I'm not sure how much this is needed yet so this might be
    integrated to Batch
    """
    refresh = pyqtSignal()
    __pyqtSignals__ = ("update")

    def __init__(self, project, ftype):
        super(QBatch, self).__init__(project, ftype)
        super(QWidget, self).__init__()
        #self.frames = {}
        self._framearray = {}

    def addfile(self, file, ftype, number):
        """
        Add a single file. Internal use only
        """

        self.frames[number] = QFrame(project=self.project, rawpath=file, ftype=ftype, number=number)
        #self._framearray[number] = [self.frames[number].rawpath, ftype, self.frames[number].state["prepare"],
        #                                                      self.frames[number].state["calibrate"],
        #                                                      self.frames[number].state["debayer"],
        #                                                      self.frames[number].state["register"]]

        self.project.set(ftype, str(number), self.frames[number].infopath)
        #self.emit(SIGNAL("update"), "CALLED FROM addfile()")
        self.refresh.emit()

    def getframearray(self):
        temp = []
        for i in self.frames:
            temp.append([self.frames[i].rawpath, self.frames[i].ftype, self.frames[i].state["prepare"],
                                                            self.frames[i].state["calibrate"],
                                                            self.frames[i].state["debayer"],
                                                            self.frames[i].state["register"]])
        #print(temp)
        self._framearray = temp
        return self._framearray

    def decode(self, number):
        """
        Decode all frames.
        """

        self.frames[number].decode()
        #self.emit(SIGNAL("update"), "CALLED FROM decode()")
        self.refresh.emit()

    framearray = property(fget=getframearray)