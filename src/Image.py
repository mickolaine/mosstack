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

class Image(object):
    '''
    classdocs
    '''

    def __init__(self, rawpath, number):
        '''
        Constructor requires a filename of a raw image. I have a Canon EOS 1100D so Canon CR2 is what I originally write this for.
        #TODO: Support for other raws
        '''
        self.rawpath  = rawpath
        self.number   = number
        self.name     = "light"     # Here could be more than a generic name. This is required for temporary files. #TODO: Maybe get this from Batch somehow
        
        self.convert()
        
        self.hdu      = fits.open(self.fitspath)
        self.image    = self.hdu[0]
        
        # Get the shape of image and the EXIF orientation. These are required to check the rotation of photos.
        # Mainly for dark, bias and flat, but might be handy with lights as well.
        self.x = self.image.shape[2]
        self.y = self.image.shape[1]
        self.orientation = int(check_output(["exiftool", "-Orientation", "-n", "-T", rawpath]).strip())
        
        print(self.name + str(self.number) + " - X: " + str(self.x) + ", Y: " + str(self.y) + ", Orientation from EXIF: " + str(self.orientation))
        
        
    def isOK(self, image):
        '''
        Test whether astropy recognizes the image
        '''
        
        if image.is_image:
            return True
        
    def convert(self):
        '''
        Converts the raw into fits.
        '''
        
        self.fitspath = conf.path + self.name + str(self.number) + ".fits"
        if exists(self.rawpath):
            if call(["rawtran", "-o", self.fitspath, self.rawpath]):
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

    
    
    
    
    
    
class Batch:
    '''
    Batch holds a list of photos loaded with astropy's fits.open
    It also checks compatibility for each photo loaded
    #TODO: For now math is also here, but I'll probably move it elsewhere later
    '''

    def __init__(self, type = None):
        '''
        Constructor loads all necessary objects and sets some default values
        list will have Image.Image type objects which will hold all the information of one image.
        '''
        self.type = type                # Define type of batch. Possibilities are light, flat, bias and dark 
        self.list = []                  # Empty list for Images
        self.reg  = Registering.Reg()   # This might be required. Maybe not
    
                    
    def add(self, rawpath):
        '''
        Add a photo to the batch. Maybe run some checks while at it.
        '''
        
        number = len(self.list) + 1     # Define index number for images
        i = Image(rawpath, number)   
        
        '''
        # For the rest, check if they match with the first one. If not, try to fix #TODO: This should probably be done with try-except structure    
        if (self.x != image.shape[2]) | (self.y != image.shape[1]):
            print("Images have different shape.\nFirst one in batch was " + str(self.x) + " x " + str(self.y))
            print("Current one is " + str(image.shape[2]) + " x " + str(image.shape[1]))
            
            # If shape is correct but differs 90 deg, try to rotate
            if (self.x == image.shape[1]) & (self.y == image.shape[2]):
                print("Attempting to rotate...")
                o = check_output(["exiftool", "-Orientation", "-n", "-T", rawpath])
        '''
        
        self.list.append(i)
        
       
    def formatNew(self, x, y):
        '''
        Format a new empty numpy.array for the imagestack
        '''
        
        self.new = numpy.array(numpy.zeros((3, x, y)), ndmin=3, dtype=float)




