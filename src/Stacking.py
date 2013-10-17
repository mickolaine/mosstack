#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.10.2013

@author: Mikko Laine

This file contains everything required for stacking the photos.
'''

import Image
import numpy as np

class Mean:
    '''
    Mean stacking should be easiest to implement, so I'll start with that.
    
    Each pixel will be a median value of the entire stack. Default for stacking bias, flat and dark.
    '''
    
    def __init__(self):
        pass
    
    def stack(self, batch):
        '''
        Stacks the batch using mean value for every subpixel of every colour
        '''
        
        
        n = len(batch.list)

        
        for i in batch.list:
            
            if i.number == 0:
                newdata = i.data/n
            else:
                newdata = newdata + i.data/n
            
            """
            if i.number == 0:               #do this so ref gets first
                r = i.data[0]/n
                g = i.data[1]/n
                b = i.data[2]/n
            else:
                r = r + i.data[0]/n
                g = g + i.data[1]/n
                b = b + i.data[2]/n
            print(i.data[0])
            
        newdata = [r, g, b]
        """
        batch.savemaster(newdata)
        
    def subtract(self, batch, calib):
        '''
        Calculates batch = batch - calib. Required for calibrating lights and flats
        '''
        
        for i in batch.list:
            if len(i.data) == 3:
                for d in range(3):
                    i.data[d] = i.data[d] - calib.data[d]
            else:
                i.data = i.data - calib.data
            i.write()
            #i.hdu.flush()
    
    def normalize(self, calib):
        '''
        Normalizes calib for divide operation. Assumes 65535 is the largest value. Check this. It might be half of that depending how the transformation was done.
        '''
        for d in range(3):
            calib.data[d] = calib.data[d] / 65535.
        calib.hdu.flush()
        
    
    def divide(self, batch, calib):
        '''
        Calculates batch = batch / calib. Required for dividing light with normalized flat
        Result may have bigger values than 65535 and that creates problems with current affine transform. Normalizing to max 65535.
        '''
        for i in batch.list:
            for d in range(3):
                i.data[d] = i.data[d] / calib.data[d]
                maximum = np.amax(i.data[d])
                if maximum > 65535:
                    i.data[d] = i.data[d] /maximum * 65535
                i.hdu.flush()
                
        