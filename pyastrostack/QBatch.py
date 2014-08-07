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

    def decode(self, number=None, frame=None):
        """
        Decode all frames.
        """
        if number is not None:
            self.frames[str(number)].decode()
        if frame is not None:
            self.frames[frame].decode()

        self.refresh.emit()

    def calibrate(self, frame, stacker, bias=None, dark=None, flat=None):
        """
        Calibrate a single frame
        """
        print("Calibrating frame " + self.frames[frame].path())
        biasframe = None
        darkframe = None
        flatframe = None
        if bias:
            biaspath = self.project.get("Masters", "bias")
            biasframe = QFrame(project=self.project, infopath=biaspath)
        if dark:
            darkpath = self.project.get("Masters", "dark")
            biasframe = QFrame(project=self.project, infopath=darkpath)
        if flat:
            flatpath = self.project.get("Masters", "flat")
            biasframe = QFrame(project=self.project, infopath=flatpath)

        self.frames[frame].calibrate(stacker, biasframe, darkframe, flatframe)
        print("...Done")
        self.project.set("Reference images", self.fphase, str(self.refnum))
        self.frames[str(self.refnum)].isref = True
        print("Calibrated images saved with generic name 'calib'.")
        self.refresh.emit()

    def debayer(self, frame, debayer):
        """
        Debayer a single frame
        """

        print("Processing image " + self.frames[frame].path())
        #t1 = datetime.datetime.now()
        self.frames[frame].debayer(debayer)
        #t2 = datetime.datetime.now()
        print("...Done")
        #print("Debayering took " + str(t2 - t1) + " seconds.")
        self.project.set("Reference images", self.fphase, str(self.refnum))
        self.frames[str(self.refnum)].isref = True
        print("Debayered images saved with generic name 'rgb'.")
        self.refresh.emit()

    def register(self, frame, register):
        """
        Register a single frame
        """

        self.frames[frame].register(register)
        self.project.set("Reference images", self.fphase, str(self.refnum))
        self.refresh.emit()

    framearray = property(fget=getframearray)