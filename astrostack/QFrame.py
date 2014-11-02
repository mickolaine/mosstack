"""
PyQt4 specific class. Program will run just fine on command line without PyQt but GUI requires it.
"""

from . Frame import Frame
from PyQt4 import QtGui
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

        idata = QFrame.align_32bit(data[0])


        #idata = np.swapaxes(idata, 0, 1)
        #idata = np.rot90(idata, 1)

        pimage = Image.fromarray(np.int16(idata)).convert("P")
        #pimage = pimage.convert("P")
        #print(pimage.size)
        #pimage.save("/home/micko/debug_pimage2.tiff")

        #imageqt = ImageQt.ImageQt(pimage)

        #__data = pimage.tobytes()
        #palette = pimage.getpalette()
        #colortable = []
        #for i in range(0, len(palette), 3):
        #    colortable.append(self._rgb(*palette[i:i + 3]))
        #qimage = QtGui.QImage(__data, pimage.size[0], pimage.size[1], QtGui.QImage.Format_Indexed8)


        #print(imageqt.size())
        #imageqt.save("/home/micko/debug_imageqt.jpg")
        #qimage = QtGui.QImage(imageqt)
        #qimage.save("/home/micko/debug_qimage.jpg")

        #qimage = qimage.scaled(w, h, aspectRatioMode=Qt.Qt.KeepAspectRatioByExpanding,
        #                             transformMode=Qt.Qt.SmoothTransformation)

        return QtGui.QPixmap.fromImage(ImageQt.ImageQt(pimage))

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

    @staticmethod
    def _rgb(r, g, b, a=255):
        """
        From Pillow PIL.ImageQt
        """

        # use qRgb to pack the colors, and then turn the resulting long
        # into a negative integer with the same bitpattern.
        return (QtGui.qRgba(r, g, b, a) & 0xffffffff)

    def update_ui(self):
        """
        Tell the user interface that something has changed and state of this object needs to be read again
        """
        pass


