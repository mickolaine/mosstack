from . Batch import Batch
from . QFrame import QFrame
from PyQt4.QtGui import QWidget
from PyQt4.QtCore import SIGNAL


class QBatch(Batch, QWidget):
    """
    QBatch is a PyQt4 aware extension of Batch. I'm not sure how much this is needed yet so this might be
    integrated to Batch
    """

    def __init__(self, project, ftype):
        super(QWidget, self).__init__()
        super(QBatch, self).__init__(project, ftype)
        self.frames = {}
        self._framearray = {}

    def addfile(self, file, ftype):
        """
        Add a single file. Internal use only
        """

        try:
            n = len(self.project.get(ftype).keys())
        except KeyError:
            n = 0

        self.frames[n] = QFrame(project=self.project, rawpath=file, ftype=ftype, number=n)
        self._framearray[n] = [self.frames[n].rawpath, ftype, self.frames[n].state["prepare"],
                                                              self.frames[n].state["calibrate"],
                                                              self.frames[n].state["debayer"],
                                                              self.frames[n].state["register"]]

        self.project.set(ftype, str(n), self.frames[n].infopath)
        print("BAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        self.emit(SIGNAL('updateTableView(QString)'), "FOO")

    def getframearray(self):
        temp = []
        for i in self._framearray:
            temp.append(self._framearray[i])
        print(temp)
        return temp

    framearray = property(fget=getframearray)