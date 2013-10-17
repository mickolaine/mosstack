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
import numpy
from PIL import Image

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
            self.rawpath  = rawpath
            self.number   = number
            self.tri      = []          # List for triangles
            self.match    = []          # List for matching triangles with reference picture
            self.name     = type        # For now I'll use type of the image as name for temp files
            
            self.convert(format = "fits")
            
            self.hdu      = fits.open(self.fitspath, mode="update")
            self.image    = self.hdu[0]
            self.data     = self.image.data
            
            # Get the shape of image and the EXIF orientation. These are required to check the rotation of photos.
            # Mainly for dark, bias and flat, but might be handy with lights as well.

            #self.orientation = int(check_output(["exiftool", "-Orientation", "-n", "-T", rawpath]).strip())     # TODO: Probably not needed anymore
            #self.rotate()
            self.x = self.image.shape[2]
            self.y = self.image.shape[1]
            
            print(self.name + str(self.number) + " - X: " + str(self.x) + ", Y: " + str(self.y)) # + ", Orientation from EXIF: " + str(self.orientation))
        
        
    def isOK(self, image):
        '''
        Test whether astropy recognizes the image. Not used yet. Probably should
        '''
        
        if image.is_image:
            return True
    
    def convert(self, format = "fits"):
        '''
        Converts the raw into fits.
        '''
        
        # Originally I used fits. Changing code to use tiff as default format. Python Imaging library Pillow
        # could be used to replace both AstroPy and scikit-image. Perhaps even SciPy.
        if format == "fits":
            self.fitspath = conf.path + self.name + str(self.number) + ".fits"
            if exists(self.rawpath):
                if exists(self.fitspath):                   # Don't convert raws again
                    pass
                elif call(["rawtran -X '-t 0' -o " + self.fitspath + " " + self.rawpath], shell=True):
                    print("Something went wrong... There might be helpful output from Rawtran above this line.")
                    print("File " + self.rawpath + " exists.")
                    if exists(self.fitspath):
                        print("File " + self.fitspath + " exists.")
                        print("Here's information about it:")
                        #TODO: Check size and magic numbers with file utility
                    else:
                        print("File " + self.fitspath + " does not. Unable to continue.")
                        exit() #TODO: Make it able to continue without this picture
            else:
                print("Unable to find file in given path: " + self.rawpath + ". Find out what's wrong and try again.")
                print("Can't continue. Exiting.")
                exit()
                
        # Support for tiff not working yet. Do not try                
        elif format == "tiff":
            pass


    def newdata(self, data):
        '''
        Saves new data
        '''
        
        self.data = numpy.array(data, dtype=numpy.int16)

        
        
        
    def writenew(self, name):
        '''
        Writes new data to Fits
        '''
        rpath = conf.path + name + "RED.fits"
        gpath = conf.path + name + "GREEN.fits"
        bpath = conf.path + name + "BLUE.fits"
        path  = conf.path + name + ".fits"
        
        datar = numpy.array(self.data[0], dtype=numpy.int16)
        datag = numpy.array(self.data[1], dtype=numpy.int16)
        datab = numpy.array(self.data[2], dtype=numpy.int16)
        
        data = numpy.array(self.data, dtype=numpy.int16)
        
        hdu = fits.PrimaryHDU()          # To create a default header
        
        fits.writeto(rpath, datar, hdu.header)
        fits.writeto(gpath, datag, hdu.header)
        fits.writeto(bpath, datab, hdu.header)
        fits.writeto( path, data , hdu.header)
        
        self.fitspath = path
        self.hdu      = fits.open(self.fitspath, mode = "update")
        self.image    = self.hdu[0]
        self.data     = self.image.data
                
    def save(self):
        '''
        Saves newdata into fits and loads that as self.hdu, self.image, self.data
        '''
        
        self.name     = "reg"
        regpath       = conf.path + "reg" + str(self.number) + ".fits"
        #data          = numpy.array([self.r, self.g, self.b], dtype=numpy.uint16)
        
        
        fits.writeto(regpath, self.data, fits.getheader(self.fitspath))
        
        #del self.r          # Release memory
        #del self.g
        #del self.b

        self.fitspath = regpath
        self.hdu      = fits.open(self.fitspath)
        self.image    = self.hdu[0]
        self.data     = self.image.data
        
        
    
    
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

