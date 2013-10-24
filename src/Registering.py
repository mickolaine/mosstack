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
from math import sqrt, log, fabs, acos
from operator import itemgetter
from scipy.ndimage.interpolation import affine_transform
#from skimage import data                                   #COMMENTING OUT, WILL BE REMOVED
#from skimage import transform as tf
from os.path import splitext

class Reg:
    '''
    Class Reg holds the math. 
    '''

    
    def __init__(self):
        
        pass
    
    def register(self, batch):
        '''
        Calls everything required for total registration process.
        '''
        self.findstars(batch)
        
        for i in batch.list:
            self.step1(i)                      # Step1 has to be finished before the rest
            
        ref = 0
        batch.setRef(ref)
      
        for i in batch.list:
            if i.number == batch.refnum:       # No need to match image with itself
                continue

            self.match(batch.refimg(), i)
            self.reduce(i)
            self.vote(i)
            self.transform_magick(i, newname = "reg")
            #self.transform(i)
            #i.setname("reg")
            #i.write()
            i.reload("reg")                    # Loads image from name "reg" and forgets the previous one
    

    def findstars(self, batch):
        '''
        Finds the stars and creates all the triangles from them
        '''
        S = Sextractor(batch.list[0])
        sensitivity = S.findSensitivity()
        del S
        
        for i in batch.list:
            S = Sextractor(i)
            S.setSensitivity(sensitivity[0], sensitivity[1])
            i.coordinates = S.getCoordinates()
            S.makeTriangles()

    def step1(self, image):
        '''
        Calculates R,C,tR and tC for every triangle in image. These quantities are described in article #TODO: Cite the article
        '''
        
        ep = 0.3
        xi = 3.*ep
        
        for tri in image.tri:      # tri is a list of coordinates. ((x1,y1),(x2,y2),(x3,y3))
            x1 = tri[0][0]
            y1 = tri[0][1]
            x2 = tri[1][0]
            y2 = tri[1][1]
            x3 = tri[2][0]
            y3 = tri[2][1]
            
            r3 = sqrt((x3-x1)**2 + (y3-y1)**2) 
            r2 = sqrt((x2-x1)**2 + (y2-y1)**2)
            
            R=r3/r2
            C=((x3-x1)*(x2-x1)+(y3-y1)*(y2-y1))/(r3*r2)     #Cosine of angle at vertex 1
            
            tR = sqrt(2.*R**2.*ep**2.*(1./r3**2. - C/(r2*r3) + 1./r2**2.))
            
            S = 1.-C**2.                                    #Sine^2 of angle at vertex 1
                       #      V----- S should be S**2 and on above line S should be sqrt of 1-C**2, but this might be faster. I don't know if python optimizes this. 
            tC = sqrt(2.*S*ep**2.*(1./r3**2. - C/(r2*r3) + 1./r2**2.) + 3.*C**2.*ep**4.*(1./r3**2. - C/(r2*r3) + 1./r2**2.)**2.)
            
            tri.append(R)
            tri.append(C)
            tri.append(tR)
            tri.append(tC)
        print("Step 1 complete for image " + str(image.number) + ".")
                

    def match(self, i1, i2):
        '''
        Matches triangles in image i1(ref) to triangles in i2. Creates a list of matching triangles and
        their properties in object i2.
        #TODO:Cite the article
        
        '''
        
        print("Starting to match image " + str(i2.number) + " to reference image " + str(i1.number))
        ep = 0.001
        xi = 3*ep            
        
        for tri1 in i1.tri:
            temp = ()
            best = None        #temporary variable to hold information about the best R-ratio.
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
                if ((Ra-Rb)**2 < (tRa**2 + tRb**2)) & ((Ca-Cb)**2 < (tCa**2 + tCb**2)):
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
        '''
        Reduces number of matched triangles. Essentially removes a portion of false matches. Probably no correct matches are removed.
        '''
        
        for match in image.match:
            x1 = match[0][0][0]
            y1 = match[0][0][1]
            x2 = match[0][1][0]
            y2 = match[0][1][1]
            x3 = match[0][2][0]
            y3 = match[0][2][1]
            
            pA = (sqrt((x1-x2)**2+(y1-y2)**2) + sqrt((x1-x3)**2+(y1-y3)**2) + sqrt((x3-x2)**2+(y3-y2)**2))
            
            x1 = match[1][0][0]
            y1 = match[1][0][1]
            x2 = match[1][1][0]
            y2 = match[1][1][1]
            x3 = match[1][2][0]
            y3 = match[1][2][1]
            
            pB = (sqrt((x1-x2)**2+(y1-y2)**2) + sqrt((x1-x3)**2+(y1-y3)**2) + sqrt((x3-x2)**2+(y3-y2)**2))
            match.append(log(pA) - log(pB))         # Value log(M) as described in equation (10). this will be match[2]
            
                
        doItAgain = True
        print("List has originally lenght of  " + str(len(image.match)))
        
        times = 0
        
        while doItAgain:
            newlist = []
            mean = 0.
            variance = 0.
            for match in image.match:                       # Calculate average value
                mean = mean + match[2]/len(image.match)
            for match in image.match:                       # Calculate variance which is sigma**2
                variance = variance + (fabs(mean - match[2])**2)/len(image.match)
            sigma = sqrt(variance)
            
            doItAgain = False
            for match in image.match:
                # print(match[2])                            #Debugging
                if fabs(match[2] - mean) < sigma*2:
                    newlist.append(match)
                else:
                    doItAgain = True                        # If you end up here, while has to be run again
            image.match = newlist                           # Save new list and do again if necessary
            del newlist
            times = times + 1
        print("After reduction the length is " + str(len(image.match)))            
    
    
    def vote(self, image):
        '''
        Count probabilities for vertex matches. Choose the most popular one, disregard the rest.
        Votes mean how many times two vertices have been matched on previous steps. This is required
        to get rid of false matches. I probably need only few matching vertices so this method suites
        me well.
        
        Creates list image.pairs, which has pairs (image.coordinate, reference.coordinate, votes) sorted by votes, biggest first
        '''
        print("Voting")
        pairs = {}          # vertex pair as the key and votes as the value
        
        for m in image.match:
            for i in range(3):
                key = (m[1][i], m[0][i])            # This is where source and destination changes places
                if key in pairs:
                    pairs[key] = pairs[key] + 1
                else:
                    pairs[key] = 1
        
        newpairs = {}
        for key in pairs:
            if pairs[key] > 2:                      # Should be >1 but I really don't need that much points. # TODO: Check if this works
                newpairs[key] = pairs[key]
        pairs = newpairs

        final=[]
        for key in pairs:
            final.append((key[0], key[1], pairs[key]))
        
        final = sorted(final, key=itemgetter(2), reverse=True)
        image.pairs = final
        print("After voting there are " + str(len(image.pairs)) + " pairs found")
        #for p in image.pairs:
        #    print(p)
            
    
    def transform_magick(self, image, newname = None):
        '''
        Transforms image according to image.pairs, but insted of skimage, this function uses
        ImageMagick's "convert -distort Affine" from command line.
        #TODO: Check if this could be done with python-bindings of imagemagick
        '''
        points = "'"
        n = 0
        for i in image.pairs:
            if n > 11:          # max number of control points is 12
                break
            #print(i)
            #print("{},{},{},{} ".format(i[0][0],i[0][1],i[1][0],i[1][1]))
            points = points + "{},{},{},{} ".format(int(i[0][0]),int(i[0][1]),int(i[1][0]),int(i[1][1]))
            n += 1
        points = points + "'"
        if newname is None:
            newpath = image.imagepath
        else:
            newpath = conf.path + newname + str(image.number) + "." + image.format
        #cmd = "convert " +  image.imagepath + " -define quantum:format=unsigned -depth 16 -distort Perspective " + points + " " + newpath
        cmd = "convert " +  image.imagepath + " -depth 16 -distort Perspective " + points + " " + newpath
        call([cmd], shell=True)
        
           
        
    """    COMMENTING OUT. WILL BE REMOVED
    def transform(self, image):
        '''
        Rotates and translates the image. Uses transform in scikit-image
        '''
        
        trans = self.transformMatrix(image)
        #print(image.data)
        new = image.data.copy()
        
        maximum = numpy.amax(new)
        scalar = 65536.
        
        if maximum > scalar:
            scalar = maximum
        
        new = new/scalar
        new = tf.warp(new, trans)
        new = new*scalar
        
        image.newdata(new)
        ""
        r = image.data[0]
        g = image.data[1]
        b = image.data[2]
        
        maximum = numpy.amax(image.data)
        scalar = 65536.
        
        if maximum > scalar:
            scalar = maximum
        
        r = r/scalar                # warp needs float values between -1 and 1.
        print(str(numpy.amax(r)))
        print(str(numpy.amin(r)))
        
        
        r = tf.warp(r, trans)
        r = r*scalar                # I only hope this won't lose precision
        
        g = g/scalar
        g = tf.warp(g, trans)
        g = g*scalar
        
        b = b/scalar
        b = tf.warp(b, trans)
        b = b*scalar                #In the end values should be signed int16, so only multiply them

        image.newdata([r, g, b])        
        "
        
    def transformMatrix(self, image):
        '''
        Estimate transforming matrix using image.pairs
        '''
        
        src = []
        dst = []
        for i in image.pairs:
            src.append(i[1])
            dst.append(i[0])
        
        src = numpy.array(src)
        dst = numpy.array(dst)
        
        tform = tf.estimate_transform(ttype="affine", src=src, dst=dst)
        
        return tform
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
        max = 30                #TODO: Max value has to be lower than 50. looking for optimal. 30 seems to make batch of 30 images last only 4 minutes. that's quite good
        
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
        
        commandlist = [conf.sex, splitext(self.image.imagepath)[0] + ".fits", "-c", self.confname]
        
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
                self.coord.append((float(i.split()[4]), self.image.y - float(i.split()[5])))
        
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
