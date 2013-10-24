#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 23.10.2013

@author: Mikko Laine
'''

import numpy as np





class demosaic:
    '''
    Demosaicing class. I'll start with regular bilinear interpolation but more will come if necessary
    
    
    '''
    
    def __init__(self):
        pass
    
    
    
    
    def bilinear(self, image):
        '''
        Bilinear interpolation for demosaicing CFA
        Now assumes order of GR
                             BG
                             
        Give image, recieve rgb-image. Doesn't return anything. Writes image as rgb#.tiff
        '''
        
        
        r = np.empty_like(image.data)
        g = r.copy()
        b = r.copy()
        cfa = image.data
        
        # Green pixels are interpolated first
        for i in range(len(image.data)):
            for j in range(len(image.data[i])):
                if i==0 or i == len(image.data)-1 or j == 0 or j == len(image.data[i])-1:           #TODO: Better border handling
                    g[i][j] = cfa[i][j]
                elif ((i%2 == 0) & (j%2 == 0)) or ((i%2 == 1) & (j%2 == 1)):                      #Test, when non-green pixel
                    g[i][j] = (cfa[i-1][j] + cfa[i][j-1] + cfa[i][j+1] + cfa[i+1][j])/4
                else:                                                                           #For the green pixels
                    g[i][j] = cfa[i][j]
                    
        #
        for i in range(len(image.data)):
            for j in range(len(image.data[i])):                     #TODO: Check the order of matrix
                if i == 0 or i == len(image.data)-1 or j == 0 or j == len(image.data[i])-1:           #TODO: Better border handling
                    r[i][j] = cfa[i][j]
                    b[i][j] = cfa[i][j]
                elif ((i%2 == 0) & (j%2 == 0)):                                   # At green on red row
                    r[i][j] = (cfa[i][j-1] + cfa[i][j+1]) /2
                    b[i][j] = (cfa[i-1][j] + cfa[i+1][j]) /2
                elif ((i%2 == 1) & (j%2 == 1)):                                 # At green on blue row
                    r[i][j] = (cfa[i-1][j] + cfa[i+1][j]) /2
                    b[i][j] = (cfa[i][j-1] + cfa[i][j+1]) /2
                elif ((i%2 == 0) & (j%2 == 1)):                                 # At red position
                    r[i][j] = cfa[i][j]
                    b[i][j] = (cfa[i-1][j-1] + cfa[i-1][j+1] + cfa[i+1][j-1] + cfa[i+1][j+1])/4
                elif ((i%2 == 1) & (j%2 == 0)):                                 # At blue position
                    r[i][j] = (cfa[i-1][j-1] + cfa[i-1][j+1] + cfa[i+1][j-1] + cfa[i+1][j+1])/4
                    b[i][j] = cfa[i][j]
        
        image.savergb(np.array([r,g,b]))
        