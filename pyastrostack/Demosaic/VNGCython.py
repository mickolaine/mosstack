from __future__ import division
from .. Demosaic.Demosaic import Demosaic
import numpy as np
import pyximport
pyximport.install(setup_args={'include_dirs': [np.get_include()]})
from . _VNGCython import _demosaic


class VNGCython(Demosaic):
    """
    Demosaicing class. I'll start with regular bilinear interpolation but more will come if necessary

    """

    def __init__(self):
        """Prepare everything for running the demosaic-algorithms."""

    def demosaic(self, image):
        """
        Bilinear interpolation for demosaicing CFA
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

        result = np.array(_demosaic(cfa, r, g, b))
        #print(result)
        return result