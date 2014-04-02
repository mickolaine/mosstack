"""
Created on 2.10.2013

@author: Mikko Laine


"""

from __future__ import division
from .. Registering.Registering import Registering
from subprocess import call, check_output
#from .. import Conf
from math import sqrt, log, fabs
#from operator import itemgetter
from os.path import splitext
from re import sub
import datetime   # For profiling
import pyximport
import numpy as np
pyximport.install(setup_args={'include_dirs': [np.get_include()]})
from . _step2 import step2 as _step2
from shutil import copyfile


class Sextractor2(Registering):
    """
    Implementation of Registering interface. This class uses SExtractor to find stars on a picture and ImageMagick
    to perform affine transform accordingly. Star matching is done with method described by E.J. Groth on article
    'A pattern-matching algorithm for two-dimensional coordinate' (http://adsabs.harvard.edu/abs/1986AJ.....91.1244G)

    This file is an attempt to make triangle matching faster by doing the calculations on Cython. So far it's a failure
    and calculations actually take more than 50% more time.

    Update 14-02-18: With couple of modifications this became about 30% faster than pure Python. Making the default for
    now. This file needs a cleanup though...
    """

    def __init__(self):
        pass

    def register(self, imagelist, project):
        """
        Calls everything required for total registration process.
        """

        t1 = datetime.datetime.now()

        self.findstars(imagelist, project)

        ref = project.get("Reference images", "light")

        for i in imagelist:
            self.step1(imagelist[i])                      # Step1 has to be finished before the rest

        for i in imagelist:

            # Don't match image with itself
            if sub("\D", "", imagelist[i].number) == ref:  # For RGB-images i.number holds more than number. Strip that
                oldpath = imagelist[i].path
                imagelist[i].genname = "reg"  # TODO: This is because of problems in Python2. Fix it
                newpath = imagelist[i].path
                copyfile(oldpath, newpath)
                continue

            imagelist[i].write_tiff()
            oldpath = imagelist[i].rgbpath(fileformat="tiff")
            imagelist[i].genname = "reg"
            newpath = imagelist[i].rgbpath()

            self.step2(imagelist[ref], imagelist[i])

            self.transform_magick(imagelist[i], oldpath, newpath)

            imagelist[i].combine(newpath)

        t2 = datetime.datetime.now()
        print("Triangle calculations took " + str(t2 - t1) + " seconds.")

    def findstars(self, imagelist, project):
        """
        Finds the stars and creates all the triangles from them
        """
        S = Sex(imagelist['1'], project)    # TODO: Ref image here
        sensitivity = S.findsensitivity()
        del S

        for i in imagelist:
            S = Sex(imagelist[i], project)
            S.setsensitivity(sensitivity[0], sensitivity[1])
            imagelist[i].coordinates = S.getcoordinates()
            S.maketriangles()

    def step1(self, image):
        """
        Calculates R,C,tR and tC for every triangle in image. These quantities are described in article #TODO: Cite the article

        Result image.tri = [[x1,y1,x2,y2,x3,y3, R, C, tR, tC], ... , ...]
        """

        ep = 0.3
        #xi = 3. * ep

        newtri = []
        for tri in image.tri:      # tri is a list of coordinates. ((x1,y1),(x2,y2),(x3,y3))

            x1 = tri[0][0]
            y1 = tri[0][1]
            x2 = tri[1][0]
            y2 = tri[1][1]
            x3 = tri[2][0]
            y3 = tri[2][1]

            x3x1 = x3 - x1
            y3y1 = y3 - y1
            x2x1 = x2 - x1
            y2y1 = y2 - y1

            r3 = sqrt(x3x1 * x3x1 + y3y1 * y3y1)
            r2 = sqrt(x2x1 * x2x1 + y2y1 * y2y1)

            R = r3 / r2
            #if R > 1.11:
            #    continue
            C = (x3x1 * x2x1 + y3y1 * y2y1) / (r3 * r2)     #Cosine of angle at vertex 1

            #tR = sqrt(2. * R ** 2. * ep ** 2. * (1. / r3 ** 2. - C / (r2 * r3) + 1. / r2 ** 2.))
            tR = sqrt(2. * R * R * ep * ep * (1. / (r3 * r3) - C / (r2 * r3) + 1. / (r2 * r2)))

            S = 1. - C ** 2.   #Sine^2 of angle at vertex 1
            # S should be S**2 and on above line S should be sqrt of 1-C**2,
            # but this might be faster. I don't know if python optimizes this.
            tC = sqrt(2. * S * ep * ep * (1. / (r3 * r3) - C / (r2 * r3) + 1. / (r2 * r2)) +
                      3. * C * C * ep * ep * ep * ep * (1. / (r3 * r3) - C / (r2 * r3) + 1. / (r2 * r2)) ** 2.)


            temp = [tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]]
            temp.append(R)
            temp.append(C)
            temp.append(tR)
            temp.append(tC)
            newtri.append(temp)
        #image.tri = np.array(newtri)
        image.tri = newtri

        print("Step 1 complete for image " + str(image.number) + ". " + str(len(image.tri)) + " triangles found.")

    #@staticmethod
    def step2(self, i1, i2):
        """
        A wrapper for Cython implementation of the algorithm

        i1 and i2 have a list tri = [[(x1,y1),(x2,y2),(x3,y3), R, C, tR, tC], ... , ...]
        """

        print("Matching image " + str(i2.number) + " to reference image " + str(i1.number) + "...")

        i2.pairs = _step2(i1.tri, i2.tri)

        print("Done.")

    def transform_magick(self, image, oldpath, newpath):
        """
        Transforms image according to image.pairs.

        Transformation is done with ImageMagick's "convert -distort Affine" from command line.

        Arguments:
        oldpath - list of pathnames for files to transform
        newpath - list of pathnames for resulting files
        """

        # Preparations
        points = "'"
        n = 0
        for i in image.pairs:
            if n > 11:          # max number of control points is 12
                break
            points = points + "{},{},{},{} ".format(int(i[0][0]), int(i[0][1]), int(i[1][0]), int(i[1][1]))
            n += 1
        points += "'"

        # Actual transforming
        if len(oldpath) == 3:
            for i in [0, 1, 2]:
                command = "convert " + oldpath[i] + " -distort Affine " \
                          + points + " " + newpath[i]
                call([command], shell=True)
                call(["rm " + oldpath[i]], shell=True)

        else:
            command = "convert " + oldpath + " -distort Affine "\
                      + points + " " + newpath
            call([command], shell=True)
            call(["rm " + oldpath], shell=True)


class Sex:
    """
    Class Sextractor controls SExtractor, obviously. Shortly, this class will extract xy-positions of stars from a fits.

    It creates a suitable configuration file, calls sextractor (or sex, have to check the name of the executable),
    checks and parses the output.
    """

    def __init__(self, image, project):
        """
        Initializes the object and common configuration values
        """

        self.image = image
        self.sextractor = project.sex
        self.path = project.path
        self.imagepath = image.getpath("light")
        self.catname = splitext(self.image.infopath)[0] + ".cat"
        self.confname = splitext(self.image.infopath)[0] + ".sex"

        self.coord = None

        self.config = {
            #-------------------------------- Catalog ------------------------------------
            "CATALOG_NAME":      self.catname,     # name of the output catalog
            "CATALOG_TYPE":      "ASCII_HEAD",     # NONE,ASCII,ASCII_HEAD, ASCII_SKYCAT,
                                                   # ASCII_VOTABLE, FITS_1.0 or FITS_LDAC
            "PARAMETERS_NAME":   "default.param",  # name of the file containing catalog contents

            #------------------------------- Extraction ----------------------------------
            "DETECT_TYPE":       "CCD",            # CCD (linear) or PHOTO (with gamma correction)
            "DETECT_MINAREA":    "70",             # minimum number of pixels above threshold
            "DETECT_THRESH":     "6.5",            # <sigmas> or <threshold>,<ZP> in mag.arcsec-2
            "ANALYSIS_THRESH":   "2.5",            # <sigmas> or <threshold>,<ZP> in mag.arcsec-2

            "FILTER":            "Y",              # apply filter for detection (Y or N)?
            "FILTER_NAME":       "default.conv",   # name of the file containing the filter

            "DEBLEND_NTHRESH":   "32",             # Number of deblending sub-thresholds
            "DEBLEND_MINCONT":   "0.005",          # Minimum contrast parameter for deblending

            "CLEAN":             "Y",              # Clean spurious detections? (Y or N)?
            "CLEAN_PARAM":       "1.0",            # Cleaning efficiency

            "MASK_TYPE":         "CORRECT",        # type of detection MASKing: can be one of NONE, BLANK or CORRECT

            #------------------------------ Photometry -----------------------------------

            "PHOT_APERTURES":    "5",                # MAG_APER aperture diameter(s) in pixels
            "PHOT_AUTOPARAMS":   "2.5, 3.5",       # MAG_AUTO parameters: <Kron_fact>,<min_radius>
            "PHOT_PETROPARAMS":  "2.0, 3.5",       # MAG_PETRO parameters: <Petrosian_fact>, <min_radius>

            "SATUR_LEVEL":       "50000.0",          # level (in ADUs) at which arises saturation

            "MAG_ZEROPOINT":     "0.0",              # magnitude zero-point
            "MAG_GAMMA":         "4.0",              # gamma of emulsion (for photographic scans)
            "GAIN":              "0.0",              # detector gain in e-/ADU
            "PIXEL_SCALE":       "1.0",              # size of pixel in arcsec (0=use FITS WCS info)

            #------------------------- Star/Galaxy Separation ----------------------------

            "SEEING_FWHM":       "1.2",              # stellar FWHM in arcsec
            "STARNNW_NAME":      "default.nnw",    # Neural-Network_Weight table filename

            #------------------------------ Background -----------------------------------

            "BACK_SIZE":         "64",               # Background mesh: <size> or <width>,<height>
            "BACK_FILTERSIZE":   "3",                # Background filter: <size> or <width>,<height>

            "BACKPHOTO_TYPE":    "GLOBAL",         # can be GLOBAL or LOCAL

            #------------------------------ Check Photo ----------------------------------

            "CHECKIMAGE_TYPE":   "NONE",           # can be NONE, BACKGROUND, BACKGROUND_RMS,
                                                   # MINIBACKGROUND, MINIBACK_RMS, -BACKGROUND,
                                                   # FILTERED, OBJECTS, -OBJECTS, SEGMENTATION,
                                                   # or APERTURES
            "CHECKIMAGE_NAME":   "check.fits",     # Filename for the check-image

            #--------------------- Memory (change with caution!) -------------------------

            "MEMORY_OBJSTACK":   "3000",             # number of objects in stack
            "MEMORY_PIXSTACK":   "300000",           # number of pixels in stack
            "MEMORY_BUFSIZE":    "1024",             # number of lines in buffer
            #----------------------------- Miscellaneous ---------------------------------

            "VERBOSE_TYPE":      "NORMAL",         # can be QUIET, NORMAL or FULL
            "WRITE_XML":         "N",              # Write XML file (Y/N)?
            "XML_NAME":          "sex.xml"         # Filename for XML output
        }

    def setsensitivity(self, area, sigma):
        """
        Set star detection sensitivity.

        I have no idea what kind of numbers here should be. And of course it alters
        from image to image. This should hence be set while running the program and maybe tested as well.
        """

        self.config["DETECT_MINAREA"]  = str(area)
        self.config["DETECT_THRESH"]   = str(sigma)
        self.config["ANALYSIS_THRESH"] = str(sigma)    # This doesn't seem to affect to the number of stars detected

    def createconf(self):
        """
        Create configuration file for SExtractor.
        """

        f = open(self.confname, "w")
        for i in self.config:
            f.write(i + " " + self.config[i] + "\n")

    def findsensitivity(self):
        """
        Run SExtractor on different DETECT_MINAREA and THRESH, in order to find suitable number of stars.

        I'll choose 25 as minimum and 30 as maximum. There are about n^3 triangles for n vertices, so n should
        be kept small.
        """
        print("Looking for suitable DETECT_MINAREA...")
        x = 0
        min = 20
        max = 25

        while x > max or x < min:
            self.createconf()
            self.execsex()
            x = float(check_output(["tail", "-1", self.catname]).split()[0])
            if x < min:
                self.config["DETECT_MINAREA"] = str(float(self.config["DETECT_MINAREA"])*.9)
                self.config["DETECT_THRESH"] = str(float(self.config["DETECT_THRESH"])*.9)
                print("DETECT_MINAREA too big. Trying " + self.config["DETECT_MINAREA"])
            elif x > max:
                self.config["DETECT_MINAREA"] = str(float(self.config["DETECT_MINAREA"])*1.2)
                self.config["DETECT_THRESH"] = str(float(self.config["DETECT_THRESH"])*1.2)
                print("DETECT_MINAREA too small. Trying " + self.config["DETECT_MINAREA"])

        print("Found " + self.config["DETECT_MINAREA"] + " & " + self.config["DETECT_THRESH"])
        return self.config["DETECT_MINAREA"], self.config["DETECT_THRESH"]

    def execsex(self):
        """ Execute SExtractor with created conf """
        # TODO: try-except here about conf-file and other requirements
        print(self.imagepath)
        commandlist = [self.sextractor, self.imagepath, "-c", self.confname]

        call(commandlist, cwd=self.path)  # cwd changes working directory

    def getcoordinates(self):
        """
        Call everything necessary and return a set of XY-coordinates in a list
        """

        self.createconf()
        while True:
            self.execsex()

            self.coord = []
            f = open(self.catname, "r")
            for i in f:
                if i.split()[0] == "#":
                    pass
                else:
                    #self.coord.append((float(i.split()[4]), float(i.split()[5])))
                    self.coord.append([float(i.split()[4]), self.image.y - float(i.split()[5])])

            self.coord = sorted(self.coord)

            if (len(self.coord) < 17) or (len(self.coord) > 26):
                area, sigma = self.findsensitivity()
                self.setsensitivity(area, sigma)
            else:
                break

        return self.coord

    def maketriangles(self):
        """
        Make all possible triangles from coordinates in self.coord and save it to self.image.tri

        Result: image.tri = [[(x1,y1),(x2,y2),(x3,y3)], ... , ...]
        """

        self.image.tri = []
        n = 0
        #for i in self.coord:
        #    print(i)
        for i in self.coord:
            for j in self.coord:
                if i == j:
                    continue
                for k in self.coord:
                    if (j == k) or (i == k):
                        continue
                    n += 1
                    self.image.tri.append([i, j, k])

        print("Total number of triangles in image " + self.image.path + " is " + str(n) + ".")
