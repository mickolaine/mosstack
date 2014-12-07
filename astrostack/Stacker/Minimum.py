"""
Class for minimum stacking. Used for calibration frames
"""

from .. Stacker.Stacking import Stacking
from numpy import zeros_like, minimum


class Minimum(Stacking):
    """
    Minimum
    """

    @staticmethod
    def stack(imagelist, project):
        """
        Stack the list of images using smallest value for every subpixel of every colour
        """

        n = len(imagelist)
        newdata = imagelist["0"].data
        number = 1
        print("Starting minimum stack for " + str(n) + " images.")
        for i in imagelist:
            print("Adding image number " + str(number) + " of " + str(n))
            newdata = minimum(newdata, imagelist[i].data)
            number += 1

        return newdata