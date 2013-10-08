#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2.10.2013

@author: Mikko Laine

This file contains everything required for registering the photos.
'''

import numpy
from subprocess import call
from subprocess import check_output
import conf
import math

class Reg:
    '''
    Class Reg holds the math. Might be a static class to hold only functions called from elsewhere. We'll see... #TODO: Fix the description when you know.
    '''

    
    def __init__(self):
        pass


    def match(self, i1, i2):
        '''
        Matches image i1 to i2
        '''
        
        ep = 0.001
        xi = 3*ep
        
        for im in (i1,i2):  #TODO: Move this to a better place. It doesn't belong here.
            for tri in im.tri:      # tri is a list of coordinates. ((x1,y1),(x2,y2),(x3,y3))
                x1 = tri[0][0]
                y1 = tri[0][1]
                x2 = tri[1][0]
                y2 = tri[1][1]
                x3 = tri[2][0]
                y3 = tri[2][1]
                
                r3 = math.sqrt((x3-x1)**2 + (y3-y1)**2) 
                r2 = math.sqrt((x2-x1)**2 + (y2-y1)**2)
                
                R=r3/r2
                C=((x3-x1)*(x2-x1)+(y3-y1)*(y2-y1))/(r3*r2)
                
                tR = math.sqrt(2*R**2*ep**2*(1/r3**2 - C/(r2*r3) + 1/r2**2))
                
                S = math.sqrt(1-C**2)                  #Sine of angle at vertex 1
                
                tC = 2*S**2*ep**2*(1/r3**2 - C/(r2*r3) + 1/r2**2) + 3*C**2*ep**4*(1/r3**2 - C/(r2*r3) + 1/r2**2)**2
                
                tri.append(R)
                tri.append(C)
                tri.append(tR)
                tri.append(tC)
            
        
        
        
        
        
    
    """ Probably not needed. Remove when certain.
    def map(self, image, p):
        '''
        Creates a two colour map of given image. Limiting colour must be adjustable somehow. For now a by percentage p
        For now it only uses green channel to find luminosities of pixels. The goal is to find stars and I'm making
        a wild guess they're visible in each channel.
        '''
        
        new = numpy.array(numpy.zeros((image.x, image.y)), dtype=bool)
        
        
        for i in range(len(image.image.data[1])):      # 1 is for the green channel
            for j in range(len(image.image.data[1][i])):
                if image.image.data[1][i][j] > 65535.0*p:
                    new[i][j] = True
        
        return new
     """               


class Sextractor:
    '''
    Class Sextractor controls SExtractor, obviously. Shortly, this class will extract xy-positions of stars from a fits.
    
    It creates a suitable configuration file, calls sextractor (or sex, have to check the name of the executable),
    checks and parses the output.
    '''
    
    def __init__(self, image):
        '''
        Initializes the object and common configuration values
        '''
        
        self.image = image
        
        self.catname = conf.path + self.image.name + str(self.image.number) + ".cat"
        
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

#------------------------------ Check Image ----------------------------------

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

    def setSensitivity(self, area, sigma):
        '''
        Set star detection sensitivity. I have no idea what kind of numbers here should be. And of course it alters
        from image to image. This should hence be set while running the program and maybe tested as well.
        '''
        
        self.config["DETECT_MINAREA"]  = str(area)
        self.config["DETECT_THRESH"]   = str(sigma)
        self.config["ANALYSIS_THRESH"] = str(sigma)    # This doesn't seem to affect to the number of stars detected
        
    def createConf(self):
        '''
        Creates configuration file for SExtractor.
        '''
        self.confname = conf.path + self.image.name + str(self.image.number) + ".sex"
        f = open(self.confname, "w")
        for i in self.config:
            f.write(i + " " + self.config[i] + "\n")   

    def findSensitivity(self):
        '''
        Run SExtractor on different DETECT_MINAREA and THRESH, in order to find suitable number of stars.
        I'll choose 25 as minimum and 50 as maximum. There are about n^3 triangles for n vertices, so n should
        be kept small.
        '''
        print("Looking for suitable DETECT_MINAREA...")
        x = 0
        min = 25
        max = 50
        
        while x > max or x < min:
            self.createConf()
            self.execSEx()
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
        
        
    def execSEx(self):
        '''
        Executing SExtractor
        The attribute cwd is required because sextractor is looking for several files from current working directory
        '''
        commandlist = [conf.sex, self.image.fitspath, "-c", self.confname]
        
        call(commandlist, cwd=conf.path)
        
    def getCoordinates(self):
        '''
        Calls everything necessary and returns a set of XY-coordinates in a list
        '''
        
        self.createConf()
        self.execSEx()
 
        self.coord = []
        f = open(self.catname, "r")
        for i in f:
            if i.split()[0] == "#":
                pass
            else:
                self.coord.append((float(i.split()[4]), float(i.split()[5])))
        
        return self.coord 
    
    def makeTriangles(self):
        '''
        Makes all possible triangles from coordinates in self.coord
        #TODO: Maybe should do only some, but I'll see first how this works
        '''
        
        self.image.tri = []
        n = 0
        for i in self.coord:
            for j in self.coord:
                if i == j:
                    break
                for k in self.coord:
                    if (j == k) or (i == k):
                        break
                    n=n+1
                    self.image.tri.append([i, j, k])      #TODO: Check if this is enough information
        print("Total number of triangles in image " + self.image.name + str(self.image.number) + " is " + str(n) + ".")
    
    
    
class alingment:
    '''
    Class for alignment information of a photo
    '''
       
        
    def __init_(self, orientation = None):
        self.orientation = orientation