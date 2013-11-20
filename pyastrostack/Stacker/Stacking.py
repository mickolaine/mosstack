#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 11.10.2013

@author: Mikko Laine

This file contains everything required for stacking the photos.
"""

import numpy as np


class Stacking:
    """
    Abstract class for all stacking methods. Stackers can now be implemented by inheriting this class and
    writing a suitable self.stack().

    This class also includes frame subtractions and divisions and basic versions of them has been implemented here.
    Feel free to add better ones to your stacker.
    """
    
    def __init__(self):
        pass

    @staticmethod
    def stack(imagelist, project):
        """
        Interface for stacking.

        Arguments:
        imagelist - a dict holding ("key": Photo) pairs to be stacked

        Return:
        newdata - a numpy.array of same form than imagelists Photo.data
        """
        pass

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
        newdata.clip(0)
        return newdata

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
        maxim = np.amax(image.data)
        newdata = image.data / calib.data * maxim
        return newdata