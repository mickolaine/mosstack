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
import Demosaic
import conf
import gc


if __name__ == '__main__':
    
    R = Registering.Reg()
    S = Stacking.Mean()
    D = Demosaic.demosaic()

    
    print("Processing bias/offset images...")
    bias  = Image.Batch(type = "bias", name = "masterbias")
    for i in conf.biaslist:
        bias.add(conf.biasprefix + i)
    S.stack(bias)
    print("Processing bias/offset images done.")
    gc.collect()
    
    print("Processing dark images...")   
    dark  = Image.Batch(type = "dark", name = "masterdark")
    for i in conf.darklist:
        dark.add(conf.darkprefix + i)
    S.subtract(dark, bias.master)
    S.stack(dark)
    print("Processing dark images done.")
    gc.collect()
    
    
    print("Processing flat images...")
    flat  = Image.Batch(type = "flat", name = "masterflat")
    for i in conf.flatlist:
        flat.add(conf.flatprefix + i)
    #S.subtract(flat, dark.master)
    S.subtract(flat, bias.master)
    S.stack(flat)
    S.normalize(flat.master)
    print("Processing flat images done.")
    gc.collect()
    
    
    light = Image.Batch(type = "light", name = "Andromeda")
    for i in conf.rawlist:
        light.add(conf.rawprefix + i)
    gc.collect()
    #S.subtract(light, bias.master)
    
    
    #S.subtract(light, dark.master)
    S.divide(light, flat.master)
    
    for i in light.list:            # TODO: Change this so that D takes batches
        D.bilinear_cl(i)
    del D
    gc.collect()
    R.register(light)
    gc.collect()
    S.stack(light)
    
    """
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
    """

    
        
        