#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2.10.2013

@author: Mikko Laine
'''

from astropy.io import fits
from os.path import splitext,basename,exists
from subprocess import call,check_output
import conf
import Registering
import numpy as np
from PIL import Image as Im

class Image(object):
    '''
    classdocs
    '''

    def __init__(self, rawpath = None, number = None, type = "light"):
        '''
        Constructor requires a filename of a raw image. I have a Canon EOS 1100D so Canon CR2 is what I originally write this for.
        #TODO: Support for other raws
        '''
        
        if rawpath == None:         # If no path given, create an empty image object
            pass
        
        else:
            self.rawpath   = rawpath     # Path for raw image
            self.name      = type        # For now I'll use type of the image as name for temp files
            self.number    = number      # Number to identify the image           
            self.imagename = conf.path + self.name + str(self.number)       # Path for converted image. No extension included
            self.tri       = []          # List for triangles
            self.match     = []          # List for matching triangles with reference picture
            self.format    = "tiff"      # Support is only for one format (for now) but I use this variable while writing the new code for tiff
            self.imagepath = self.imagename + self.format
            
            self.convert(format = self.format)
            
            if self.format == "fits":
                self.hdu      = fits.open(self.imagepath, mode="update")
                self.image    = self.hdu[0]
                self.data     = self.image.data
                self.x        = self.image.shape[2]
                self.y        = self.image.shape[1]
                
            elif self.format == "tiff":
                self.image    = Im.open(self.imagepath)
                call(["convert", self.imagepath, self.imagename + ".fits"])
                self.data     = np.array(self.image)
                self.x        = self.image.size[0]
                self.y        = self.image.size[1]
            
            print(self.name + str(self.number) + " - X: " + str(self.x) + ", Y: " + str(self.y)) # + ", Orientation from EXIF: " + str(self.orientation))
        
        
    def isOK(self, image):
        '''
        Test whether astropy recognizes the image. Not used yet. Probably should
        '''
        
        if image.is_image:
            return True
    
    def convert(self, format = "fits"):
        '''
        Converts the raw into a format this program can use. Originally it was FITS but after running in problems with rawtran I chose TIFF.
        Eventually there might be several formats...
        '''
        
        # Originally I used fits. Changing code to use tiff as default format. Python Imaging library Pillow
        # could be used to replace both AstroPy and scikit-image. Perhaps even SciPy.
        if format == "fits":
            self.imagepath = conf.path + self.name + str(self.number) + ".fits"
            if exists(self.rawpath):
                if exists(self.imagepath):                   # Don't convert raws again
                    pass
                elif call(["rawtran -X '-t 0' -o " + self.imagepath + " " + self.rawpath], shell=True):
                    print("Something went wrong... There might be helpful output from Rawtran above this line.")
                    print("File " + self.rawpath + " exists.")
                    if exists(self.imagepath):
                        print("File " + self.imagepath + " exists.")
                        print("Here's information about it:")
                        #TODO: Check size and magic numbers with file utility
                    else:
                        print("File " + self.imagepath + " does not. Unable to continue.")
                        exit() #TODO: Make it able to continue without this picture
            else:
                print("Unable to find file in given path: " + self.rawpath + ". Find out what's wrong and try again.")
                print("Can't continue. Exiting.")
                exit()
                
        # TIFF               
        elif format == "tiff":
            self.imagepath = conf.path + self.name + str(self.number) + ".tiff"
            if exists(self.rawpath):
                if exists(self.imagepath):                   # Don't convert raws again
                    pass
                elif call(["dcraw -T -4 -t 0 -D " + self.rawpath], shell=True):
                    print("Something went wrong... There might be helpful output from DCRaw above this line.")
                    print("File " + self.rawpath + " exists.")
                    if exists(self.imagepath):
                        print("File " + self.imagepath + " exists.")
                        print("Here's information about it:")
                        #TODO: Check size and magic numbers with file utility
                    else:
                        print("File " + self.imagepath + " does not. Unable to continue.")
                        exit() #TODO: Make it able to continue without this picture
                else:
                    origtiff = splitext(self.rawpath)[0] + ".tiff"
                    newtiff  = conf.path + self.name + str(self.number) + ".tiff"
                    print("Moving file " + origtiff + " to " + newtiff)
                    call(["mv", origtiff, newtiff])
                
            else:
                print("Unable to find file in given path: " + self.rawpath + ". Find out what's wrong and try again.")
                print("Can't continue. Exiting.")
                exit()


    def newdata(self, data):
        '''
        Saves new data
        '''
        
        self.data = np.array(data, dtype=np.int16)

        
        
        
    def writenew(self, name):
        '''
        Writes new data to Fits
        '''
        rpath = conf.path + name + "RED.fits"
        gpath = conf.path + name + "GREEN.fits"
        bpath = conf.path + name + "BLUE.fits"
        path  = conf.path + name + ".fits"
        
        datar = np.array(self.data[0], dtype=np.int16)
        datag = np.array(self.data[1], dtype=np.int16)
        datab = np.array(self.data[2], dtype=np.int16)
        
        data = np.array(self.data, dtype=np.int16)
        
        hdu = fits.PrimaryHDU()          # To create a default header
        
        fits.writeto(rpath, datar, hdu.header)
        fits.writeto(gpath, datag, hdu.header)
        fits.writeto(bpath, datab, hdu.header)
        fits.writeto( path, data , hdu.header)
        
        self.imagepath = path
        self.hdu      = fits.open(self.imagepath, mode = "update")
        self.image    = self.hdu[0]
        self.data     = self.image.data
    
    def save(self, name = "reg"):
        '''
        Saves newdata into fits and loads that as self.hdu, self.image, self.data
        '''
        
        self.name     = name
        regpath       = conf.path + self.name + str(self.number) + ".fits"
        #data          = np.array([self.r, self.g, self.b], dtype=np.uint16)
        
        
        fits.writeto(regpath, self.data, fits.getheader(self.imagepath))
        
        #del self.r          # Release memory
        #del self.g
        #del self.b

        self.imagepath = regpath
        self.hdu       = fits.open(self.imagepath)
        self.image     = self.hdu[0]
        self.data      = self.image.data
        
    def write(self):
        '''
        Replaces self.save and self.writenew and probably some more. Works for TIFF files
        '''
        
        self.image = Im.fromarray(self.data)
        self.image.save(self.imagepath, format="tiff")
        
    
    
class Batch:
    '''
    Batch holds a list of photos loaded with astropy's fits.open
    It also checks compatibility for each photo loaded
    #TODO: For now math is also here, but I'll probably move it elsewhere later
    '''

    def __init__(self, type = None, name = None):
        '''
        Constructor loads all necessary objects and sets some default values
        list will have Image.Image type objects which will hold all the information of one image.
        '''
        self.type   = type                # Define type of batch. Possibilities are light, flat, bias and dark 
        self.list   = []                  # Empty list for Images
        self.refnum = None                # list index where the reference image can be found
        self.name   = name                # Name for the resulting image
        
        self.master = Image()       # New empty image to save the result in
                    
    def add(self, rawpath):
        '''
        Add a photo to the batch. Maybe run some checks while at it.
        '''
        
        number = len(self.list)         # Define index number for images
        i = Image(rawpath, number, type = self.type)   
                
        self.list.append(i)
        
    def setRef(self, ref):
        '''
        Set image in list[ref] as the reference image. Required only for lights
        '''
        self.refnum = ref
    
    
    def refimg(self):
        '''
        Returns the reference image
        '''
        return self.list[self.refnum]

    def savemaster(self, data):
        '''
        Saves the result image. Might be a good idea to release memory while here...
        '''

        self.master.newdata(data)
        self.master.writenew(self.name)
        
        del self.list            # Master image or result has been saved. No need for the list anymore. Releasing memory

