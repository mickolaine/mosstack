#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 23.10.2013

@author: Mikko Laine
"""

import numpy as np
import pyopencl as cl


class Demosaic:
    """
    Demosaicing class. I'll start with regular bilinear interpolation but more will come if necessary

    """
    
    def __init__(self):
        """Prepare everything for running the demosaic-algorithms."""
        pass

    def demosaic(self, image):
        """

        Arguments:
        image - a pyAstroStack.Photo

        Returns:
        [red, green, blue] as numpy.array

        Interpolated image will be given to image via image.savergb()
        """

    #TODO: Remove everything after this
    def opencl_test(self, image):
        """
        Identity function to test opencl.

        Arguments:
        image - a pyAstroStack.Photo

        Returns:
        Nothing

        Saves the grayscale image data times three with image.savergb(). No interpolation done.
        """
        mf = cl.mem_flags
        
        print("Before raveling: " + str(image.data.shape))
        print(image.data)
        
        cfa = np.ravel(np.float32(image.data), order='K')
        print("After raveling: " + str(cfa.shape))
        print(cfa)
        cfa_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=cfa)

        dest_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, cfa.nbytes)
        
        codecommon = """
        __kernel void bilinear(__global const float *a, __global float *c)
        {
          int x = """ + str(image.y) + """;
          int len = """ + str(len(cfa)) + """;
          int gid = get_global_id(0);
          
        """
        
        codegreen = codecommon + """
                                                                          // conditions explained      
            c[gid] = a[gid];
            
        }

        
        """
        
        prg_green = cl.Program(self.ctx, codegreen).build()
        prg_red   = cl.Program(self.ctx, codegreen).build()
        prg_blue  = cl.Program(self.ctx, codegreen).build()

        prg_green.bilinear(self.queue, cfa.shape, None, cfa_buf, dest_buf)
        g = np.empty_like(cfa)
        cl.enqueue_copy(self.queue, g, dest_buf)
        
        dest_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, cfa.nbytes)       # Reset dest_buf just in case. Maybe not necessary
        prg_red.bilinear(self.queue, cfa.shape, None, cfa_buf, dest_buf)
        r = np.empty_like(cfa)
        cl.enqueue_copy(self.queue, r, dest_buf)
        
        dest_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, cfa.nbytes)       # Reset dest_buf just in case. Maybe not necessary
        prg_blue.bilinear(self.queue, cfa.shape, None, cfa_buf, dest_buf)
        b = np.empty_like(cfa)
        cl.enqueue_copy(self.queue, b, dest_buf)
        print("After CL: " + str(g.shape))
        print(g)
        r = np.reshape(r, (image.y, -1), order='K')
        g = np.reshape(g, (image.y, -1), order='K')
        b = np.reshape(b, (image.y, -1), order='K')
        print("After reshape: " + str(g.shape))
        print(g)
        image.savergb(np.array([r, g, b]))

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
        
        return np.array([r, g, b])