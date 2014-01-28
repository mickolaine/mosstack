"""
Created on 2.10.2013

@author: Mikko Laine


"""

__author__ = 'Mikko Laine'

from .. Registering.Registering import Registering
from subprocess import call, check_output
from .. import Conf
from math import sqrt, log, fabs
from operator import itemgetter
from os.path import splitext
from re import sub
import datetime   # For profiling
import pyximport
import numpy as np
pyximport.install(setup_args={'include_dirs': [np.get_include()]})
from . _step2 import step2 as _step2



class Sextractor2(Registering):
    """
    Implementation of Registering interface. This class uses SExtractor to find stars on a picture and ImageMagick
    to perform affine transform accordingly. Star matching is done with method described by E.J. Groth on article
    'A pattern-matching algorithm for two-dimensional coordinate' (http://adsabs.harvard.edu/abs/1986AJ.....91.1244G)
    """

    def __init__(self):
        pass

    def register(self, imagelist, project):
        """
        Calls everything required for total registration process.
        """

        self.findstars(imagelist)

        ref = project.get("Reference images", "light")

        for i in imagelist:
            self.step1(imagelist[i])                      # Step1 has to be finished before the rest

        for i in imagelist:
            # Don't match image with itself
            if sub("\D", "", imagelist[i].number) == ref:  # For RGB-images i.number holds more than number. Strip that
                continue  # TODO: Copy the reference image. Now it's omitted

            t1 = datetime.datetime.now()

            #self.match(imagelist[ref], imagelist[i])
            #self.reduce(imagelist[i])
            #self.vote(imagelist[i])
            self.step2(imagelist[ref], imagelist[i])
            t2 = datetime.datetime.now()
            print("Triangle calculations took " + str(t2-t1) + " seconds.")

            newpath = self.transform_magick(imagelist[i], newname="reg")

            if len(newpath) == 3:
                for j in [0, 1, 2]:
                    project.set("Registered images", imagelist[i].number + imagelist[i].ccode[j], newpath[j])
            else:
                project.set("Registered images", imagelist[i].number, newpath)

    def findstars(self, imagelist):
        """
        Finds the stars and creates all the triangles from them
        """
        S = Sex(imagelist['1'])    # TODO: Ref image here
        sensitivity = S.findsensitivity()
        del S

        for i in imagelist:
            S = Sex(imagelist[i])
            S.setsensitivity(sensitivity[0], sensitivity[1])
            imagelist[i].coordinates = S.getcoordinates()
            S.maketriangles()

    def step1(self, image):
        """
        Calculates R,C,tR and tC for every triangle in image. These quantities are described in article #TODO: Cite the article

        Result image.tri = [[x1,y1,x2,y2,x3,y3, R, C, tR, tC], ... , ...]
        """

        ep = 0.3
        xi = 3. * ep

        newtri = []
        for tri in image.tri:      # tri is a list of coordinates. ((x1,y1),(x2,y2),(x3,y3))

            x1 = tri[0][0]
            y1 = tri[0][1]
            x2 = tri[1][0]
            y2 = tri[1][1]
            x3 = tri[2][0]
            y3 = tri[2][1]

            r3 = sqrt((x3 - x1) ** 2 + (y3 - y1) ** 2)
            r2 = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            R = r3 / r2
            C = ((x3 - x1) * (x2 - x1) + (y3 - y1) * (y2 - y1)) / (r3 * r2)     #Cosine of angle at vertex 1

            tR = sqrt(2. * R ** 2. * ep ** 2. * (1. / r3 ** 2. - C / (r2 * r3) + 1. / r2 ** 2.))

            S = 1. - C ** 2.   #Sine^2 of angle at vertex 1
            # S should be S**2 and on above line S should be sqrt of 1-C**2,
            # but this might be faster. I don't know if python optimizes this.
            tC = sqrt(2. * S * ep ** 2. * (1. / r3 ** 2. - C / (r2 * r3) + 1. / r2 ** 2.) +
                      3. * C ** 2. * ep ** 4. * (1. / r3 ** 2. - C / (r2 * r3) + 1. / r2 ** 2.) ** 2.)

            temp = [tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]]
            temp.append(R)
            temp.append(C)
            temp.append(tR)
            temp.append(tC)
            newtri.append(np.array(temp))
        image.tri = newtri

        print("Step 1 complete for image " + str(image.number) + ".")

    def step2(self, i1, i2):
        """
        An XXXXX implementation of the algorithm

        i1 and i2 have a list tri = [[(x1,y1),(x2,y2),(x3,y3), R, C, tR, tC], ... , ...]
        """

        print("Starting to match image " + str(i2.number) + " to reference image " + str(i1.number))

        i2.pairs = _step2(np.array(i1.tri), np.array(i2.tri))

    def match(self, i1, i2):
        """
        Matches triangles in image i1(ref) to triangles in i2. Creates a list of matching triangles and
        their properties in object i2.
        #TODO:Cite the article

        """

        print("Starting to match image " + str(i2.number) + " to reference image " + str(i1.number))
        #ep = 0.001
        #xi = 3 * ep

        for tri1 in i1.tri:
            temp = ()
            best = None        # temporary variable to hold information about the best R-ratio.
            for tri2 in i2.tri:

                Ra  = tri1[3]
                Rb  = tri2[3]
                tRa = tri1[5]
                tRb = tri2[5]
                Ca  = tri1[4]
                Cb  = tri2[4]
                tCa = tri1[6]
                tCb = tri2[6]

                # Run the check described in articles equations (7) and (8)
                if ((Ra - Rb) ** 2 < (tRa ** 2 + tRb ** 2)) & ((Ca - Cb) ** 2 < (tCa ** 2 + tCb ** 2)):
                    # print("Found! Ra-Rb = " + str((Ra-Rb)))   #Debugging

                    #Test if newfound match is better than the previous found with same tri1
                    if (best is None) or ((Ra-Rb)**2 < best):
                        #if so, save it for later use
                        best = (Ra-Rb)**2
                        temp = [tri1, tri2]
            if best is not None:
                # print("Adding triangles " + str(temp[0]) + " and " + str(temp[1]) + " as a match.")      # Debugging
                i2.match.append(temp)
            del temp
            del best
        print("Matching done for image " + str(i2.number) + ".")
        print("    " + str(len(i2.match)) + " matches found.")
        #print(i2.match)                #Debugging

    def reduce(self, image):
        """
        Reduces number of matched triangles. Essentially removes a portion of false matches. Probably no correct matches are removed.
        """

        for match in image.match:
            x1 = match[0][0][0]
            y1 = match[0][0][1]
            x2 = match[0][1][0]
            y2 = match[0][1][1]
            x3 = match[0][2][0]
            y3 = match[0][2][1]

            pA = (sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) +
                  sqrt((x1 - x3) ** 2 + (y1 - y3) ** 2) +
                  sqrt((x3 - x2) ** 2 + (y3 - y2) ** 2))

            x1 = match[1][0][0]
            y1 = match[1][0][1]
            x2 = match[1][1][0]
            y2 = match[1][1][1]
            x3 = match[1][2][0]
            y3 = match[1][2][1]

            pB = (sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) +
                  sqrt((x1 - x3) ** 2 + (y1 - y3) ** 2) +
                  sqrt((x3 - x2) ** 2 + (y3 - y2) ** 2))
            match.append(log(pA) - log(pB))         # Value log(M) as described in equation (10). this will be match[2]

        do_it_again = True
        print("List has originally lenght of  " + str(len(image.match)))

        times = 0

        while do_it_again:
            newlist = []
            mean = 0.
            variance = 0.
            for match in image.match:                       # Calculate average value
                mean += match[2] / len(image.match)
            for match in image.match:                       # Calculate variance which is sigma**2
                variance += (fabs(mean - match[2]) ** 2) / len(image.match)
            sigma = sqrt(variance)

            do_it_again = False
            for match in image.match:
                # print(match[2])                            #Debugging
                if fabs(match[2] - mean) < sigma * 2:
                    newlist.append(match)
                else:
                    do_it_again = True                        # If you end up here, while has to be run again
            image.match = newlist                           # Save new list and do again if necessary
            del newlist
            times += 1
        print("After reduction the length is " + str(len(image.match)))

    def vote(self, image):
        """
        Count probabilities for vertex matches. Choose the most popular one, disregard the rest.
        Votes mean how many times two vertices have been matched on previous steps. This is required
        to get rid of false matches. I probably need only few matching vertices so this method suites
        me well.

        Creates list image.pairs, which has pairs (image.coordinate, reference.coordinate, votes) sorted by votes, biggest first
        """
        print("Voting")
        pairs = {}          # vertex pair as the key and votes as the value

        for m in image.match:
            for i in range(3):
                key = (m[1][i], m[0][i])            # This is where source and destination changes places
                if key in pairs:
                    pairs[key] += 1
                else:
                    pairs[key] = 1

        newpairs = {}
        for key in pairs:
            if pairs[key] > 2:                      # Should be >1 but I really don't need that much points.
                newpairs[key] = pairs[key]          # TODO: Check if this works
        pairs = newpairs

        final = []
        for key in pairs:
            final.append((key[0], key[1], pairs[key]))

        final = sorted(final, key=itemgetter(2), reverse=True)
        image.pairs = final
        print("After voting there are " + str(len(image.pairs)) + " pairs found")

    def transform_magick(self, image, newname=None):
        """
        Transforms image according to image.pairs, but instead of skimage, this function uses
        ImageMagick's "convert -distort Affine" from command line.
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
        if image.rgb:
            newpath = ["", "", ""]
            for i in [0, 1, 2]:
                print(image.imagepath[i])
                newpath[i] = image.imagename + "_" + newname + "_" + image.ccode[i] + image.format
                command = "convert " + image.imagepath[i] + " -distort Affine "\
                          + points + " " + newpath[i]

                call([command], shell=True)

        else:
            newpath = image.imagename + "_" + newname + image.format
            command = "convert " + image.imagepath + " -distort Affine "\
                      + points + " " + newpath
            call([command], shell=True)

        return newpath


class Sex:
    """
    Class Sextractor controls SExtractor, obviously. Shortly, this class will extract xy-positions of stars from a fits.

    It creates a suitable configuration file, calls sextractor (or sex, have to check the name of the executable),
    checks and parses the output.
    """

    def __init__(self, image):
        """
        Initializes the object and common configuration values
        """

        self.image = image

        self.catname = self.image.imagename + ".cat"

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
        self.confname = self.image.imagename + ".sex"
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
        return (self.config["DETECT_MINAREA"], self.config["DETECT_THRESH"])

    def execsex(self):
        """ Execute SExtractor with created conf """
        # TODO: try-except here about conf-file and other requirements
        commandlist = [Conf.sex, splitext(self.image.imagepath[1])[0] + ".fits", "-c", self.confname]

        call(commandlist, cwd=Conf.path)  # cwd changes working directory

    def getcoordinates(self):
        """
        Call everything necessary and return a set of XY-coordinates in a list
        """

        self.createconf()
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
        return self.coord


    def maketriangles(self):
        """
        Make all possible triangles from coordinates in self.coord and save it to self.image.tri

        Result: image.tri = [[(x1,y1),(x2,y2),(x3,y3)], ... , ...]
        """

        self.image.tri = []
        n = 0
        for i in self.coord:
            for j in self.coord:
                if i == j:
                    break
                for k in self.coord:
                    if (j == k) or (i == k):
                        break
                    n += 1
                    self.image.tri.append([i, j, k])

        print("Total number of triangles in image " + self.image.imagename + str(self.image.number) + " is " + str(n) + ".")
