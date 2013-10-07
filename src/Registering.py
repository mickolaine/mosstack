'''
Created on 2.10.2013

@author: Mikko Laine

This file contains everything required for registering the photos.
'''

import numpy
from subprocess import call
import conf

class Reg:
    '''
    Class Reg holds the math. Might be a static class to hold only functions called from elsewhere. We'll see... #TODO: Fix the description when you know.
    '''

    
    def __init__(self):
        pass

    
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
        
        self.catname = "cat-" + image.name + image.number + ".cat"
        
        self.config = {
#-------------------------------- Catalog ------------------------------------                       
                       "CATALOG_NAME":      self.catname      # name of the output catalog
                       "CATALOG_TYPE":      "ASCII_HEAD",     # NONE,ASCII,ASCII_HEAD, ASCII_SKYCAT,
                                                              # ASCII_VOTABLE, FITS_1.0 or FITS_LDAC
                       "PARAMETERS_NAME":   "default.param",  # name of the file containing catalog contents

#------------------------------- Extraction ----------------------------------             
                       "DETECT_TYPE":       "CCD",            # CCD (linear) or PHOTO (with gamma correction)
                       "DETECT_MINAREA":    "10",             # minimum number of pixels above threshold
                       "DETECT_THRESH":     "2.5",            # <sigmas> or <threshold>,<ZP> in mag.arcsec-2
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
        self.config["ANALYSIS_THRESH"] = str(sigma)
        
    def createConf(self):
        '''
        Creates configuration file for SExtractor.
        '''
        self.confname = conf.path + image.name + image.number + ".sex"
        f = open(self.confname, "w")
        for i in self.config:
            f.write(i + " " + self.config[i])   
        
    def execSEx(self):
        '''
        Executing SExtractor
        '''
        
        call([conf.sex, image.fitspath, "-c", self.confname])
        
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
                self.coord.append(float(i.split()[4]), float(i.split()[5]))
        
        return self.coord 
                
class alingment:
    '''
    Class for alignment information of a photo
    '''
       
        
    def __init_(self, orientation = None):
        self.orientation = orientation