from . Batch import Batch
from . QFrame import QFrame
from PyQt4.QtGui import QWidget
from PyQt4.QtCore import *
from os.path import splitext


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

        # Check if the file is an .info file instead of raw file
        if splitext(file)[1] == ".info":
            frame = QFrame(project=self.project, infopath=file)
            self.frames[frame.number] = frame
            return

        self.frames[str(number)] = QFrame(project=self.project, rawpath=file, ftype=ftype, number=number)
        #self._framearray[number] = [self.frames[number].rawpath, ftype, self.frames[number].state["prepare"],
        #                                                      self.frames[number].state["calibrate"],
        #                                                      self.frames[number].state["debayer"],
        #                                                      self.frames[number].state["register"]]

        self.project.set(ftype, str(number), self.frames[number].infopath)
        #self.emit(SIGNAL("update"), "CALLED FROM addfile()")
        self.refresh.emit()

    def addfiles(self, allfiles, ftype):
        """
        Add several files at once. Used only with loading a project
        """

        # Check the files are indeed .info files. They should be but let this be a check that I use this method properly
        rawfiles = []
        for i in allfiles:
            if splitext(i)[1] == ".info":
                rawfiles.append(i)

        for i in rawfiles:
            frame = QFrame(project=self.project, infopath=i)
            self.frames[frame.number] = frame

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

        self.frames[str(number)].decode()
        #self.emit(SIGNAL("update"), "CALLED FROM decode()")
        self.refresh.emit()

    framearray = property(fget=getframearray)