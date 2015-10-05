"""
PyQt4 specific class. Program will run just fine on command line without PyQt but GUI requires it.
"""

from . Frame import Frame
from PyQt4 import QtGui
import numpy as np
from PIL import Image #, ImageQt


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

        idata = QFrame.align_32bit(np.flipud(data[0]))

        pimage = Image.fromarray(np.int16(idata)).convert("P")

        #return QtGui.QPixmap.fromImage(ImageQt.ImageQt(pimage))
        return None

    @staticmethod
    def align_32bit(data):
        """
        QImage requires 32bit aligned images. This checks the dimensions and crops some off if necessary.

        Note that this does not affect real data, only the image shown on screen. Real data still holds every pixel.

        Arguments:
        data: 2D numpy array

        Return:
        32bit aligned data
        """

        y, x = data.shape
        xc = x % 4
        yc = y % 4
        if xc != 0:
            if yc != 0:
                return data[:-yc, :-xc]
            else:
                return data[:, :-xc]
        else:
            if yc != 0:
                return data[:-yc, :]
        return data

    def update_ui(self):
        """
        Tell the user interface that something has changed and state of this object needs to be read again
        """
        pass


