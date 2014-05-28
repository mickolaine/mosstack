"""
Created on 2.10.2013

@author: Mikko Laine


"""

#from .. Registering.Registering import Registering
from subprocess import call, check_output
from .. Config import Global
#from math import sqrt, log, fabs
#from operator import itemgetter
from os.path import splitext, isfile
#from re import sub
#from shutil import copyfile
#import datetime   # For profiling


class Sextractor:
    """
    Class Sextractor controls SExtractor, obviously. Shortly, this class will extract xy-positions of stars from a fits.

    It creates a suitable configuration file, calls sextractor (or sex, have to check the name of the executable),
    checks and parses the output.

    TODO: Test for SExtractor version: 2.4.4 has a bug
    """

    def __init__(self, image, project):
        """
        Initializes the object and common configuration values
        """

        self.image = image
        self.sextractor = Global.get("Programs", "sextractor")
        self.path = image.wdir
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

    def extracting_done(self):
        """
        Check if star catalog has already been extracted for this project. No need to do it again.

        Returns boolean
        """
        try:
            return isfile(self.image.frameinfo.get("Paths", "catalog"))
        except KeyError:
            return False

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
        print(self.imagepath)
        commandlist = [self.sextractor, self.imagepath, "-c", self.confname]

        call(commandlist, cwd=self.path)  # cwd changes working directory

    def getcoordinates(self):
        """
        Call everything necessary and return a set of XY-coordinates in a list
        """

        if self.extracting_done():
            self.coord = []
            f = open(self.catname, "r")
            for i in f:
                if i.split()[0] == "#":
                    pass
                else:
                    self.coord.append((float(i.split()[4]), float(i.split()[5])))
                    #self.coord.append([float(i.split()[4]), self.image.y - float(i.split()[5])])

            self.coord = sorted(self.coord)
            return self.coord

        self.createconf()
        while True:
            self.execsex()

            self.coord = []
            f = open(self.catname, "r")
            for i in f:
                if i.split()[0] == "#":
                    pass
                else:
                    self.coord.append((float(i.split()[4]), float(i.split()[5])))
                    #self.coord.append([float(i.split()[4]), self.image.y - float(i.split()[5])])

            self.coord = sorted(self.coord)

            if (len(self.coord) < 17) or (len(self.coord) > 26):
                area, sigma = self.findsensitivity()
                self.setsensitivity(area, sigma)
            else:
                self.image.frameinfo.set("Paths", "catalog", self.catname)
                break

        return self.coord

    def gettriangles(self):
        """
        Make all possible triangles from coordinates in self.coord and save it to self.image.tri

        Result: image.tri = [[(x1,y1),(x2,y2),(x3,y3)], ... , ...]
        """

        tri = []
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
                    tri.append([i, j, k])

        print("Total number of triangles in image " + self.image.path + " is " + str(n) + ".")

        return tri