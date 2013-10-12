#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 25.9.2013

@author: micko

This is a main program intended for testing the classes and functions. My intention is to write a GUI
when the core functionality works well enough.
'''

from astropy.io import fits
import numpy
from subprocess import check_output
import Registering
import Image
import Stacking
import conf

"""
    
    def median(self):
        '''
        Calculate median of a stack. Does Sum_i P_i /n for each colour, and each x,y, where P is pixel and n is number of images. 
        '''
        n = float(len(self.list))
        i = 0
        
        for image in self.list:
            self.new += image[0].data
            print(i)
            i += 1
        
        self.new = self.new / n
        print(self.new)
"""           


if __name__ == '__main__':
    
    R = Registering.Reg()
    S = Stacking.Median()
    light = Image.Batch(type = "light", name = "Andromeda")
    for i in conf.rawlist:
        light.add(conf.rawprefix + i)
    
    temp = Registering.Sextractor(light.list[0])
    sensitivity = temp.findSensitivity()
    del temp
    
    for i in light.list:
        s = Registering.Sextractor(i)
        s.setSensitivity(sensitivity[0], sensitivity[1])
        i.coordinates = s.getCoordinates()
        s.makeTriangles()
    
    for i in light.list:
        R.step1(i)                      # Step1 has to be finished before the rest
    
    ref = 0
    light.setRef(ref)
      
    for i in light.list:
        if i.number == light.refnum:       # No need to match image with itself
            continue

        R.match(light.refimg(), i)
        R.reduce(i)
        R.vote(i)
        R.transform(i)
        i.save()                        # Saves registered image on disc so it won't be clogging the memory
    
    
    S.stack(light)
    
        
        