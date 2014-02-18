"""
Class for mean stacking. Used for calibration frames
"""

__author__ = 'micko'

from .. Stacker.Stacking import Stacking
#import numpy as np
from numpy import zeros_like


class Mean(Stacking):
    """
    Mean stacking should be easiest to implement, so I'll start with that.

    Each pixel will be a median value of the entire stack. Default for stacking bias, flat and dark.
    """

    @staticmethod
    def stack(imagelist, project):
        """
        Stack the list of images using mean value for every subpixel of every colour
        """

        n = len(imagelist)
        imagelist["2"].load_data()
        newdata = zeros_like(imagelist["2"].data)
        for i in imagelist:
            imagelist[i].load_data()
            newdata += imagelist[i].data / n
            imagelist[i].release_data2()

        return newdata