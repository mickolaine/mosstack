#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 2.10.2013

@author: Mikko Laine
"""

from astropy.io import fits
from os.path import splitext, exists, split
from subprocess import call
import Conf
import numpy as np
from PIL import Image as Im


class Photo(object):
    """
    Class holds loading and saving photo files and converting photo to numpy.array
    """

    # format for intermediate files. TODO: Make this unnecessary
    format = "fits"

    def __init__(self, rawpath=None, number=None, name=None, itype="light"):
        """
        Constructor requires a filename of a raw image. I have a Canon EOS 1100D so Canon CR2 is what I originally
        write this for.
        # TODO: Support for other raws

        Arguments:
        rawpath = path where original raw image can be found
        number  = number to identify the image, perhaps not required anymore since this is also in Conf
        itype   = type for the image: light, bias, dark, flat
        """

        if rawpath is None:              # If no path given, create an empty image object
            self.number = None
            return
        
        self.rawformat = splitext(rawpath)[1][1:]

        self.rawpath   = rawpath     # Path for raw image
        self.name      = name        # For now I'll use type of the image as name for temp files
        self.number    = number      # Number to identify the image
        self.itype     = itype
        self.imagename = Conf.path + self.name + "_" + self.itype + str(self.number)  # Path for image. No extension
        self.tri       = []          # List of triangles
        self.match     = []          # List of matching triangles with reference picture
        self.imagepath = self.imagename + "." + self.format
        self.fitspath  = self.imagename + ".fits"

        # If raw file is fits, just copy it to working directory (if not already there) and open
        if self.rawformat == "fits":
            print(self.rawpath)
            if split(self.rawpath)[0] + "/" != Conf.path:
                call(["cp", self.rawpath, self.imagepath])
            else:
                self.imagepath = self.rawpath

        else:
            self.convert(iformat="fits")    # TODO: Remove iformat argument as soon as done with
                                            # removing tiff as intermediate file

        self.hdu       = fits.open(self.imagepath)
        self.image     = self.hdu[0]
        self.data      = self.image.data
        self.x         = self.image.shape[1]
        self.y         = self.image.shape[0]

        # TODO: Remove this when ready with tiffs
        #elif self.format == "tiff":
        #    self.image    = Im.open(self.imagepath)
        #    #call(["convert", self.imagepath, self.imagename + ".fits"])
        #    if itype == "light":
        #        call(["rawtran -X '-t 0' -o " + self.fitspath + " " + self.rawpath], shell=True)
        #    self.data     = np.array(self.image, np.float32)
        #    self.x        = self.image.size[0]
        #    self.y        = self.image.size[1]

        print(self.name + str(self.number) + " - X: " + str(self.x) + ", Y: " + str(self.y))

    def convert(self, iformat="fits"):
        """
        Convert the raw into FITS

        TODO: Remove iformat argument when sure it won't be needed
        """

        if iformat == "fits":
            #self.imagepath = Conf.path + self.name + str(self.number) + ".fits"
            if exists(self.rawpath):
                if exists(self.imagepath):                   # Don't convert raws again
                    pass
                elif call(["rawtran -X '-t 0' -c u -o " + self.imagepath + " " + self.rawpath], shell=True):
                    print("Something went wrong... There might be helpful output from Rawtran above this line.")
                    print("File " + self.rawpath + " exists.")
                    if exists(self.imagepath):
                        print("File " + self.imagepath + " exists.")
                        print("Here's information about it:")
                        # TODO: Check size and magic numbers with file utility
                    else:
                        print("File " + self.imagepath + " does not. Unable to continue.")
                        exit()  # TODO: Make it able to continue without this picture
            else:
                print("Unable to find file in given path: " + self.rawpath + ". Find out what's wrong and try again.")
                print("Can't continue. Exiting.")
                exit()
                
        # TIFF      TODO: Remove this when done with tiff
        #elif iformat == "tiff":
        #    self.imagepath = Conf.path + self.name + str(self.number) + ".tiff"
        #    if exists(self.rawpath):
        #        if exists(self.imagepath):                   # Don't convert raws again
        #            pass
        #        elif call(["dcraw -T -4 -t 0 -D " + self.rawpath], shell=True):
        #            print("Something went wrong... There might be helpful output from DCRaw above this line.")
        #            print("File " + self.rawpath + " exists.")
        #            if exists(self.imagepath):
        #                print("File " + self.imagepath + " exists.")
        #                print("Here's information about it:")
        #                # TODO: Check size and magic numbers with file utility
        #            else:
        #                print("File " + self.imagepath + " does not. Unable to continue.")
        #                exit()  # TODO: Make it able to continue without this picture
        #        else:
        #            origtiff = splitext(self.rawpath)[0] + ".tiff"
        #            newtiff  = Conf.path + self.name + str(self.number) + ".tiff"       # TODO: Change this to shutil
        #            print("Moving file " + origtiff + " to " + newtiff)
        #            call(["mv", origtiff, newtiff])
        #
        #    else:
        #        print("Unable to find file in given path: " + self.rawpath + ". Find out what's wrong and try again.")
        #        print("Can't continue. Exiting.")
        #        exit()

    def newdata(self, data):
        """
        Saves new data
        """
        
        self.data = np.float32(np.array(data))

    def savergb(self, data):
        """
        Saves new data
        """
        
        self.rgbdata = np.array(data)  
        
        #self.rgbpath = conf.path + "rgb" + str(self.number) + ".tiff"
        
        #self.imagepath = self.rgbpath
        
        self.redpath = Conf.path + "red" + str(self.number) + ".tiff"
        self.bluepath = Conf.path + "blue" + str(self.number) + ".tiff"
        self.greenpath = Conf.path + "green" + str(self.number) + ".tiff"
        
        self.imager   = Im.fromarray(np.int16(self.rgbdata[0]))
        self.imager.save(self.redpath, format="tiff")
        del self.imager
        
        self.imageg   = Im.fromarray(np.int16(self.rgbdata[1]))
        self.imageg.save(self.bluepath, format="tiff")
        del self.imageg
        
        self.imageb   = Im.fromarray(np.int16(self.rgbdata[1]))
        self.imageb.save(self.greenpath, format="tiff")
        del self.imageb        
        
        #call(["convert", redpath, greenpath, bluepath, "-colorspace", "RGB", \
        # "-channel", "RGB", "-combine", self.rgbpath])
        #call(["rm", redpath, greenpath, bluepath])
        
        del self.image
        #self.data     = [np.array(self.imager), np.array(self.imageg), np.array(self.imageb)]
        #This probably should be loaded when needed
    
    def savefinal(self, data, name):
        """
        Saves new data
        """
        # Monochrome data
        if data.ndim == 2:
            newpath = Conf.path + name + "_final.tiff"
            print(np.amax(data))
            image   = Im.fromarray(np.int16(data))
            image.save(newpath, format="tiff")

        # RGB data
        elif data.ndim == 3:

            self.rgbdata = np.array(data)

            redpath = Conf.path + name + "_red.tiff"
            bluepath = Conf.path + name + "_blue.tiff"
            greenpath = Conf.path + name + "_green.tiff"

            imager   = Im.fromarray(np.int16(data[0]))
            imager.save(redpath, format="tiff")

            imageg   = Im.fromarray(np.int16(data[1]))
            imageg.save(bluepath, format="tiff")

            imageb   = Im.fromarray(np.int16(data[1]))
            imageb.save(greenpath, format="tiff")
        
    """   
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
        #data          = np.array([self.r, self.g, self.b], dtype=np.int16)
        
        
        fits.writeto(regpath, self.data, fits.getheader(self.imagepath))
        
        #del self.r          # Release memory
        #del self.g
        #del self.b

        self.imagepath = regpath
        self.hdu       = fits.open(self.imagepath)
        self.image     = self.hdu[0]
        self.data      = self.image.data
    """
        
    def write(self):
        """
        Replaces self.save and self.writenew and probably some more. Works for TIFF files
        """
        if self.format == "tiff":
            self.image = Im.fromarray(np.float32(self.data))
            self.image.save(self.imagepath, format="tiff")
        if self.format == "fits":
            hdu = fits.PrimaryHDU()                 # To create a default header
            fits.writeto(self.imagepath, self.data, hdu.header)
        
    def reload(self, name, ref = 0):
        """
        Loads self.image from name
        """
        if ref == 1:
            self.redpath   = Conf.path + "red" + str(self.number) + ".tiff"
            self.greenpath = Conf.path + "green" + str(self.number) + ".tiff"
            self.bluepath  = Conf.path + "blue" + str(self.number) + ".tiff"
        else:
            self.redpath   = Conf.path + name + str(self.number) + "red.tiff"
            self.greenpath = Conf.path + name + str(self.number) + "green.tiff"
            self.bluepath  = Conf.path + name + str(self.number) + "blue.tiff"
        print("Opening file in " + self.imagepath)
        self.imager     = Im.open(self.redpath)
        self.imageg     = Im.open(self.greenpath)
        self.imageb     = Im.open(self.bluepath)
        self.data      = [np.array(self.imager),np.array(self.imageg),np.array(self.imageb)]
        #print(self.data)
        self.x         = self.imager.size[0]
        self.y         = self.imager.size[1]

    def setname(self, name):
        """
        Set name for the empty image.
        """
        if self.number is None:
            self.imagepath = Conf.path + name + "." + self.format
        else:
            self.imagepath = Conf.path + name + str(self.number) + "." + self.format
            
    def release(self):
        """
        Release not needed images from memory
        """
        try:
            del self.imager
            del self.imageg
            del self.imageb
        except AttributeError:
            del self.image
        del self.data
        
    
class Batch:
    """
    Batch holds a list of photos loaded with astropy's fits.open
    It also checks compatibility for each photo loaded
    #TODO: For now math is also here, but I'll probably move it elsewhere later
    """

    def __init__(self, itype=None, name=None, project=None):
        """
        Constructor loads all necessary objects and sets some default values
        list will have Photo.Photo type objects which will hold all the information of one image.
        """
        self.itype  = itype               # Define type of batch. Possibilities are light, flat, bias and dark
        self.list   = []                  # Empty list for Images
        self.refnum = None                # list index where the reference image can be found
        self.name   = name                # Name for the resulting image

        if project is not None:
            self.project = project
        self.master = Photo()             # New empty image to save the result in
                    
    def add(self, rawpath):
        """
        Add a photo to the batch. Maybe run some checks while at it.
        """
        
        number = len(self.list)         # Define index number for images
        i = Photo(rawpath, number, itype=self.itype, name=self.name)
                
        self.list.append(i)
        
    def setref(self, ref):
        """
        Set image in list[ref] as the reference image. Required only for lights
        """
        self.refnum = ref

    def refimg(self):
        """
        Returns the reference image
        """
        return self.list[self.refnum]

    def savemaster(self, data):
        """
        Saves the result image. Might be a good idea to release memory while here...
        """
        
        self.master.newdata(data)
        self.master.setname(self.name)
        self.master.write()

        self.project.conf.save(self.itype, self.master.imagepath, "Master frames")
        
        del self.list            # Master image or result has been saved. No need for the list anymore. Releasing memory
        
    def savefinal(self, data):
        
        self.master.savefinal(data, self.name)

    def demosaic(self, demosaic):
        """
        Demosaic CFA-image into RGB.

        This resides in Batch because this class will handle all the writing
        in Conf

        Arguments
        demosaic: a Demosaic-type object
        """

        for i in self.list:
            demosaic.bilinear_cl(i)