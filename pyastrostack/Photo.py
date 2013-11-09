#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 2.10.2013

@author: Mikko Laine
"""

from astropy.io import fits
from os.path import splitext, exists, split, basename
from shutil import copyfile
from subprocess import call
import Conf
import numpy as np
from PIL import Image as Im
import gc
import re.sub


class Photo(object):
    """
    Class holds loading and saving photo files and converting photo to numpy.array
    """

    # format for intermediate files. TODO: Make this unnecessary
    format  = "fits"

    # dict to hold section to suffix mappings
    suffix = {
        "Registered frames": "reg",
        "RGB frames": "rgb",
        "Calibrated frames": "calib",
    }

    def __init__(self, section=None, number=None, project=None, rgb=None, data=None):
        """
        Constructor requires a filename of a raw image. I have a Canon EOS 1100D so Canon CR2 is what I originally
        write this for.
        # TODO: Support for other raws

        Arguments:
        section = Section in configuration. Essentially type of files.
        number  = Number to identify the image. Same as found in project file
        project = Conf.Project type object
        rgb     = True/False if image is RGB
        data    = Create Photo from numpy.array
        """

        # Common variables for any case
        self.project   = project
        self.tri       = np.array([])         # List of triangles
        self.match     = np.array([])         # List of matching triangles with reference picture
        self.name      = self.project.get("Default", "Project name")  # Name of project. Used to give name to temp files
        self.number    = number               # Number to identify the image
        self.wdir      = self.project.get("Setup", "Path")  # Working directory
        self.imagename = self.wdir + self.name

        # Create image from data
        if data is not None:
            self.data = data
            return

        # Create empty image
        if (section is None) & (number is None) & (data is None):
            return

        self.srcpath   = self.project.get(section, number)  # Path for source file
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
        if rgb:
            self.red       = fits.open(self.imagename + "_r.fits", memmap=True)
            self.green     = fits.open(self.imagename + "_g.fits", memmap=True)
            self.blue      = fits.open(self.imagename + "_b.fits", memmap=True)
            self.imager    = self.red[0]
            self.imageg    = self.green[0]
            self.imageb    = self.blue[0]
            self.data      = None

        else:
            self.hdu       = fits.open(self.imagepath, memmap=True)
            self.image     = self.hdu[0]
            self.data      = None

        self.x = self.image.shape[1]
        self.y = self.image.shape[0]

        print(self.name + str(self.number) + " - X: " + str(self.x) + ", Y: " + str(self.y))

    def load_data(self):
        """
        Load data into memory
        """
        if self.project.get("State", "Demosaic") == "1":
            self.data = np.array([self.imager.data, self.imageg.data, self.imageb.data])
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

    def write(self, section=None, number=None, final=False):
        """
        Write the image on disk

        Arguments:
        suffix   = Suffix to add to file name: <Project name>_suffix.fits
        final    = Define writing of final image. Temporary files are saved as FITS only
                   but final also as TIFF
        """

        hdu = fits.PrimaryHDU()                 # To create a default header
        self.imagename = self.imagename + "_" + self.suffix[section]
        self.imagepath = self.imagename + ".fits"
        self.number    = number

        # Monochrome data
        if self.data.ndim == 2:
            fits.writeto(self.imagepath + ".fits", self.data, hdu.header)

            # Write TIFF is image is final light
            if final & section not in ("dark", "bias", "flat"):
                image = Im.fromarray(np.int16(self.data))
                image.save(self.imagename + ".tiff", format="tiff")
            elif section in ("dark", "bias", "flat"):
                self.project.set("Master", section, self.imagepath)
            else:
                self.project.set(section, self.number, self.imagepath)

        # RGB data
        else:
            ccode = {1: "r", 2: "g", 3: "b"}
            rgbname = []
            rgbpath = []

            for i in [0, 1, 2]:
                rgbname[i] = self.imagename + "_" + ccode[i]
                rgbpath[i] = rgbname[i] + ".fits"
                fits.writeto(rgbpath[i], self.data[i], hdu.header)

            # Write TIFF is image is final
            if final:
                image = []
                for i in [0, 1, 2]:
                    rgbpath[i] = rgbname[i] + ".tiff"
                    image[i] = Im.fromarray(np.int16(self.data[i]))
                    image[i].save(rgbpath[i], format="tiff")

            else:
                for i in [0, 1, 2]:
                    self.project.set(section, str(self.number) + ccode[i], self.rgbpath[i])

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
            # Only one channel
            if key.isnumeric():
                photo = Photo(section=section, number=key, project=self.project)
            # Three channels
            else:
                photo = Photo(section=section, number=key, rgb=True, project=self.project)

            self.list[key] = photo

        if section in ("dark", "bias", "flat"):
            self.itype = section              # Define type of batch. Possibilities are light, flat, bias and dark
        else:
            self.itype = "light"

        self.refnum = int(project.get("Reference", key="self.itype"))  # Number of reference frame
        self.name   = self.project.get("Default", key="project name")  # Name for the resulting image

        self.master = Photo(project=project)  # New empty image to save the result in

    def refimg(self):
        """
        Returns the reference image
        """
        return self.list[self.refnum]

    def demosaic(self, demosaic):
        """
        Demosaic CFA-image into RGB.

        Arguments
        demosaic: a Demosaic-type object
        """

        for i in self.list:
            i.load_data()
            new = Photo(project=self.project, data=demosaic.bilinear_cl(i))
            new.write(section="RGB images", number=i.number)
            i.release_data()
        self.project.set("Demosaic", "1", "State")
        self.project.write()

    def register(self, register):
        """
        Register and transform images.

        Arguments
        register: a Registering-type object
        """

        register.register(self.list, self.project)
        self.project.set("State", "Registering", "1")
        self.project.write()

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
