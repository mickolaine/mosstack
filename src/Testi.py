#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 25.9.2013

@author: micko

Testilisäys. Miten gitti toimii <--- Nevermind this
'''

from astropy.io import fits
import numpy
from subprocess import check_output
import Registering
import Image
import Stacking
import conf

"""
class Batch:
    '''
    Batch holds a list of photos loaded with astropy's fits.open
    It also checks compatibility for each photo loaded
    #TODO: For now math is also here, but I'll probably move it elsewhere later
    '''

    def __init__(self):
        '''
        Constructor loads all necessary objects and sets some default values
        list will have Image.Image type objects which will hold all the information of one image.
        '''
        
        self.list = []
        self.x    = None
        self.y    = None
        self.reg  = Registering.Reg()
    
                    
    def add(self, filename):
        '''
        Add a photo to the batch. Add() checks if the photo is of a same size and shape than the original. Not necessary for light frames
        so I'll probably make that optional.
        If photo checks ok, it will be added to batch
        #TODO: Make this accept raw images and transform them to fits
        '''
        
        hdu = fits.open(filename)
        image = hdu[0]
        
            
        # If no images on batch yet, set shape and orientation with the first one given
        if self.x is None:
            self.x = image.shape[2]
            self.y = image.shape[1]
            self.orientation = int(check_output(["exiftool", "-Orientation", "-n", "-T", filename]).strip())
        
        # For the rest, check if they match with the first one. If not, try to fix #TODO: This should probably be done with try-except structure    
        elif (self.x != image.shape[2]) | (self.y != image.shape[1]):
            print("Images have different shape.\nFirst one in batch was " + str(self.x) + " x " + str(self.y))
            print("Current one is " + str(image.shape[2]) + " x " + str(image.shape[1]))
            
            # If shape is correct but differs 90 deg, try to rotate
            if (self.x == image.shape[1]) & (self.y == image.shape[2]):
                print("Attempting to rotate...")
                o = check_output(["exiftool", "-Orientation", "-n", "-T", filename])
                    
                    
        
        
        self.list.append(fits.open(filename))
        
       
    def formatNew(self, x, y):
        '''
        Format a new empty numpy.array for the imagestack
        '''
        
        self.new = numpy.array(numpy.zeros((3, x, y)), ndmin=3, dtype=float)

    
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

""" VANHA
if __name__ == '__main__':
    root  = "/media/data/Temp/iris/"
    
    light = Batch()
    bias  = Batch()
    flat  = Batch()
    dark  = Batch()
    
 
    lightn = root + "andromeda"
    biasn  = root + "bias"
    flatn  = root + "flat"
    darkn  = root + "dark"
    for i in range(1,32):
        light.add(lightn + str(i) + ".fits")
        print("Added " + lightn + str(i) + ".fits")
        
    for i in range(1,31):
        bias.add( biasn  + str(i) + ".fits")
        #print("Added " + biasn + str(i) + ".fits, dimensions X = " + str(len(bias.list[i-1][0].data[0])) + ", Y = " + str(len(bias.list[i-1][0].data[0][0])))


    biasDim = [len(bias.list[0][0].data[0]), len(bias.list[0][0].data[0][0])]
    print(str(biasDim))
    bias.formatNew(biasDim[0], biasDim[1])
    bias.median()
        
    for i in range(1,11):
        dark.add( darkn  + str(i) + ".fits")
        print("Added " + darkn + str(i) + ".fits")
    darkDim = [len(dark.list[0][0].data[0]), len(dark.list[0][0].data[0][0])]
    dark.formatNew(darkDim[0], darkDim[1])
    dark.median()
        
    for i in range(1,8):
        flat.add( flatn  + str(i) + ".fits")
        print("Added " + flatn + str(i) + ".fits")
    flatDim = [len(flat.list[0][0].data[0]), len(flat.list[0][0].data[0][0])]
    flat.formatNew(flatDim[0], flatDim[1])
    flat.median()
    
    dark.new = dark.new - bias.new
    flat.new = flat.new - bias.new
    
    print(dark.new)
    print(flat.new)
    
    input("Press any key to end program.")
"""

if __name__ == '__main__':
    
    R = Registering.Reg()
    S = Stacking.Median()
    light = Image.Batch(type = "light")
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
        R.step1(i)
        
    for i in light.list:
        if i.number == 0:       # 0 is the reference image. No need to match image with itself
            continue
        print("Starting to match image " + str(i.number) + " to reference image " + str(0))
        R.match(light.list[0], i)
        R.reduce(i)
        R.vote(i)
        #t, r = R.affineTransform(i)
        #print(R.transformMatrix(i))
        
        R.transform(i)
    S.stack(light)
        
        #print(str(t))
        #print(str(r))
    
    #print(light.list[0].tri)
    #input("Press Enter to end program.")
        
        