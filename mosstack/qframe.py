"""
PyQt5 specific class. Program will run just fine on command line without PyQt but GUI requires it.
"""

import numpy as np
from PIL import Image
from . frame import Frame


class QFrame(Frame):
    """
    QFrame is a variation of Frame class intended for PyQt5 gui. It inherits
    Frame, which represents one photo frame. This class holds everything
    specific to GUI and its use requires PyQt5.
    """

    def __init__(self, project=None, rawpath=None, infopath=None,
                 ftype="light", number=None, fphase="orig"):
        """
        Initializing the QFrame is quite identical to initializing Frame. Calling
        super is enough.
        """
        super(QFrame, self).__init__(project=project,
                                     rawpath=rawpath,
                                     infopath=infopath,
                                     ftype=ftype,
                                     number=number,
                                     fphase=fphase)

    @staticmethod
    def from_frame(frame):
        """
        Return QFrame created from Frame
        """
        project = frame.project
        rawpath = frame.rawpath
        infopath = frame.infopath
        ftype = frame.ftype
        number = frame.number
        fphase = frame.fphase
        return QFrame(project, rawpath, infopath, ftype, number, fphase)

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
        QImage requires 32bit aligned images. This checks the dimensions
        and crops some off if necessary.

        Note that this does not affect real data, only the image shown on
        screen. Real data still holds every pixel.

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
