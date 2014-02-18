"""
Class for median stacker. Will be probably named Median.py instead of Median2.py for final 0.1
"""

from .. Stacker.Stacking import Stacking
import numpy as np
import gc
import math
import datetime   # For profiling


class Median(Stacking):
    """
    Each pixel will be a median value of the entire stack.

    Calculation will be done in parts to save memory. This will quickly consume 20GB otherwise
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def stack(imagelist, project):
        """
        Stack the list of images using median value for every subpixel of every colour
        """
        print("Beginning median stack...")

        # Determine number of slices. My idea is to have it about the same as number of images, but in n^2
        # for 10 images it could be 3^2 = 9  or 4^2 = 16
        # for 20 images             4^2 = 16 or 5^2 = 25

        images = len(imagelist)

        n = math.ceil(math.sqrt(images)) - 1  # n^2 will be the nearest square < number of images
                                              # at most there will be two image worth of data in memory

        ### Calculating image clip coordinates
        X = imagelist["2"].x
        Y = imagelist["2"].y
        rgb = imagelist["2"].rgb

        xclip = math.ceil(X / n)
        yclip = math.ceil(Y / n)

        dX = 0
        dY = 0

        sec = []
        r = []
        g = []
        b = []
        result = None

        while dX < X:
            if X - dX > xclip:
                dY = 0
                while dY < Y:
                    if Y - dY > yclip:
                        # print("Y = " + str(Y) + ": dY = " + str(dY) + ": yclip = " + str(yclip))
                        # print("X = " + str(X) + ": dX = " + str(dX) + ": xclip = " + str(xclip))
                        # print("dX + xclip - 0 = " + str(dX + xclip - 0) + ": dY + yclip - 0 = " + str(dY + yclip - 0))
                        sec.append((dX, dX + xclip - 0, dY, dY + yclip - 0))
                        dY += yclip
                    else:
                        # print("Y = " + str(Y) + ": dY = " + str(dY) + ": yclip = " + str(yclip))
                        # print("X = " + str(X) + ": dX = " + str(dX) + ": xclip = " + str(xclip))
                        # print("dX + xclip - 0 = " + str(dX + xclip - 0) + ": dY = " + str(dY))
                        sec.append((dX, dX + xclip - 0, dY, Y))
                        dY = Y
                dX += xclip
            else:
                dY = 0
                while dY < Y:
                    if Y - dY > yclip:
                        # print("Y = " + str(Y) + ": dY = " + str(dY) + ": yclip = " + str(yclip))
                        # print("X = " + str(X) + ": dX = " + str(dX) + ": xclip = " + str(xclip))
                        # print("X = " + str(X) + ": dY + yclip - 0" + str(dY + yclip - 0))
                        sec.append((dX, X, dY, dY + yclip -0))
                        dY += yclip
                    else:
                        # print("Y = " + str(Y) + ": dY = " + str(dY) + ": yclip = " + str(yclip))
                        # print("X = " + str(X) + ": dX = " + str(dX) + ": xclip = " + str(xclip))
                        sec.append((dX, X, dY, Y))
                        dY = Y
                dX = X

        inumber = 0

        lines = []
        line = None
        for clip in sec:
            #print(clip)
            if clip[0] != line:
                lines.append([])
                i = len(lines) - 1
                lines[i].append(clip)
                line = clip[0]
            else:
                lines[i].append(clip)

        # for line in lines:
        #     print(line)

        t1 = datetime.datetime.now()

        for line in lines:
            rslice = None
            gslice = None
            bslice = None
            for clip in line:
                print("Calculating clip " + str(inumber + 1) + " of " + str(len(sec)))

                if rgb:
                    rlist = []
                    glist = []
                    blist = []
                    for i in imagelist:
                        imagelist[i].load_data2(clip)
                        rlist.append(imagelist[i].data[0].copy())  # *1.265026)
                        glist.append(imagelist[i].data[1].copy())
                        blist.append(imagelist[i].data[2].copy())  # *2.525858)
                        imagelist[i].release_data2()
                    r = np.median(rlist, axis=0)
                    del rlist
                    gc.collect()
                    g = np.median(glist, axis=0)
                    del glist
                    gc.collect()
                    b = np.median(blist, axis=0)
                    del blist
                    gc.collect()

                    if rslice is None:
                        rslice = r
                        gslice = g
                        bslice = b
                    else:
                        #print(rslice.shape)
                        #print(r.shape)
                        rslice = np.r_[rslice, r]
                        gslice = np.r_[gslice, g]
                        bslice = np.r_[bslice, b]
                        #print(rslice.shape)

                else:
                    rlist = []
                    for i in imagelist:
                        imagelist[i].load_data2(clip)
                        rlist.append(imagelist[i].data)
                        imagelist[i].release_data2()
                        gc.collect()
                    r = np.median(rlist, axis=0)  # Use r-list to store monochrome data
                    del rlist
                    gc.collect()

                    if rslice is None:
                        rslice = r

                    else:
                        rslice = np.r_[rslice, r]

                inumber += 1

            if result is None:
                if rgb:
                    result = [rslice, gslice, bslice]
                else:
                    result = rslice
            else:
                if rgb:
                    result = [np.c_[result[0], rslice], np.c_[result[1], gslice], np.c_[result[2], bslice]]
                else:
                    result = np.c_[result, rslice]

        for i in imagelist:
            imagelist[i].release()
            gc.collect()

        t2 = datetime.datetime.now()

        print("Calculating done!")
        print("Calculating took " + str(t2 - t1))
        if rgb:
            return np.int16(np.array(result))
        else:
            return result
