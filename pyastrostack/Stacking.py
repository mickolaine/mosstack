#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 11.10.2013

@author: Mikko Laine

This file contains everything required for stacking the photos.
"""

from pyastrostack import Image
import numpy as np


class Mean:
    """
    Mean stacking should be easiest to implement, so I'll start with that.
    
    Each pixel will be a median value of the entire stack. Default for stacking bias, flat and dark.
    """
    
    def __init__(self):
        pass
    
    def stack(self, batch):
        """
        Stack the batch using mean value for every subpixel of every colour
        """
        
        
        n = len(batch.list)

        if batch.type == "light":
            for i in batch.list:
                if i.number == 0:               # do this so ref gets first
                    i.reload("light", ref=1)
                    r = i.data[0]/n
                    g = i.data[1]/n
                    b = i.data[2]/n
                else:
                    i.reload("reg")
                    r += i.data[0]/n
                    g += i.data[1]/n
                    b += i.data[2]/n
                print(i.data[0])
                i.release()
            newdata = [r, g, b]
        
        else:
            for i in batch.list:
                
                if i.number == 0:               # do this so ref gets first
                    print("Reference image")
                    print(i.data)
                    r = i.data/n
                    print("Divided")
                    print(r)
                else:
                    print("adding")
                    r += i.data/n
                    print("got")
                    print(r)
                del i.data
                del i.image
                
            newdata = r
            
        if batch.type == "light":
            batch.savefinal(newdata)
        else:
            batch.savemaster(newdata)
        
    def subtract(self, batch, calib):
        """
        Calculates batch = batch - calib. Required for calibrating lights and flats
        """
        
        for i in batch.list:
            i.data = i.data - calib.data
            i.data.clip(0)
            i.write()
            #i.hdu.flush()
    
    def clip(self, batch):
        """
        Clip negative values replacing them by 0
        """
        batch.master.data = batch.master.data.clip(0)
        batch.master.write()
    
    def normalize(self, calib):
        """
        Normalizes calib by maximum value for divide operation.
        """
        calib.data = calib.data / np.amax(calib.data)
        #calib.write()
        
    
    def divide(self, batch, calib):
        """
        Calculates batch = batch / calib.

        Required for dividing light with normalized flat.
        """
        for i in batch.list:
            i.data = i.data / calib.data
            i.data = np.nan_to_num(i.data)
            i.write()
                
        