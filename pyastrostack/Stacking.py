#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 11.10.2013

@author: Mikko Laine

This file contains everything required for stacking the photos.
"""

import Photo
import numpy as np


# TODO: Create Stacker interface and make Mean it's implementation

class Mean:
    """
    Mean stacking should be easiest to implement, so I'll start with that.
    
    Each pixel will be a median value of the entire stack. Default for stacking bias, flat and dark.
    """
    
    def __init__(self):
        pass

    @staticmethod
    def stack(imagelist, project):
        """
        Stack the list of images using mean value for every subpixel of every colour
        """

        n = len(imagelist)
        newdata = np.zeros_like(imagelist[0].data)
        for i in imagelist:
            print(i.imagepath)
            print(np.amax(i.data))
            print(np.amax(newdata))
            newdata += (i.data / n)
            i.release()
            
        return newdata

    @staticmethod
    def subtract(batch, calib):
        """
        Calculates batch = batch - calib. Required for calibrating lights and flats
        """
        
        for i in batch.list:
            i.data = i.data - calib.data
            i.data.clip(0)
            i.write()
            #i.hdu.flush()

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
        Normalizes calib by maximum value for divide operation.
        """
        calib.data = calib.data / np.amax(calib.data)
        #calib.write()

    @staticmethod
    def divide(batch, calib):
        """
        Calculates batch = batch / calib.

        Required for dividing light with normalized flat.
        """
        for i in batch.list:
            i.data = i.data / calib.data
            i.data = np.nan_to_num(i.data)
            i.write()