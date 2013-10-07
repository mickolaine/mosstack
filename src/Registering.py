'''
Created on 2.10.2013

@author: Mikko Laine

This file contains everything required for registering the photos.
'''

import numpy

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
                    


class alingment:
    '''
    Class for alignment information of a photo
    '''
       
        
    def __init_(self, orientation = None):
        self.orientation = orientation