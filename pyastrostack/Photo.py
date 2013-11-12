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
from re import sub


class Photo(object):
    """
    Class holds loading and saving photo files and converting photo to numpy.array
    """

    # TODO: Make this unnecessary
    format  = "fits"
    """
    Set format for intermediate files. Only FITS is possible as of 2013-10-08 but this might be
    in use somewhere else as well.

    Will be removed.
    """

    suffix = {
        "Registered images": "reg",
        "RGB images": "rgb",
        "Calibrated images": "calib",
    }
    """
    Dictionary to hold section name to file suffix mappings. Files are named according to a scheme.
    This dict is used to fetch filename addition (suffix does not mean extension here) according
    to previous process.

    File names are like:
    <Project name>_<suffix>(_rgb).fits
    for example
    Andromeda_reg_r.fits, which is registered red channel of project Andromeda
    """

    ccode = {0: "r", 1: "g", 2: "b"}
    """
    Dictionary to fetch colour channel suffix to file names. RGB data is usually handled by
    arrays where index 0 is red, 1 is green and 2 is blue.
    """

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
        self.tri       = []         # List of triangles
        self.match     = []         # List of matching triangles with reference picture
        self.name      = self.project.get("Default", "Project name")  # Name of project. Used to give name to temp files
        self.number    = number               # Number to identify the image
        self.wdir      = self.project.get("Setup", "Path")  # Working directory
        self.imagename = self.wdir + self.name + "_" + str(self.number)

        # Create image from data
        if data is not None:
            self.data = data
            return

        # Create empty image
        if (section is None) & (number is None) & (data is None):
            return

        if not rgb:
            self.srcpath   = self.project.get(section, number)  # Path for source file
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

        self.imagepath = self.imagename + ".fits"

        if section in ("dark", "bias", "flat"):
            self.itype = section
        else:
            self.itype = "light"

        # Check if demosaicing done and assume rgb-pictures
        if rgb:
            self.imagepath = ["", "", ""]
            self.hdu       = [0, 0, 0]
            self.image     = [0, 0, 0]
            self.srcpath   = self.project.get(section, number + "r")[:-7]
            for i in [0, 1, 2]:
                self.imagepath[i] = self.srcpath + "_" + self.ccode[i] + ".fits"
                self.hdu[i]       = fits.open(self.imagepath[i], memmap=True)
                self.image[i]     = self.hdu[i][0]

            self.rgb    = True
            self.data   = None
            self.x = self.image[0].shape[1]
            self.y = self.image[0].shape[0]

        else:
            self.rgb   = False
            self.hdu   = fits.open(self.imagepath, memmap=True)
            self.image = self.hdu[0]
            self.data  = None

            self.x = self.image.shape[1]
            self.y = self.image.shape[0]

        print(self.name + str(self.number) + " - X: " + str(self.x) + ", Y: " + str(self.y))

    def load_data(self):
        """
        Load data into memory
        """
        if self.rgb:
            self.data = np.array([self.image[0].data, self.image[1].data, self.image[2].data])
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
        if section:
            self.number    = number
            self.imagename = self.wdir + self.name + "_" + str(self.number) + "_" + self.suffix[section]
        else:
            self.imagename = self.wdir + self.name + "_final"
        self.imagepath = self.imagename + ".fits"

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
            rgbname = [0, 0, 0]
            rgbpath = ["", "", ""]

            for i in [0, 1, 2]:
                rgbname[i] = self.imagename + "_" + self.ccode[i]
                rgbpath[i] = rgbname[i] + ".fits"
                fits.writeto(rgbpath[i], self.data[i], hdu.header)

            # Write TIFF is image is final
            if final:
                image = [0, 0, 0]
                for i in [0, 1, 2]:
                    rgbpath[i] = rgbname[i] + ".tiff"
                    image[i] = Im.fromarray(np.int16(self.data[i]))
                    image[i].save(rgbpath[i], format="tiff")

            else:
                for i in [0, 1, 2]:
                    self.project.set(section, str(self.number) + self.ccode[i], rgbpath[i])

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


        filestemp = {}
        for key in files:
            if not key.isnumeric():
                temp = sub("\D", "", key)
                if temp not in filestemp:
                    filestemp[temp] = files[key][:-7]

        if len(filestemp) != 0:
            rgb = True
            files = filestemp
        else:
            rgb = False

        for key in files:
            # Only one channel
            if not rgb:
                photo = Photo(section=section, number=key, project=self.project)
            # Three channels
            else:
                photo = Photo(section=section, number=key, rgb=True, project=self.project)

            self.list[key] = photo

        if section in ("dark", "bias", "flat"):
            self.itype = section              # Define type of batch. Possibilities are light, flat, bias and dark
        else:
            self.itype = "light"

        self.refnum = int(project.get("Reference images", key="light"))  # Number of reference frame
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
            self.list[i].load_data()
            new = Photo(project=self.project, data=demosaic.bilinear_cl(self.list[i]))
            new.write(section="RGB images", number=i)
            self.list[i].release_data()
        self.project.set("State", "Demosaic", "1")
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
            new = Photo(project=self.project, data=newdata)
            new.write(final=True)
