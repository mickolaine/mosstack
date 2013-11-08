#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 2.10.2013

@author: Mikko Laine
"""

from astropy.io import fits
from os.path import splitext, exists, split
from shutil import copyfile
from subprocess import call
import Conf
import numpy as np
from PIL import Image as Im
import gc


class Photo(object):
    """
    Class holds loading and saving photo files and converting photo to numpy.array
    """

    # format for intermediate files. TODO: Make this unnecessary
    format  = "fits"

    def __init__(self, section=None, number=None, project=None, data=None):
        """
        Constructor requires a filename of a raw image. I have a Canon EOS 1100D so Canon CR2 is what I originally
        write this for.
        # TODO: Support for other raws

        Arguments:
        section = Section in configuration. Essentially type of files.
        number  = Number to identify the image. Same as found in project file
        project = Conf.Project type object
        data    = Create Photo from numpy.array
        """

        # Common variables for any case
        self.project   = project
        self.tri       = np.array([])         # List of triangles
        self.match     = np.array([])         # List of matching triangles with reference picture
        self.name      = self.project.get("Default", "Project name")  # Name of project. Used to give name to temp files
        self.number    = number               # Number to identify the image
        self.wdir      = self.project.get("Setup", "Path")  # Working directory

        # Create image from data
        if data is not None:
            self.data = data
            return

        # Create empty image
        if (section is None) & (number is None) & (data is None):
            return

        self.srcpath   = self.project.get(section, number)  # Path for source file
        self.imagename = self.wdir + self.name
        self.imagepath = self.imagename + ".fits"

        if section in ("dark", "bias", "flat"):
            self.itype = section
        else:
            self.itype = "light"

        self.rawformat = splitext(self.srcpath)[1][1:]

        # For source files that are already FITS
        if self.rawformat == "fits":
            # If image source image resides outside wdir, copy it there
            if split(self.srcpath)[0] + "/" != self.wdir:
                copyfile(self.srcpath, self.imagepath)
            else:
                self.imagepath = self.srcpath

        # For everything else, try converting
        else:
            self.convert()

        # Check if demosaicing done and assume rgb-pictures
        if self.project.get("State", "Demosaic") == "1":
            self.red       = fits.open(self.srcpath + "_r.fits", memmap=True)
            self.green     = fits.open(self.srcpath + "_g.fits", memmap=True)
            self.blue      = fits.open(self.srcpath + "_b.fits", memmap=True)
            self.imager    = self.red[0]
            self.imageg    = self.green[0]
            self.imageb    = self.blue[0]
            self.data      = None

        else:
            self.hdu       = fits.open(self.imagepath, memmap=True)
            self.image     = self.hdu[0]
            self.data      = None

        self.x         = self.image.shape[1]
        self.y         = self.image.shape[0]

        print(self.name + str(self.number) + " - X: " + str(self.x) + ", Y: " + str(self.y))

    def load_data(self):
        """
        Load data into memory
        """
        if self.project.get("State", "Demosaic") == "1":
            self.data      = np.array([self.imager.data, self.imageg.data, self.imageb.data])
        else:
            self.data = self.image.data

    def release_data(self):
        """
        Release data from memory
        """
        self.data = None
        gc.collect()

    def convert(self):
        """
        Convert the raw into FITS
        """

        #self.imagepath = Conf.path + self.name + str(self.number) + ".fits"
        if exists(self.srcpath):
            if exists(self.imagepath):                   # Don't convert raws again
                pass
            elif call(["rawtran -X '-t 0' -c u -o " + self.imagepath + " " + self.srcpath], shell=True):
                print("Something went wrong... There might be helpful output from Rawtran above this line.")
                print("File " + self.srcpath + " exists.")
                if exists(self.imagepath):
                    print("File " + self.imagepath + " exists.")
                    print("Here's information about it:")
                    # TODO: Check size and magic numbers with file utility
                else:
                    print("File " + self.imagepath + " does not. Unable to continue.")
                    exit()  # TODO: Make it able to continue without this picture
        else:
            print("Unable to find file in given path: " + self.srcpath + ". Find out what's wrong and try again.")
            print("Can't continue. Exiting.")
            exit()

    #def newdata(self, data):
    #    """
    #    Saves new data
    #    """
    #
    #    self.data = np.float32(np.array(data))
    #
    #def savergb(self, data):
    #    """
    #    Saves new data
    #    """
    #
    #    self.rgbdata = np.array(data)
    #
    #    #self.rgbpath = conf.path + "rgb" + str(self.number) + ".tiff"
    #
    #    #self.imagepath = self.rgbpath
    #
    #    self.redpath = Conf.path + "red" + str(self.number) + ".tiff"
    #    self.bluepath = Conf.path + "blue" + str(self.number) + ".tiff"
    #    self.greenpath = Conf.path + "green" + str(self.number) + ".tiff"
    #
    #    self.imager   = Im.fromarray(np.int16(self.rgbdata[0]))
    #    self.imager.save(self.redpath, format="tiff")
    #    del self.imager
    #
    #    self.imageg   = Im.fromarray(np.int16(self.rgbdata[1]))
    #    self.imageg.save(self.bluepath, format="tiff")
    #    del self.imageg
    #
    #    self.imageb   = Im.fromarray(np.int16(self.rgbdata[1]))
    #    self.imageb.save(self.greenpath, format="tiff")
    #    del self.imageb
    #
    #    #call(["convert", redpath, greenpath, bluepath, "-colorspace", "RGB", \
    #    # "-channel", "RGB", "-combine", self.rgbpath])
    #    #call(["rm", redpath, greenpath, bluepath])
    #
    #    del self.image
    #    #self.data     = [np.array(self.imager), np.array(self.imageg), np.array(self.imageb)]
    #    #This probably should be loaded when needed

    def write(self, final=False):
        """
        Write the image on disk

        Arguments:
        final       = Define writing of final image.
        """
        if not final:
            if self.format == "tiff":
                self.image = Im.fromarray(np.float32(self.data))
                self.image.save(self.imagepath, format="tiff")
            if self.format == "fits":
                hdu = fits.PrimaryHDU()                 # To create a default header
                if self.data.ndim == 3:
                    fits.writeto(self.redpath, self.data[0], hdu.header)
                    fits.writeto(self.greenpath, self.data[1], hdu.header)
                    fits.writeto(self.bluepath, self.data[2], hdu.header)
                else:
                    fits.writeto(self.imagepath, self.data, hdu.header)
        else:
            # Monochrome data
            if self.data.ndim == 2:
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
        
    #def reload(self, name, ref=0):
    #    """
    #    Loads self.image from name
    #    """
    #    if ref == 1:
    #        self.redpath   = Conf.path + "red" + str(self.number) + ".tiff"
    #        self.greenpath = Conf.path + "green" + str(self.number) + ".tiff"
    #        self.bluepath  = Conf.path + "blue" + str(self.number) + ".tiff"
    #    else:
    #        self.redpath   = Conf.path + name + str(self.number) + "red.tiff"
    #        self.greenpath = Conf.path + name + str(self.number) + "green.tiff"
    #        self.bluepath  = Conf.path + name + str(self.number) + "blue.tiff"
    #    print("Opening file in " + self.imagepath)
    #    self.imager     = Im.open(self.redpath)
    #    self.imageg     = Im.open(self.greenpath)
    #    self.imageb     = Im.open(self.bluepath)
    #    self.data      = [np.array(self.imager),np.array(self.imageg),np.array(self.imageb)]
    #    #print(self.data)
    #    self.x         = self.imager.size[0]
    #    self.y         = self.imager.size[1]

    #def setname(self, name):
    #    """
    #    Set name for the empty image.
    #    """
    #    if self.number is None:
    #        self.imagename = Conf.path + self.name + "_" + name
    #        self.imagepath = self.imagename + ".fits"
    #        self.redpath   = self.imagename + "_red.fits"
    #        self.greenpath = self.imagename + "_green.fits"
    #        self.bluepath  = self.imagename + "_blue.fits"
    #    else:
    #        self.imagename = Conf.path + self.name + "_" + name + str(self.number)
    #        self.imagepath = self.imagename + ".fits"
    #        self.redpath   = self.imagename + "_red.fits"
    #        self.greenpath = self.imagename + "_green.fits"
    #        self.bluepath  = self.imagename + "_blue.fits"
            
    def release(self):
        """
        Release not needed images from memory
        """

        self.imager = None
        self.imageg = None
        self.imageb = None
        self.image = None
        gc.collect()
        self.data = None
        
    
class Batch:
    """
    Batch holds a list of photos loaded with astropy's fits.open
    It also checks compatibility for each photo loaded
    """

    def __init__(self, section=None, project=None):
        """
        Constructor loads all necessary objects and sets some default values
        list will have Photo.Photo type objects which will hold all the information of one image.

        Arguments:
        section = section of files in project file
        project = Project object
        """

        self.project = project
        files        = self.project.get(section)
        self.list    = {}                     # Empty list for Photos
        for key, value in files:
            photo = Photo(section=section, number=int(key), project=self.project)
            self.list[key] = photo

        if section in ("dark", "bias", "flat"):
            self.itype = section              # Define type of batch. Possibilities are light, flat, bias and dark
        else:
            self.itype = "light"

        self.refnum = int(project.get("Reference", key="self.itype"))  # Number of reference frame
        self.name   = self.project.get("Default", key="project name")  # Name for the resulting image

        self.master = Photo(project=project)  # New empty image to save the result in

    def add(self, rawpath):
        """   OBSOLETE      perhaps...
        Add a photo to the batch. Maybe run some checks while at it.
        """
        
        number = len(self.list)         # Define index number for images
        i = Photo(rawpath, number, itype=self.itype, name=self.name)
                
        self.list.append(i)

    def addrgb(self, redpath, greenpath, bluepath):
        """   OBSOLETE      perhaps...
        Add rgb channels from different files
        """

        number = len(self.list)         # Define index number for images
        red   = Photo(redpath,   number, itype=self.itype, name=self.name)
        green = Photo(greenpath, number, itype=self.itype, name=self.name)
        blue  = Photo(bluepath,  number, itype=self.itype, name=self.name)

        red.load_data()
        green.load_data()
        blue.load_data()

        new = Photo()
        new.newdata([red.data, green.data, blue.data])
        new.imagename = Conf.path + self.name
        new.imagepath = Conf.path + self.name + ".fits"
        new.greenpath = greenpath
        new.fitspath  = new.greenpath
        new.x         = red.x
        new.y         = red.y
        new.tri       = []          # List of triangles
        new.match     = []          # List of matching triangles with reference picture
        self.list.append(new)

    def setref(self, ref):
        """   OBSOLETE      perhaps...
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

        self.project.set(self.itype, self.master.imagepath, "Master frames")
        self.project.write()
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
            i.load_data()
            i.newdata(demosaic.bilinear_cl(i))
            i.setname("rgb")
            i.write()
            i.release_data()
            self.project.set(str(i.number), i.imagename, "RGB frames")
        self.project.set("Demosaic", "1", "State")
        self.project.write()

    def register(self, register):
        """
        Register and transform images.

        Arguments
        register: a Registering-type object
        """

        register.register(self.list, self.project)

    def stack(self, stacker):
        """
        Stack images using given stacker

        Arguments:
        stacker  = Stacker type object
        """

        newdata = stacker.stack(self.list, self.project)

        if self.itype == "light":
            Photo(project=self.project, data=newdata)
            Photo.write(final=True)
