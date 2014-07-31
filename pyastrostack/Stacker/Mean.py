"""
Class for mean stacking. Used for calibration frames
"""

from .. Stacker.Stacking import Stacking
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
        print(imagelist.values())
        newdata = zeros_like(list(imagelist.values())[0].data)
        number = 1
        print("Starting mean stack for " + str(n) + " images.")
        for i in imagelist:
            print("Adding image number " + str(number) + " of " + str(n))
            newdata += imagelist[i].data / n
            number += 1

        return newdata