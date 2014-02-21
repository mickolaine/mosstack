#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 2.10.2013

@author: Mikko Laine
"""

from astropy.io import fits
from os.path import splitext, exists, split, basename
from shutil import copyfile, move
from subprocess import call
from . import Conf
import numpy as np
from PIL import Image as Im
import gc
from re import sub


class Photo(object):
    """
    Class holds loading and saving photo files and converting photo to numpy.array
    """

    suffix = {
        "Registered images": "reg",
        "RGB images": "rgb",
        "Calibrated images": "calib",
        "Master frames": "master",
        "bias": "bias",
        "dark": "dark",
        "flat": "flat",
        "light": "light"
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

    section = {
        "reg": "Registered images",
        "rgb": "RGB images",
        "calib": "Calibrated images",
        "master": "Master frames",
        "bias": "bias",
        "dark": "dark",
        "flat": "flat",
        "light": "light"
    }
    """
    Dictionary to hold file suffix to section name mappings. Same as dict suffix but backwards
    """

    calib = ("flat", "bias", "dark", "Master frames")
    """
    Tuple of identifiers of calibration frames
    """

    ccode = {0: "r", 1: "g", 2: "b"}
    """
    Dictionary to fetch colour channel suffix to file names. RGB data is usually handled by
    arrays where index 0 is red, 1 is green and 2 is blue.
    """

    def __init__(self, section=None, number=None, project=None, data=None, raw=False, load=True):
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
        raw     = Boolean to indicate whether image is camera raw or something created by this program
        """

        # Common variables for any case
        self.format    = ".fits"
        self.project   = project
        self.name      = self.project.get("Default", "Project name")  # Name of project. Used to give name to temp files
        self.number    = number     # Number to identify the image
        self.wdir      = self.project.get("Setup", "Path")  # Working directory
        self.sec       = section
        self.load      = load

        # Instance variables required later
        self.srcpath   = None       # Path for source image
        self.rgb       = False      # Is image rgb or monochrome (Boolean)
        self.tri       = []         # List of triangles
        self.match     = []         # List of matching triangles with reference picture

        self.x = None
        self.y = None               # Dimensions for image

        # The following objects are lists because colour channels are separate
        self.hdu = []               # HDU-object for loading fits. Not required for tiff
        self.image = []             # Image object. Required for Tiff and Fits
        self.data = np.array([])    # Image data as an numpy.array

        if section in self.calib:
            if section == "Master frames":
                self.imagename = self.wdir + self.name + "_" + number + "_master"
            else:
                self.imagename = self.wdir + self.name + "_" + section + "_" + str(self.number)

        else:
            self.imagename = self.wdir + self.name + "_" + str(self.number)

        # Frame information file.
        self.frame = Conf.Frame(self.imagename + ".info", self.project)

        self.imagepath = self.imagename + self.format

        # Create image from data
        if data is not None:
            self.data = data
            return

        # Create empty image
        if (section is None) & (number is None) & (data is None):
            return

        loaded = bool(int(self.frame.get("Default", "Loaded")))

        if loaded and section not in self.calib:
            self.x = float(self.frame.get("Image", "X"))
            self.y = float(self.frame.get("Image", "Y"))
            self.imagepath = []
            if self.project.get("Colors", section) == "rgb":
                self.rgb = True
            if self.rgb:
                for i in (0, 1, 2):
                    self.imagepath.append(self.frame.get("Paths", self.section[section] + " " + self.ccode[i]))
            else:
                self.imagepath = self.frame.get("Paths", self.section[section])

        if not loaded or self.load or section in self.calib:
            if raw:
                self._load_raw(self.suffix[section], number)
            if self.format == ".fits":
                self._load_fits(section, number)
            elif self.format == ".tiff":
                self._load_tiff(section, number)

    def _load_raw(self, suffix, number):
        """
        Load a 'raw' image. This could be anything in the future but for now DSLR raws will be supported.
        I have a Canon myself so that's what I'll use for testing. I try to write support for other formats
        as well.

        Arguments:
        suffix - light, dark, flat, bias. I use the same name than in other _load_* methods
        number - number of file
        """

        srcpath = self.project.get(suffix, number)  # Path for source file
        rawformat = splitext(srcpath)[1][1:]

        print("Loading RAW image " + srcpath + "...")

        if rawformat == "fits":
            # If image source image resides outside wdir, copy it there
            if split(srcpath)[0] + "/" != self.wdir:
                copyfile(srcpath, self.imagepath)
            else:
                self.imagepath = srcpath
        else:
            self._convert_pgm(srcpath)
            self.frame.set("Paths", "Light", self.imagepath)
        print("Done!")

    def _load_tiff(self, suffix, number):
        """
        Load a tiff file created by this program

        Arguments:
        suffix - file name suffix indicating progress of process. eg. calib, reg, rgb
        number - number of file
        """

        color = self.project.get("Colors", suffix)

        if color == "rgb":
            self.imagepath = []
            self.hdu       = []
            self.image     = []
            self.data      = []
            self.srcpath   = self.project.get(self.section[suffix], number + "r")[:-7]
            for i in [0, 1, 2]:
                self.imagepath.append(self.srcpath + "_" + self.ccode[i] + ".tiff")
                self.frame.set("Paths", self.section[suffix] + " " + self.ccode[i], self.imagepath[i])
                print("Loading RGB image element " + self.imagepath[i] + "...")
                self.image.append(Im.open(self.imagepath[i]))
                self.data.append(np.flipud(np.array(self.image[i])))
            self.x = len(self.data[0][0])
            self.y = len(self.data[0])

            self.frame.set("Image", "X", str(self.x))
            self.frame.set("Image", "Y", str(self.y))
            self.rgb    = True
            self.data   = None

            print("Done!")
            print("Image has dimensions X: " + str(self.x) + ", Y: " + str(self.y))

        else:
            self.rgb   = False
            print("Loading image " + self.imagepath + "...")
            self.image = Im.open(self.imagepath)
            self.data  = np.array(self.image)
            self.data  = np.flipud(self.data)
            self.x = len(self.data[0])
            self.y = len(self.data)

            self.frame.set("Image", "X", str(self.x))
            self.frame.set("Image", "Y", str(self.y))
            self.data  = None

            print("Done!")
            print("Image has dimensions X: " + str(self.x) + ", Y: " + str(self.y))
        self.frame.set("Default", "Loaded", "1")

    def _load_fits(self, suffix, number):
        """
        Load a fits file created by this program

        Arguments:
        suffix - file name suffix indicating progress of process. eg. calib, reg, rgb
        number - number of file
        """
        color = self.project.get("Colors", suffix)

        if color == "rgb":
            self.rgb    = True
            self.imagepath = []
            self.hdu       = []
            self.image     = []
            self.data      = np.array([])
            self.srcpath   = self.project.get(self.section[suffix], number + "r")[:-7]
            for i in [0, 1, 2]:
                self.imagepath.append(self.srcpath + "_" + self.ccode[i] + ".fits")
                self.frame.set("Paths", self.section[suffix] + " " + self.ccode[i], self.imagepath[i])
            for i in [0, 1, 2]:
                print("Loading image " + self.imagepath[i] + "...")
                self.hdu.append(fits.open(self.imagepath[i], memmap=True))
                self.image.append(self.hdu[i][0])
            self.x = self.image[0].shape[1]
            self.y = self.image[0].shape[0]

            self.frame.set("Image", "X", str(self.x))
            self.frame.set("Image", "Y", str(self.y))

            self.load_data()

            #self.data   = None
            self.release_data2()
            gc.collect()

            print("Done!")
            print("Image has dimensions X: " + str(self.x) + ", Y: " + str(self.y))

        else:
            self.rgb   = False
            print("Loading image " + self.imagepath + "...")
            self.hdu   = fits.open(self.imagepath, memmap=True)
            self.image = self.hdu[0]
            self.x = self.image.shape[1]
            self.y = self.image.shape[0]

            self.frame.set("Image", "X", str(self.x))
            self.frame.set("Image", "Y", str(self.y))

            self.data  = None

            print("Done!")
            print("Image has dimensions X: " + str(self.x) + ", Y: " + str(self.y))
        self.frame.set("Default", "Loaded", "1")

    def _load_fits2(self, suffix, number):
        """
        Load a fits file created by this program

        Arguments:
        suffix - file name suffix indicating progress of process. eg. calib, reg, rgb
        number - number of file
        """
        color = self.project.get("Colors", suffix)

        if self.rgb:
            self.imagepath = []
            self.hdu       = []
            self.image     = []
            self.data      = np.array([])
            self.srcpath   = self.project.get(self.section[suffix], number + "r")[:-7]
            for i in [0, 1, 2]:
                self.imagepath.append(self.srcpath + "_" + self.ccode[i] + ".fits")
                self.hdu.append(fits.open(self.imagepath[i], memmap=True))
                self.image.append(self.hdu[i][0])
        else:
            self.hdu   = fits.open(self.imagepath, memmap=True)
            self.image = self.hdu[0]
            self.x = self.image.shape[1]
            self.y = self.image.shape[0]

            self.frame.set("Image", "X", str(self.x))
            self.frame.set("Image", "Y", str(self.y))

            self.data  = None
        self.frame.set("Default", "Loaded", "1")

    def load_data(self):
        """
        Load data into memory
        """
        if self.format == ".fits":
            if self.rgb:
                self.data = np.array([self.image[0].data, self.image[1].data, self.image[2].data])
            else:
                self.data = self.image.data
        else:
            if self.rgb:
                self.data = np.array([np.flipud(np.array(self.image[0])),
                                      np.flipud(np.array(self.image[1])),
                                      np.flipud(np.array(self.image[2]))])
            else:
                self.data = np.flipud(np.array(self.image))

    def load_data2(self, clip=None):
        """
        Load portion of FITS-data into memory. Does not work with TIFF

        Arguments:
        rangetuple - coordinates of the clipping area (x0, x1, y0, y1)
        """

        if self.format != ".fits":
            print("This method works only with FITS files.")

        if clip is not None:
            y0 = clip[0]
            y1 = clip[1]
            x0 = clip[2]
            x1 = clip[3]

            self._load_fits2(self.sec, self.number)

            if self.rgb:
                self.data = np.array([self.image[0].data[x0:x1, y0:y1],
                                      self.image[1].data[x0:x1, y0:y1],
                                      self.image[2].data[x0:x1, y0:y1]])
            else:
                self.data = self.image.data[x0:x1, y0:y1]

        else:
            self._load_fits2(self.sec, self.number)

            if self.rgb:
                self.data = np.array([self.image[0].data,
                                      self.image[1].data,
                                      self.image[2].data])
            else:
                self.data = self.image.data

    def release_data(self):
        """
        Release data from memory
        """
        #self.data = None
        for i in [0, 1, 2]:
            self.hdu[i].close()
            self.image[i] = None
            self.data[i] = None
        del self.image
        del self.data
        gc.collect()

    def release_data2(self):
        """
        Release data from memory and delete even the hdu
        """
        if self.rgb:
            for i in [0, 1, 2]:
                self.hdu[i].close()
                self.image[i] = None
                self.data = None
                self.hdu[i] = None
            del self.image
            del self.data

        else:
            self.hdu.close()
            self.image = None
            self.data = None
            self.hdu = None

        gc.collect()

    def _convert_pgm(self, srcpath):
        """
        Convert the raw file into FITS via PGM. This is a test because I think the PIL-kit has some problems
        with TIFF files.

        Arguments:
        srcpath - Full unix path where to find source file

        Return:
        Nothing. File is created or program crashed. Perhaps this is a good place for try-except...
        """

        if exists(srcpath):

            if exists(self.imagepath):
                print("Image already converted.")
                return

            print("Converting RAW image...")
            if call(["dcraw -v -4 -t 0 -D " + srcpath], shell=True):
                print("Something went wrong... There might be helpful output from Rawtran above this line.")
                if exists(self.imagepath):
                    print("File " + self.imagepath + " was created but dcraw returned an error.")
                else:
                    print("Unable to continue.")
            else:
                move(srcpath[:-3] + "pgm", self.imagepath[:-4] + "pgm")
                call(["convert", self.imagepath[:-4] + "pgm", self.imagepath])
                print("Conversion successful!")
        else:
            print("Unable to find file in given path: " + srcpath + ". Find out what's wrong and try again.")
            print("Can't continue. Exiting.")
            exit()

    def convert(self, srcpath):
        """
        Convert the raw into TIFF
        """

        if exists(srcpath):
            if not exists(self.imagepath):                   # Don't convert raws again
                print("Converting RAW image...")
                if call(["dcraw -v -T -4 -t 0 -d " + srcpath], shell=True):
                    print("Something went wrong... There might be helpful output from Rawtran above this line.")
                    print("File " + srcpath + " exists.")
                    if exists(self.imagepath):
                        print("File " + self.imagepath + " exists.")
                        print("Here's information about it:")
                        # TODO: Check size and magic numbers with file utility
                    else:
                        print("File " + self.imagepath + " does not. Unable to continue.")
                        exit()  # TODO: Make it able to continue without this picture
                else:
                    move(srcpath[:-3] + "tiff", self.imagepath[:-4] + "tiff")
                    call(["convert", self.imagepath[:-4] + "tiff", self.imagepath])
                    print("Conversion successful!")

        else:
            print("Unable to find file in given path: " + srcpath + ". Find out what's wrong and try again.")
            print("Can't continue. Exiting.")
            exit()

    def _write_fits(self, section, number, final=False, log=False):
        """
        Write self.data to disk as a fits file

        Arguments:
        suffix   = Suffix to add to file name: <Project name>_suffix.fits
        number   = Number of the image
        final    = Add "final" to file name
        log      = Write file info to project file
        """

        hdu = fits.PrimaryHDU()                 # To create a default header

        if self.data is None:
            print("No data set! Exiting...")
            exit()

        if final:
            self.imagename = self.wdir + self.name + "_final"
        else:
            self.number = number
            try:
                suffix = self.suffix[section]
            except KeyError:
                suffix = section
            self.imagename = self.wdir + self.name + "_" + str(self.number) + "_" + suffix

        self.imagepath = self.imagename + ".fits"

        # CFA or single channel data. Only one file to create.
        # TODO: modify data so that single channel has ndim == 1 (ISSUE #3)
        if self.data.ndim == 2:
            fits.writeto(self.imagepath, np.int16(self.data), hdu.header, clobber=True)
            if log:
                if section == "Master frames":
                    self.project.set(section, number, self.imagepath)
                else:
                    self.project.set(section, str(self.number), self.imagepath)
                    self.frame.set("Paths", section, self.imagepath)

        elif self.data.ndim == 3:
            rgbname = ["", "", ""]
            rgbpath = ["", "", ""]
            for i in [0, 1, 2]:
                rgbname[i] = self.imagename + "_" + self.ccode[i]
                rgbpath[i] = rgbname[i] + ".fits"
                fits.writeto(rgbpath[i],
                             np.int16(self.data[i]),  # / np.amax(self.data[i]) * 63000.),
                             hdu.header,
                             clobber=True)
                if log:
                    self.project.set(section, str(self.number) + self.ccode[i], rgbpath[i])
                    self.frame.set("Paths", section + " " + self.ccode[i], rgbpath[i])
            if final:
                call(["convert", rgbpath[0], rgbpath[1], rgbpath[2], "-channel", "RGB", "-combine",
                      "-depth", "16", self.imagename + "_combined.tiff"])
        else:
            print("Data has unsupported number of dimensions. Exiting...")
            exit()
        self.project.write()

    def _write_tiff(self, section, number, final=False, log=False):
        """
        Write self.data to disk as a tiff file

        Arguments:
        suffix   = Suffix to add to file name: <Project name>_suffix.fits
        number   = Number of the image
        final    = Add "final" to file name
        log      = Write file info to project file
        """

        if section:
            self.number = number
            try:
                suffix = self.suffix[section]
            except KeyError:
                suffix = section
            self.imagename = self.wdir + self.name + "_" + str(self.number) + "_" + suffix
        else:
            self.imagename = self.wdir + self.name + "_final"
        self.imagepath = self.imagename + ".tiff"

        if self.data.ndim == 2:
            image = Im.fromarray(np.flipud(np.int16(self.data)).copy())
            image.save(self.imagename + ".tiff", format="tiff")
            if log:
                self.project.set(section, str(self.number), self.imagepath)

        elif self.data.ndim == 3:
            rgbname = ["", "", ""]
            rgbpath = ["", "", ""]

            image = [0, 0, 0]
            for i in [0, 1, 2]:
                rgbpath[i] = rgbname[i] + ".tiff"
                image[i] = Im.fromarray(np.flipud(np.int16(self.data[i])).copy())
                image[i].save(rgbpath[i], format="tiff")
                if log:
                    self.project.set(section, str(self.number) + self.ccode[i], rgbpath[i])
        self.project.write()

    def write_tiff(self):
        """
        Load data from current fits and save it as a tiff. Required because ImageMagick
        doesn't work with fits too well.
        """
        self.load_data2()

        image = [0, 0, 0]
        for i in [0, 1, 2]:
            image[i] = Im.fromarray(np.flipud(np.int16(self.data[i])).copy())
            image[i].save(self.imagepath[i][:-5] + ".tiff", format="tiff")

        self.release_data2()

    def write(self, section=None, number=None, final=False, log=True):
        """
        Wrapper function to relay writing of the image on disk

        Arguments:
        suffix   = Suffix to add to file name: <Project name>_suffix.fits
        number   = Defines the number of photo.
        final    = Define writing of final image. Temporary files are saved as FITS only
                   but final also as TIFF
        """

        self._write_fits(section, number, final=final, log=log)

    def release(self):
        """
        Release not needed images from memory
        """

        self.image = None
        gc.collect()
        self.data = None
        
    
class Batch:
    """
    Batch holds a list of photos loaded with astropy's fits.open
    It also checks compatibility for each photo loaded
    """

    def __init__(self, section=None, project=None, load=True):
        """
        Constructor loads all necessary objects and sets some default values
        list will have Photo.Photo type objects which will hold all the information of one image.

        Arguments:
        section = section of files in project file
        project = Project object
        """

        self.project = project
        files        = self.project.get(Photo.section[section])
        self.list    = {}                     # Empty list for Photos
        self.section = section

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

        if section in ("light", "dark", "flat", "bias"):
            self.project.set("Colors", section, "cfa")
            raw = True
        else:
            raw = False

        if section in ("dark", "bias", "flat"):
            self.itype = section              # Define type of batch. Possibilities are light, flat, bias and dark
            self.project.set("Colors", "Master frames", "cfa")
            self.project.write()
        else:
            self.itype = "light"

        for key in files:
            photo = Photo(section=section, number=key, project=self.project, raw=raw, load=load)
            self.list[key] = photo

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
            self.list[i].load_data2()
            new = Photo(project=self.project, number=i, data=demosaic.demosaic(self.list[i]))
            new.write(section="RGB images", number=i)
            self.list[i].release_data2()
        self.project.set("Colors", "rgb", "rgb")
        self.project.set("State", "Demosaic", "1")
        self.project.write()

    def register(self, register):
        """
        Register and transform images.

        Arguments
        register: a Registering-type object
        """

        register.register(self.list, self.project)
        self.project.set("Colors", "reg", "rgb")
        self.project.set("State", "Registering", "1")
        self.project.write()

    def stack(self, stacker):
        """
        Stack images using given stacker

        Arguments:
        stacker  = Stacking type object
        """

        newdata = stacker.stack(self.list, self.project)

        if self.itype == "light":
            new = Photo(project=self.project, data=newdata)
            new.write(final=True, log=False)
        elif self.itype in ("bias", "dark", "flat"):
            new = Photo(project=self.project, data=newdata)
            new.write(section="Master frames", number=self.itype)

    def subtract(self, calib, stacker):
        """
        Subtract calib from images in imagelist
        """

        calib = Photo(section="Master frames", number=calib, project=self.project)
        calib.load_data()

        for i in self.list:
            self.list[i].load_data2()
            new = Photo(project=self.project, number=i, data=stacker.subtract(self.list[i], calib))
            if self.section in ("flat", "bias", "dark"):
                new.write(section=self.section, number=i)
            else:
                new.write(section="Calibrated images", number=i)
            self.list[i].release_data2()
        calib.release_data2()
        self.project.set("Colors", "calib", "cfa")
        self.project.write()

    def divide(self, calib, stacker):
        """
        Divide images in imagelist with calib
        """

        calib = Photo(section="Master frames", number=calib, project=self.project)
        calib.load_data()
        for i in self.list:
            self.list[i].load_data2()
            new = Photo(project=self.project, number=i, data=stacker.divide(self.list[i], calib))
            new.write(section="Calibrated images", number=i)
            self.list[i].release_data2()
        calib.release_data2()
        self.project.set("Colors", "calib", "cfa")
        self.project.write()