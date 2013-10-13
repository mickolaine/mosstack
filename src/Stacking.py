#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.10.2013

@author: Mikko Laine

This file contains everything required for stacking the photos.
'''

import Image

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
        
        n = len(batch.list)                 # -1 because I don't handle the reference image yet
        
        r = 0.
        b = 0.
        g = 0.
        
        for i in batch.list:
            if i.number != 0:
                r = r + i.data[0]
                g = g + i.data[1]
                b = b + i.data[2]
            
        r = r/n
        b = b/n
        g = g/n
        
        new = Image.Image()
        new.newdata(r, g, b)
        new.writeNew(batch.name)
