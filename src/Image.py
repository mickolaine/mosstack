'''
Created on 2.10.2013

@author: micko
'''

from astropy.io import fits
from os.path import splitext,basename,exists
from subprocess import call

class Image(object):
    '''
    classdocs
    '''

    def __init__(self, rawpath):
        '''
        Constructor requires a filename of a raw image. I have a Canon EOS 1100D so Canon CR2 is what I originally write this for.
        #TODO: Support for other raws
        '''
        self.rawpath  = rawpath
        self.convert()
        
        self.hdu      = fits.open(self.fitspath)
        self.image    = self.hdu[0]
        
        
    def isOK(self, image):
        '''
        Test whether astropy recognizes the image
        '''
        
        if image.is_image:
            return True
        
    def convert(self):
        '''
        Converts the raw into fits.
        '''
        
        self.fitspath = splitext(basename(self.rawpath))[0] + ".fits"
        if exists(self.rawpath):
            if call(["rawtran", "-o", self.filtsname, self.rawpath]):
                print("Something went wrong... There might be helpful output from Rawtran above this line.")
                print("File " + self.rawpath + " exists.")
                if exists(self.fitspath):
                    print("File " + self.fitspath + " exists.")
                    print("Here's information about it:")
                    #TODO: Check size and magic numbers with file utility
                else:
                    print("File " + self.fitspath + " does not. Unable to continue.")
                    exit() #TODO: Make it able to continue without this picture
        else:
            print("Unable to find file in given path: " + self.rawpath + ". Find out what's wrong and try again.")
            print("Can't continue. Exiting.")
            exit()

        



