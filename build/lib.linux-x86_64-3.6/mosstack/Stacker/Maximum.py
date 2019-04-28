"""
Class for maximum stacking. Used for calibration frames
"""

from .. Stacker.Stacking import Stacking
from numpy import zeros_like, maximum


class Maximum(Stacking):
    """
    Maximum stack includes the largest value for each pixel.

    Possible uses are for example getting satellite trails to same image.
    """

    @staticmethod
    def stack(imagelist, project):
        """
        Stack the list of images using largest value for every subpixel of every colour
        """

        n = len(imagelist)
        newdata = zeros_like(list(imagelist.values())[0].data)
        number = 1
        print("Starting maximum stack for " + str(n) + " images.")
        for i in imagelist:
            print("Adding image number " + str(number) + " of " + str(n))
            newdata = maximum(newdata, imagelist[i].data)
            number += 1

        return newdata