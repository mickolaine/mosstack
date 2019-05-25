from . batch import Batch
from . qframe import QFrame
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QRunnable, pyqtSignal
from os.path import splitext, split


class QBatch(Batch, QWidget):
    """
    QBatch is a PyQt5 aware extension of Batch. I'm not sure how much this
    is needed yet so this might be integrated to Batch
    """
    refresh = pyqtSignal()
    __pyqtSignals__ = ("update")

    def __init__(self, project, ftype):
        Batch.__init__(self, project, ftype)
        QWidget.__init__(self)
        #super(Batch, self).__init__(project, ftype)
        #super(QWidget, self).__init__()
        #self.frames = {}
        self._framearray = {}

    def addfile(self, file, ftype):
        """
        Add a single file using Batch.addfile and do what gui needs
        to be done.
        """

        f_key = Batch.addfile(self, file, ftype)
        if f_key is None:
            #TODO: This should probably pop a message
            return
        self.framearray[f_key] = QFrame.from_frame(self.framearray[f_key])
        self.refresh.emit()

    def addfiles(self, allfiles, ftype):
        """
        Add several files at once. Used only with loading a project
        """

        # Check the files are indeed .info files. They should be but let
        # this be a check that I use this method properly
        rawfiles = []
        for i in allfiles:
            if splitext(i)[1] == ".info":
                rawfiles.append(i)

        for i in rawfiles:
            frame = QFrame(project=self.project, infopath=i)
            self.framearray[frame.number] = frame

    def getframearray(self):
        temp = []
        for i in self.framearray:
            temp.append([i, split(self.framearray[i].rawpath)[1],
                         self.framearray[i].ftype,
                         self.framearray[i].state["prepare"],
                         self.framearray[i].state["calibrate"],
                         self.framearray[i].state["debayer"],
                         self.framearray[i].state["register"]])
        #print(temp)
        for i in temp:

            # Do this only for states, not for rest of the table
            for j in (3, 4, 5, 6):
                if i[j] == 0:
                    i[j] = "Not started"
                elif i[j] == 1:
                    i[j] = "Working..."
                elif i[j] == 2:
                    i[j] = "Done!"
                elif i[j] == -1:
                    i[j] = "Error"
                else:
                    i[j] = "FAIL"
        #temp = sorted(temp, key=lambda frames: frames[0])
        self._framearray = temp
        return self._framearray

    def decode(self, number=None, frame=None):
        """
        Decode all frames.
        """
        if number is not None:
            self.framearray[str(number)].decode()
        if frame is not None:
            self.framearray[frame].decode()

        self.refresh.emit()

    def calibrate(self, frame, stacker, bias=0, dark=0, flat=0):
        """
        Calibrate a single frame
        """
        print("Calibrating frame " + self.framearray[frame].path())
        biasframe = None
        darkframe = None
        flatframe = None
        if bias > 0:
            biaspath = self.project.get("Masters", "bias")
            biasframe = QFrame(project=self.project, infopath=biaspath)
        if dark > 0:
            darkpath = self.project.get("Masters", "dark")
            biasframe = QFrame(project=self.project, infopath=darkpath)
        if flat > 0:
            flatpath = self.project.get("Masters", "flat")
            biasframe = QFrame(project=self.project, infopath=flatpath)

        self.framearray[frame].calibrate(stacker, biasframe, darkframe, flatframe)
        print("...Done")

        self.framearray[self.refId].isref = True
        print("Calibrated images saved with generic name 'calib'.")
        self.refresh.emit()

    def debayer_old(self, frame, debayer):
        """
        Debayer a single frame
        """

        print("Processing image " + self.framearray[frame].path())

        #self.frames[frame].debayer(debayer)
        self.framearray[frame].debayertool = debayer
        self.framearray[frame].debayer_worker()
        print("...Done")

        self.framearray[self.refId].isref = True
        print("Debayered images saved with generic name 'rgb'.")
        self.refresh.emit()

    def debayer_threaded(self, threadpool):

        for i in sorted(self.framearray):
            threadpool.start(GenericThread(self.framearray[i].debayer))

    def register(self, frame, register, ref=False):
        """
        Register a single frame
        """

        self.framearray[frame].register(register)

        self.refresh.emit()

    def register_threaded(self, threadpool):
        """
        Register all frames using threads
        """
        self.framearray[self.refId].register_worker()

        for i in sorted(self.framearray):
            if i == self.refId:
                continue
            threadpool.start(GenericThread(self.framearray[i].register))

        for i in sorted(self.framearray):
            threadpool.start(GenericThread(self.framearray[i].register))

    framearray = property(fget=getframearray)


class GenericThread(QRunnable):
    """
    Generic thread borrowed from http://joplaete.wordpress.com/2010/07/21/threading-with-pyqt4/

    Will rewrite this, when I understand what's happening here
    """
    __pyqtSignals__ = ("update")
    refresh = pyqtSignal()

    def __init__(self, function, *args, **kwargs):
        QRunnable.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.function(*self.args, **self.kwargs)
        return
