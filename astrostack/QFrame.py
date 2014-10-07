"""
PyQt4 specific class. Program will run just fine on command line without PyQt but GUI requires it.
"""

from . Frame import Frame
from PyQt4 import QtGui
from PyQt4 import Qt
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
        idata = np.swapaxes(idata, 0, 1)

        pimage = Image.fromarray(np.int16(idata))

        pimage = pimage.convert("P")

        w, h = idata.shape
        imageqt = ImageQt.ImageQt(pimage)

        qimage = QtGui.QImage(imageqt)
        qimage = qimage.scaled(w * .25, h * .25, aspectRatioMode=Qt.Qt.IgnoreAspectRatio,
                                                 transformMode=Qt.Qt.SmoothTransformation)

        return QtGui.QPixmap.fromImage(qimage)

    def update_ui(self):
        """
        Tell the user interface that something has changed and state of this object needs to be read again
        """
        pass


