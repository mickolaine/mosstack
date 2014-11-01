"""
PyQt4 specific class. Program will run just fine on command line without PyQt but GUI requires it.
"""

from . Frame import Frame
from PyQt4 import QtGui
from PyQt4 import Qt
from PyQt4 import QtCore
import numpy as np
from PIL import Image, ImageQt


class QFrame(Frame):
    """
    QFrame is a variation of Frame class intended for PyQt4 gui. It inherits Frame, which represents one photo frame.
    This class holds everything specific to GUI and it's use requires PyQt4.
    """

    def __init__(self, project=None, rawpath=None, infopath=None, ftype="light", number=None, fphase="orig"):
        """

        """
        super(QFrame, self).__init__(project=project,
                                     rawpath=rawpath,
                                     infopath=infopath,
                                     ftype=ftype,
                                     number=number,
                                     fphase=fphase)

    def getQPixmap(self):
        """
        Return frame data as QImage
        """

        ch = self.data
        ch = ch - np.amin(ch)
        data = ch / np.amax(ch) * 255
        idata = data[0]
        print(idata.shape)
        #idata = np.swapaxes(idata, 0, 1)
        #idata = np.rot90(idata, 1)
        print(idata.shape)

        pimage = Image.fromarray(np.int16(idata))
        print(pimage.size)
        w, h = pimage.size
        h = int(h / 4)
        w = int(w / 4)
        print(w, h)

        pimage = pimage.convert("P")
        print(pimage.size)
        imageqt = ImageQt.ImageQt(pimage)
        qimage = QtGui.QImage(imageqt)
        print(qimage.size())
        #qimage = qimage.scaled(w, h, aspectRatioMode=Qt.Qt.KeepAspectRatioByExpanding,
        #                             transformMode=Qt.Qt.SmoothTransformation)
        print(qimage.size())
        return QtGui.QPixmap.fromImage(qimage)

    def update_ui(self):
        """
        Tell the user interface that something has changed and state of this object needs to be read again
        """
        pass


