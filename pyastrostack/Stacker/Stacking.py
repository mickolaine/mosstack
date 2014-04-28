"""
Created on 11.10.2013

@author: Mikko Laine

This file contains everything required for stacking the photos.
"""
from __future__ import division
import numpy as np
import datetime   # For profiling
import math
import gc


class Stacking:
    """
    Abstract class for all stacking methods. Stackers can now be implemented by inheriting this class and
    writing a suitable self._realstack(). It is also possible to substitute Stacking.stack with something completely
    different.

    This class also includes frame subtractions and divisions and basic versions of them has been implemented here.
    Feel free to add better ones to your stacker.
    """
    
    def __init__(self):
        pass

    #@staticmethod
    def stack(self, imagelist, project):
        """
        Stack images in list. Requires subclass that implements the stacking itself.

        This function takes care of splitting frames into smaller pieces and putting them back together. Stacking
        functionality has to be written in a subclass of Stacking to function _realstack(), which is only called here.
        This abstract class does not implement it.

        Arguments:
        imagelist - a dict holding ("key": Photo) pairs to be stacked
        project - Project info object

        Return:
        newdata - a numpy.array of same form than imagelists Photo.data
        """

        # Determine number of slices. My idea is to have it about the same as number of images, but in n^2
        # for 10 images it could be 3^2 = 9  or 4^2 = 16
        # for 20 images             4^2 = 16 or 5^2 = 25

        images = len(imagelist)

        n = math.ceil(math.sqrt(images)) - 1  # n^2 will be the nearest square < number of images
                                              # at most there will be two image worth of data in memory

        ### Calculating image clip coordinates

        X = list(imagelist.values())[0].x
        Y = list(imagelist.values())[0].y

        xclip = math.ceil(X / n)
        yclip = math.ceil(Y / n)

        dX = 0
        dY = 0

        sec = []
        result = None

        # Calculating indices for clips
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

        # Organize clips to stripes. This makes putting image back together a lot easier
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

        # Take clips one line at a time
        for line in lines:
            tempslice = None
            for clip in line:
                print("Calculating clip " + str(inumber + 1) + " of " + str(len(sec)))

                # Construct 3d array of all the frames
                templist = []
                for i in imagelist:
                    imagelist[i].setclip(clip)

                    if len(templist) == 0:
                        templist = imagelist[i].data[np.newaxis, :, :]
                    else:
                        templist = np.vstack((templist, imagelist[i].data[np.newaxis, :, :]))

                ### The stacking itself.
                temp = self._realstack(templist)

                ###

                del templist
                gc.collect()

                inumber += 1

                if tempslice is None:
                    tempslice = temp
                else:
                    tempslice = np.hstack([tempslice, temp])

            if result is None:
                result = tempslice
            else:
                result = np.dstack([result, tempslice])

        return result

    @staticmethod
    def subtract(image, calib):
        """
        Calculates image - calib. Required for calibrating lights and flats

        Arguments:
        image - Photo to calibrate
        calib - Masterframe Photo to calibrate with

        Return:
        calibrated data as an array
        """

        newdata = image.data - calib.data
        newdata = newdata.clip(0)
        return np.uint16(newdata)

    @staticmethod
    def clip(batch):
        """
        Clip negative values replacing them by 0
        """
        batch.master.data = batch.master.data.clip(0)
        batch.master.write()

    @staticmethod
    def normalize(calib):
        """
        Normalizes calib by maximum  value for divide operation.

        Arguments:
        calib - Photo to normalize

        Return:
        normalized data array
        """
        return calib.data / np.amax(calib.data)


    @staticmethod
    def divide(image, calib):
        """
        Calculates image / calib. Calibration frame is normalized automatically.

        Arguments:
        image - Photo to calibrate
        calib - Masterframe Photo to calibrate with
        """
        maxim = np.amax(calib.data)
        newdata = image.data / calib.data * maxim
        return newdata