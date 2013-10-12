#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 11.10.2013

@author: Mikko Laine

This file contains everything required for stacking the photos.
'''

class Median:
    '''
    Median stacking should be easiest to implement, so I'll start with that.
    
    Each pixel will be a median value of the entire stack. Default for stacking bias, flat and dark.
    '''
    
    def __init__(self):
        pass
    
    def stack(self, batch):
        '''
        Stacks the batch using median value for every subpixel of every colour
        '''
        
        n = len(batch.list) -1               # -1 because I don't handle the reference image yet
        
        r = 0.
        b = 0.
        g = 0.
        
        for i in batch.list:
            if i.number != 0:
                r = r + i.r/n
                g = g + i.g/n
                b = b + i.b/n
            
        batch.list[0].newdata(r,g,b)         # Use reference image to write 
        batch.list[0].writeNew()