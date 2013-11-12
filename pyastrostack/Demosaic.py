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
        self.ctx = cl.create_some_context()

        self.queue = cl.CommandQueue(self.ctx)

    def bilinear_cl(self, image):
        """ Bilinear interpolation using pyOpenCL.

        Arguments:
        image - a pyAstroStack.Photo

        Returns:
        [red, green, blue] as numpy.array

        Interpolated image will be given to image via image.savergb()
        """
        mf = cl.mem_flags

        print("Processing image " + image.imagepath)

        cfa = np.ravel(np.float32(image.data), order='K')
        #print(len(cfa))
        cfa_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=cfa)

        dest_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, cfa.nbytes)
        
        codecommon = """
        __kernel void bilinear(__global const float *a, __global float *c)
        {
          int x = """ + str(image.x) + """;
          int len = """ + str(len(cfa)) + """;
          int gid = get_global_id(0);
          
        """
        
        codegreen = codecommon + """
                                                                          // conditions explained      
             if (gid < x || gid%x == 0 || gid%x == 1 || gid > len - x)    // upper border, right, left and lower border
             {
                c[gid] = a[gid];
             }
             else if ((gid%2 == 0 && (gid/x)%2 == 0) ||                   // Non-green pixels
                      (gid%2 == 1 && (gid/x)%2 == 1))                     // even on even line, odd on odd line.
             {
                c[gid] = (a[gid-1] + a[gid-x] + a[gid+x] + a[gid+1])/4;
             }
             else                                                         // Green pixels. Should be all the rest
             {
                c[gid] = a[gid];
             }
        }

        
        """
        
        codered = codecommon + """

             if (gid < x || gid%x == 0 || gid%x == 1 || gid > len - x)  // upper border, right, left and lower border
             {
                 c[gid] = a[gid];
             }
             else if (gid%2 == 0 && (gid/x)%2 == 0)            // Red pixels
             {
                c[gid] = a[gid];
             }
             else if (gid%2 == 1 && (gid/x)%2 == 1)            // Blue pixels
             {
                c[gid] = (a[gid-1-x] + a[gid+1-x] + a[gid-1+x] + a[gid+1+x])/4;
             }
             else if ((gid%2 == 0) && (gid/x)%2 == 1)          // Green pixels, reds on sides 
             {
                c[gid] = (a[gid-x] + a[gid +x]) /2;
             }
             else if ((gid%2 == 1) && (gid/x)%2 == 0)          // Green pixel, blues on side
             {
                c[gid] = (a[gid-1] + a[gid+1]) /2;
             }
             else                                              // You shouldn't end here. Just in case
             {
                c[gid] = a[gid];
             }
        }
        """
        
        codeblue = codecommon + """
             if (gid < x || gid%x == 0 || gid%x == 1 || gid > len - x)  // upper border, right, left and lower border
             {
                c[gid] = a[gid];
             }
             else if (gid%2 == 0 && (gid/x)%2 == 0)            // Red pixels
             {
                c[gid] = (a[gid-1-x] + a[gid+1-x] + a[gid-1+x] + a[gid+1+x])/4;
             }
             else if (gid%2 == 1 && (gid/x)%2 == 1)            // Blue pixels
             {
                c[gid] = a[gid];
             }
             else if ((gid%2 == 0) && (gid/x)%2 == 1)          // Green pixels, reds on sides
             {
                c[gid] = (a[gid-1] + a[gid+1]) /2;
             }
             else if ((gid%2 == 1) && (gid/x)%2 == 0)          // Green pixel, blues on side
             {
                c[gid] = (a[gid-x] + a[gid +x]) /2;
             }
             else                                              // You shouldn't end here. Just in case
             {
                c[gid] = a[gid];
             }
        }
        """
        
        prg_green = cl.Program(self.ctx, codegreen).build()
        prg_red   = cl.Program(self.ctx, codered  ).build()
        prg_blue  = cl.Program(self.ctx, codeblue ).build()

        prg_green.bilinear(self.queue, cfa.shape, None, cfa_buf, dest_buf)
        g = np.empty_like(cfa)
        cl.enqueue_copy(self.queue, g, dest_buf)
        
        dest_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, cfa.nbytes)     # Reset dest_buf just in case. Maybe not necessary
        prg_red.bilinear(self.queue, cfa.shape, None, cfa_buf, dest_buf)
        r = np.empty_like(cfa)
        cl.enqueue_copy(self.queue, r, dest_buf)
        
        dest_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, cfa.nbytes)     # Reset dest_buf just in case. Maybe not necessary
        prg_blue.bilinear(self.queue, cfa.shape, None, cfa_buf, dest_buf)
        b = np.empty_like(cfa)
        cl.enqueue_copy(self.queue, b, dest_buf)
        #print(r)
        r = np.reshape(r, (image.y, -1), order='K')
        g = np.reshape(g, (image.y, -1), order='K')
        b = np.reshape(b, (image.y, -1), order='K')
        #print("After reshape: " + str(g.shape))
        print("...Done")
        return np.array([r, g, b])
        #image.savergb(np.array([r, g, b]))
    
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
        r = np.reshape(r,(image.y,-1),order='K')
        g = np.reshape(g,(image.y,-1),order='K')
        b = np.reshape(b,(image.y,-1),order='K')
        print("After reshape: " + str(g.shape))
        print(g)
        image.savergb(np.array([r,g,b]))
    
    
    
    
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
        
        
        
        
        
    def LRP_cl(self, image):
        """ LaRoche-Prescott interpolation using pyOpenCL. NOT IMPLEMENTED YET!

        Arguments:
        image - a pyAstroStack.Photo

        Returns:
        Nothing

        Interpolated image will be given to image via image.savergb()
        """
        mf = cl.mem_flags
        
        cfa = np.ravel(image.data)
        print(len(cfa))
        cfa_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=cfa)

        dest_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, cfa.nbytes)
        
        codecommon = """
        #include <math.h>
        __kernel void bilinear(__global const float *a, __global float *c)
        {
          int x = """ + str(image.x) + """;
          int len = """ + str(len(cfa)) + """;
          int gid = get_global_id(0);
          
        """
        # Green is implemented
        codegreen = codecommon + """
                                                                          // conditions explained      
             if (gid < x || gid%x == x-1 || gid%x == 1 || gid > len - x)  // upper border, right, left, lower border
             {
                c[gid] = a[gid];
             }
             else if ((gid%2 == 0 && (gid/x)%2 == 0) ||                   // Non-green pixels
                      (gid%2 == 1 && (gid/x)%2 == 1))                     // even on even line, odd on odd line.
             {
                alpha = fabs((a[gid-2]+a[gid+2])/2 - a[gid]);
                beta  = fabs((a[gid-2*x]+a[gid+2*x])/2 - a[gid]);
                if (alpha < beta) {
                    c[gid] = (a[gid-1]+a[gid+1])/2;
                }
                else if (alpha > beta) {
                    c[gid] = (a[gid-x]+a[gid+x])/2;
                }
                else {
                    c[gid] = (a[gid-1] + a[gid-x] + a[gid+x] + a[gid+1])/4;
                }
             }
             else                                                         // Green pixels
             {
                c[gid] = a[gid];
             }
        }

        
        """
        # Red is not implemented
        codered = codecommon + """

             if (gid < x || gid%x == x-1 || gid%x == 1 || gid > len - x)  // upper border, right, left, lower border
             {
                 c[gid] = a[gid];
             }
             else if (gid%2 == 0 && (gid/x)%2 == 0)
             {
                c[gid] = (a[gid-x] + a[gid +x]) /2;
             }
             else if (gid%2 == 1 && (gid/x)%2 == 1)
             {
                c[gid] = (a[gid-1] + a[gid+1]) /2;
             }
             else if ((gid%2 == 0) && (gid/x)%2 == 1)
             {
                c[gid] = a[gid];
             }
             else
             {
                c[gid] = (a[gid-1-x] + a[gid+1-x] + a[gid-1+x] + a[gid+1+x])/4;
             }
        }
        """
        # Blue is not implemented
        codeblue = codecommon + """
             if (gid < x || gid%x == x-1 || gid%x == 1 || gid > len - x)  // upper border, right, left, lower border
             {
                c[gid] = a[gid];
             }
             else if (gid%2 == 0 && (gid/x)%2 == 0)
             {
                c[gid] = (a[gid-1] + a[gid+1]) /2;
             }
             else if (gid%2 == 1 && (gid/x)%2 == 1)
             {
                c[gid] = (a[gid-x] + a[gid +x]) /2;
             }
             else if ((gid%2 == 0) && (gid/x)%2 == 1)
             {
                c[gid] = (a[gid-1-x] + a[gid+1-x] + a[gid-1+x] + a[gid+1+x])/4;
             }
             else
             {
                c[gid] = a[gid];
             }
        }
        """
        
        prg_green = cl.Program(self.ctx, codegreen).build()
        prg_red   = cl.Program(self.ctx, codered  ).build()
        prg_blue  = cl.Program(self.ctx, codeblue ).build()

        
        prg_green.bilinear(self.queue, cfa.shape, None, cfa_buf, dest_buf)
        g = np.empty_like(cfa)
        cl.enqueue_copy(self.queue, g, dest_buf)
        
        dest_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, cfa.nbytes)    # Reset dest_buf just in case. Maybe not necessary
        prg_red.bilinear(self.queue, cfa.shape, None, cfa_buf, dest_buf)
        r = np.empty_like(cfa)
        cl.enqueue_copy(self.queue, r, dest_buf)
        
        dest_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, cfa.nbytes)    # Reset dest_buf just in case. Maybe not necessary
        prg_blue.bilinear(self.queue, cfa.shape, None, cfa_buf, dest_buf)
        b = np.empty_like(cfa)
        cl.enqueue_copy(self.queue, b, dest_buf)
        
        r = np.reshape(image.x,-1)
        g = np.reshape(image.x,-1)
        b = np.reshape(image.x,-1)
        
        image.savergb(np.array([r,g,b]))
        