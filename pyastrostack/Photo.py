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
from os import listdir
import datetime   # For profiling


class Frame:
    """
    Frame has all the information of a single photo frame and all the methods to read and write data on disk
    """

    def __init__(self, project, genname, infopath=None, number=None):
        """
        Create a Frame object from frameinfo file or create an empty Frame object.

        Arguments
        project = Project settings object
        genname = Generic name for image to load (light, calib, rgb, reg...)
        infopath = frame info file
        """

        # Common variables for any case
        self.project   = project
        self.name      = self.project.get("Default", "Project name")  # Name of project. Used to give name to temp files
        self.wdir      = self.project.get("Setup", "Path")  # Working directory
        self._genname  = genname
        self.format    = ".fits"

        # Instance variables required later
        self.rgb       = False      # Is image rgb or monochrome (Boolean)
        self.clip      = []
        self.tri       = []         # List of triangles
        self.match     = []         # List of matching triangles with reference picture

        self.path = None            # Path for image
        self.tiffpath = []          # List for paths to tiff files, required for aligning with imagemagick
        self.bayer = None
        self._x = None
        self._y = None               # Dimensions for image

        self.number = number

        # The following objects are lists because colour channels are separate
        self.hdu = None             # HDU-object for loading fits. Not required for tiff
        self.image = None           # Image object. Required for Tiff and Fits
        self._data = None   # Image data as an numpy.array

        if infopath:
            self.frameinfo = Conf.Frame(infopath, self.project)
            self.infopath = infopath
            self.readinfo()
        else:
            self.frameinfo = None
            self.infopath = self.wdir + self.name + "_" + str(self.number) + "_" + self.genname + ".info"
            if self.number or self.number == 0:
                self.path = self.wdir + self.name + "_" + str(self.number) + "_" + self.genname + ".fits"
            else:
                self.path = self.wdir + self.name + "_" + self.genname + ".fits"

    def rgbpath(self, fileformat=None):
        """
        Return list of file paths where "_[rgb]" is placed before the extension

        eg. if self.path is /path/to/file_2_reg.tiff this returns
         [/path/to/file_2_reg_r.tiff, /path/to/file_2_reg_g.tiff, /path/to/file_2_reg_b.tiff]
        This is required for ImageMagicks inability to understand rgb fits, or actually fits' in general
        Arguments:
        format = if specified, change the extension to this
        """

        base, ext = splitext(self.path)
        if fileformat:
            ext = "." + fileformat
        pathlist = []
        for i in ("_r", "_g", "_b"):
            pathlist.append(base + i + ext)
        return pathlist

    def combine(self, newpath):
        """
        Combine channels from three fits files into one.
        """
        hdu = []
        data = []

        for i in (0, 1, 2):
            hdu.append(fits.open(newpath[i]))
            data.append(hdu[i][0].data)

        self.data = np.array(data)
        self.write()

    def getpath(self, genname):
        """
        Return path by some other genname than self.genname. Read from .info
        """

        try:
            return self.frameinfo.get("Paths", genname)
        except:
            return self.wdir + self.name + "_" + str(self.number) + "_" + genname + ".fits"

    def readinfo(self):
        """
        Read frame info from specified file
        """

        self.number = self.frameinfo.get("Default", "Number")
        self.path = self.frameinfo.get("Paths", self.genname)
        #self.frametype = self.frameinfo.get("Default", "Frametype")
        self.x = int(self.frameinfo.get("Properties", "X"))
        self.y = int(self.frameinfo.get("Properties", "Y"))

    def extractinfo(self):
        """
        Read the file into memory and extract all required information
        """

        # TODO: Bayer matrix from cfa-images
        self.bayer = None

        self._load_data()

        # Image dimensions
        if len(self.image.shape) == 3:
            self.x = self.image.shape[2]
            self.y = self.image.shape[1]
        else:
            self.x = self.image.shape[1]
            self.y = self.image.shape[0]

        self._release_data()
        print("Done!")
        print("Image has dimensions X: " + str(self.x) + ", Y: " + str(self.y))

    def writeinfo(self):
        """
        Write frame info to specified file
        """

        self.frameinfo = Conf.Frame(self.infopath, self.project)

        self.frameinfo.set("Default", "Number", str(self.number))
        self.frameinfo.set("Paths", self.genname, self.path)
        #self.frameinfo.set("Default", "Frametype", self.frametype)
        self.frameinfo.set("Properties", "Bayer filter", str(self.bayer))
        self.frameinfo.set("Properties", "X", str(self.x))
        self.frameinfo.set("Properties", "Y", str(self.y))

    def fromraw(self, path):
        """
        Create a Frame object from raw photo

        Arguments:
        path - Unix path of the photo

        Returns:
        Frame
        """

        self._convert(path)
        self.extractinfo()
        self.writeinfo()

    def setclip(self, clip):
        """
        Set the data clip coordinates
        """

        self.clip = clip

    def getdata(self):
        """
        Getter for data.

        Data can't be loaded in memory all the time because of the size of it. This getter handles reading data
        from disk and returning it as if it were just Frame.data
        """

        if self._data is None:
            self._load_data()
        data = self._data.copy()
        self._release_data()
        return data

    def setdata(self, data):
        """
        Setter for data.
        """
        if len(data.shape) == 3:
            self._data = data
        else:
            self._data = np.array([data])

    def deldata(self):
        """
        Destructor for data
        """

        self._data = None

    data = property(getdata, setdata, deldata)

    def getgenname(self):
        return self._genname

    def setgenname(self, genname):
        """
        Set genname and take care of info file changes
        """
        self._genname = genname
        self.path = self.wdir + self.name + "_" + self.number + "_" + self.genname + ".fits"
        self.frameinfo.set("Paths", self.genname, self.path)

    genname = property(fget=getgenname, fset=setgenname)

    def get_x(self):
        if self._x:
            return self._x
        else:
            self.x = self.frameinfo.get("Properties", "X")
            return self._x

    def set_x(self, x):
        self._x = x

    x = property(fget=get_x, fset=set_x)

    def get_y(self):
        if self._y:
            return self._y
        else:
            self.y = self.frameinfo.get("Properties", "Y")
            return self._y

    def set_y(self, y):
        self._y = y

    y = property(fget=get_y, fset=set_y)

    def _convert(self, srcpath):
        """
        Convert the raw file into FITS via PGM.

        There are some problems with TIFF format. That's why via PGM.

        Arguments:
        srcpath - Full unix path where to find source file

        Return:
        Nothing. File is created or program crashed. Perhaps this is a good place for try-except...
        """

        if exists(srcpath):

            if exists(self.path):
                print("Image already converted.")
                return

            print("Converting RAW image...")
            if call(["dcraw -v -4 -t 0 -D " + srcpath], shell=True):
                print("Something went wrong... There might be helpful output from Rawtran above this line.")
                if exists(self.path):
                    print("File " + self.path + " was created but dcraw returned an error.")
                else:
                    print("Unable to continue.")
            else:
                move(srcpath[:-3] + "pgm", self.path[:-4] + "pgm")
                call(["convert", self.path[:-4] + "pgm", self.path])
                print("Conversion successful!")
        else:
            print("Unable to find file in given path: " + srcpath + ". Find out what's wrong and try again.")
            print("Can't continue. Exiting.")
            exit()

    def _load_fits(self):
        """
        Load a fits file created by this program

        Arguments:
        suffix - file name suffix indicating progress of process. eg. calib, reg, rgb
        number - number of file
        """

        self.hdu = fits.open(self.path, memmap=True)
        self.image = self.hdu[0]

    def _load_data(self):
        """
        Load portion of FITS-data into memory. Does not work with TIFF

        Arguments:
        rangetuple - coordinates of the clipping area (x0, x1, y0, y1)
        """

        if self.format != ".fits":
            print("This method works only with FITS files.")

        if self.clip:
            y0 = self.clip[0]
            y1 = self.clip[1]
            x0 = self.clip[2]
            x1 = self.clip[3]

            self._load_fits()

            if len(self.image.shape) == 3:
                self._data = self.image.data[0:3, x0:x1, y0:y1]
            else:
                self._data = np.array([self.image.data[x0:x1, y0:y1]])
        else:
            self._load_fits()
            if len(self.image.shape) == 3:
                self._data = self.image.data
            else:
                self._data = np.array([self.image.data])

    def _release_data(self):
        """
        Release data from memory and delete even the hdu
        """
        if self.hdu is not None:
            self.hdu.close()
        self.image = None
        self.data = None
        self.hdu = None

        gc.collect()

    def _write_fits(self):
        """
        Write self.data to disk as a fits file
        """

        hdu = fits.PrimaryHDU()  # To create a default header

        if self._data is None:
            print("No data set! Exiting...")
            exit()

        fits.writeto(self.path, np.int16(self.data), hdu.header, clobber=True)

    def _write_tiff(self):
        """
        Write self.data to disk as a tiff file
        """

        if self.data.shape[0] == 1:
            imagedata = np.flipud(np.int16(self.data[0].copy()))
            image = Im.fromarray(imagedata)
            image.save(splitext(self.path)[0] + ".tiff", format="tiff")

        elif self.data.shape[0] == 3:
            rgbpath = self.rgbpath(fileformat="tiff")
            for i in (0, 1, 2):
                imagedata = np.flipud(np.int16(self.data[i].copy()))
                image = Im.fromarray(imagedata)
                image.save(rgbpath[i], format="tiff")
            call(["convert", rgbpath[0], rgbpath[1], rgbpath[2],
                  "-channel", "RGB", "-depth", "16", "-combine",
                  splitext(self.path)[0] + ".tiff"])
            call(["rm", rgbpath[0], rgbpath[1], rgbpath[2]])

    def write_tiff(self):
        """
        Load data from current fits and save it as a tiff. Required because ImageMagick
        doesn't work with fits too well.
        """
        self._load_data()

        image = []
        rgbpath = self.rgbpath(fileformat="tiff")
        for i in [0, 1, 2]:
            image.append(Im.fromarray(np.flipud(np.int16(self.data[i])).copy()))
            image[i].save(rgbpath[i], format="tiff")

        self._release_data()

    def write(self, tiff=False):
        """
        Wrapper function to relay writing of the image on disk. This is remnants of something much more complicated...

        Arguments:
        tiff     = Write also a tiff file in addition to fits
        """

        self._write_fits()
        if tiff:
            self._write_tiff()


class Batch:
    """
    Batch holds a list of photos loaded with astropy's fits.open
    It also checks compatibility for each photo loaded
    """

    extensions = (".CR2", ".cr2")   # TODO: Add here all supported extensions, and move this to a better place

    def __init__(self, project, genname):
        """
        Constructor loads Frames according to arguments.

        Arguments:
        project = Configuration object for the project
        genname = Generic name of the files
        """

        self.project = project
        self.genname = genname

        self.name    = self.project.get("Default", key="project name")    # Name for the resulting image

        self.list    = {}                                                 # Empty dict for Photos

        if genname in ("flat", "dark", "bias"):
            self.category = genname
        else:
            self.category = "light"

        if self.project.hassection("Reference images"):
            if self.project.haskey("Reference images", self.genname):
                self.refnum  = int(project.get("Reference images", key=self.genname))  # Number of reference frame
            else:
                self.refnum = 1
        else:
            self.refnum = 1

        if self.project.hassection(self.category):
            files = self.project.get(self.category)                       # Paths for the frame info files
            for key in files:
                self.list[key] = Frame(self.project, self.genname, infopath=files[key], number=key)

    def demosaic(self, demosaic):
        """
        Demosaic CFA-image into RGB.

        Arguments
        demosaic: a Demosaic-type object
        """

        for i in self.list:
            print("Processing image " + self.list[i].path)
            t1 = datetime.datetime.now()
            self.list[i].data = demosaic.demosaic(self.list[i].data[0])
            t2 = datetime.datetime.now()
            print("...Done")
            print("Debayering took " + str(t2-t1) + " seconds.")
            self.list[i].genname = "rgb"
            self.list[i].write(tiff=True)
        self.project.set("Reference images", self.genname, str(self.refnum))

    def register(self, register):
        """
        Register and transform images.

        Arguments
        register: a Registering-type object
        """

        register.register(self.list, self.project)
        self.project.set("Reference images", self.genname, str(self.refnum))

    def stack(self, stacker):
        """
        Stack images using given stacker

        Arguments:
        stacker = Stacking type object
        """

        new = Frame(self.project, self.genname, number="master")
        new.data = stacker.stack(self.list, self.project)
        new.write(tiff=True)

    def subtract(self, calib, stacker):
        """
        Subtract calib from images in imagelist
        """

        cframe = Frame(self.project, calib, number="master")

        for i in self.list:
            print("Subtracting " + calib + " from image " + str(self.list[i].number))
            self.list[i].data = stacker.subtract(self.list[i], cframe)
            if self.list[i].genname not in ("bias", "dark", "flat"):
                self.list[i].genname = "calib"
            #print(self.list[i].infopath)
            self.list[i].write()
        self.project.set("Reference images", "calib", str(self.refnum))

    def divide(self, calib, stacker):
        """
        Divide images in imagelist with calib
        """

        cframe = Frame(self.project, calib, number="master")

        for i in self.list:
            print("Dividing image " + str(self.list[i].number) + " with " + calib)
            self.list[i].data = stacker.divide(self.list[i], cframe)
            if self.list[i].genname not in ("bias", "dark", "flat"):
                self.list[i].genname = "calib"
            self.list[i].write()
        self.project.set("Reference images", "calib", str(self.refnum))

    def directory(self, path, itype):
        """
        Add directory to Batch

        Arguments:
        path - Unix path where the photos are (Must end in "/")
        type - Type of photo frames (light, dark, bias, flat)
        """

        allfiles = listdir(path)
        rawfiles = []

        for i in allfiles:
            if splitext(i)[1] in self.extensions:
                rawfiles.append(path + i)

        if len(rawfiles) != 0:
            print("Found files :")
            for i in rawfiles:
                print(i)
        else:
            print("No supported RAW files found. All files found are listed here: " + str(allfiles))
            exit()

        n = len(self.list)

        for i in rawfiles:
            frame = Frame(self.project, self.genname, number=n)
            frame.fromraw(i)
            self.project.set(itype, str(n), frame.infopath)
            n += 1

        # Set reference only if not already set
        #if not self.project.hassection("Reference images"):
        #    print("Setting first image in list as reference image. This can be altered in project file.")
        #    ref = "1"
        #    self.project.set("Reference images", itype, ref)
        #elif not self.project.haskey("Reference images", itype):
        #    print("Setting first image in list as reference image. This can be altered in project file.")
        #    ref = "1"
        #    self.project.set("Reference images", itype, ref)

        self.project.set("Reference images", itype, "1")
        self.project.write()