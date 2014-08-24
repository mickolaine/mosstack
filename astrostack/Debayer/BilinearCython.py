from __future__ import division
from .. Debayer.Debayer import Debayer
import numpy as np
import pyximport
pyximport.install(setup_args={'include_dirs': [np.get_include()]})
from . _BilinearCython import _debayer

class BilinearCython(Debayer):
    """
    Debayering class. I'll start with regular bilinear interpolation but more will come if necessary

    """

    def __init__(self):
        """Prepare everything for running the debayer-algorithms."""

    def debayer(self, image):
        """
        Bilinear interpolation for debayering CFA
        Now assumes order of GR
                             BG

        Give cfa-image, receive rgb-image. Return numpy.array
        """
        #print(image)
        cfa = np.float32(image) #.byteswap().newbyteorder()
        #print(cfa)
        r = np.zeros_like(cfa)
        g = np.zeros_like(cfa)
        b = np.zeros_like(cfa)

        result = np.array(_debayer(cfa, r, g, b))
        #print(result)
        return result