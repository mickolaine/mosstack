"""
Class for median stacker. Will be probably named Median.py instead of Median2.py for final 0.1
"""

from .. Stacker.Stacking import Stacking
import numpy as np
import gc
import math
import datetime   # For profiling
import pyximport
pyximport.install(setup_args={'include_dirs': [np.get_include()]})
from . _math import _sigmaMedian


class SigmaMedian(Stacking):
    """
    Each pixel will be a median value of the entire stack.

    Calculation will be done in parts to save memory. This will quickly consume 20GB otherwise
    """

    def __init__(self):
        #super().__init__()
        pass

    @staticmethod
    def stack(imagelist, project):
        """
        Stack the list of images using median value for every subpixel of every colour
        """
        print("Beginning sigma sum stack...")

        # Determine number of slices. My idea is to have it about the same as number of images, but in n^2
        # for 10 images it could be 3^2 = 9  or 4^2 = 16
        # for 20 images             4^2 = 16 or 5^2 = 25

        t = []
        t.append(datetime.datetime.now())

        images = len(imagelist)

        n = math.ceil(math.sqrt(images)) - 1  # n^2 will be the nearest square < number of images
                                              # at most there will be two image worth of data in memory

        ### Calculating image clip coordinates

        X = list(imagelist.values())[0].x
        Y = list(imagelist.values())[0].y

        #print(X)
        #print(n)
        xclip = math.ceil(X / n)
        yclip = math.ceil(Y / n)

        dX = 0
        dY = 0

        sec = []
        r = []
        g = []
        b = []
        result = None

        t.append(datetime.datetime.now())

        while dX < X:
            if X - dX > xclip:
                dY = 0
                while dY < Y:
                    if Y - dY > yclip:
                        sec.append((dX, dX + xclip - 0, dY, dY + yclip - 0))
                        dY += yclip
                    else:
                        sec.append((dX, dX + xclip - 0, dY, Y))
                        dY = Y
                dX += xclip
            else:
                dY = 0
                while dY < Y:
                    if Y - dY > yclip:
                        sec.append((dX, X, dY, dY + yclip -0))
                        dY += yclip
                    else:
                        sec.append((dX, X, dY, Y))
                        dY = Y
                dX = X

        inumber = 0

        lines = []
        line = None
        for clip in sec:

            if clip[0] != line:
                lines.append([])
                i = len(lines) - 1
                lines[i].append(clip)
                line = clip[0]
            else:
                lines[i].append(clip)

        t.append(datetime.datetime.now())

        for line in lines:
            tempslice = None
            for clip in line:
                print("Calculating clip " + str(inumber + 1) + " of " + str(len(sec)))

                templist = []
                for i in imagelist:
                    imagelist[i].setclip(clip)
                    templist.append(imagelist[i].data)
                t.append(datetime.datetime.now())
                templist = np.array(templist)
                t.append(datetime.datetime.now())

                print(templist.shape)
                temp = _sigmaMedian(templist, np.std(templist, axis=0), np.median(templist, axis=0), 3.0)
                t.append(datetime.datetime.now())
                print(temp.shape)

                del templist
                gc.collect()

                inumber += 1

                if tempslice is None:
                    tempslice = temp
                else:
                    tempslice = np.hstack([tempslice, temp])
                t.append(datetime.datetime.now())
                #for i in t:
                #    print(i -t[0])

            if result is None:
                result = tempslice
            else:
                result = np.dstack([result, tempslice])

        return result
