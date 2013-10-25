#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 23.10.2013

@author: Mikko Laine
'''

import numpy as np
import pyopencl as cl





class demosaic:
    '''
    Demosaicing class. I'll start with regular bilinear interpolation but more will come if necessary
    
    
    '''
    
    def __init__(self):
        self.ctx = cl.create_some_context()
        self.queue = cl.CommandQueue(self.ctx)
    
    def bilinear_cl(self, image):
        '''
        Bilinear interpolation using pyOpenCL
        '''
        mf = cl.mem_flags
        
        cfa = np.ravel(image.data)
        print(len(cfa))
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
          for (int i = 0; i < len; i++)                                         // conditions explained
          {       
             if (i < x || i%x == x-1 || i%x == 1 || i > len - x)  // upper border, right border, left border, lower border
             {
                c[gid] = a[gid];
             }
             else if ((i%2 == 0 && (i/x)%2 == 0) || (i%2 == 1 && (i/x)%2 == 1))   // even on even line, odd on odd line. Non-green pixels 
             {
                c[gid] = (a[gid-1] + a[gid-x] + a[gid+x] + a[gid+1])/4;
             }
             else                                                             // Green pixels
             {
                c[gid] = a[gid];
             }
          }
        } 
        
        """
        
        codered = codecommon + """
         for (int i = 0; i < len; i++)
         {
             if (i < x || i%x == x-1 || i%x == 1 || i > len - x)  // upper border, right border, left border, lower border
             {
                 c[gid] = a[gid];
             }
             else if (i%2 == 0 && (i/x)%2 == 0)
             {
                c[gid] = (a[gid-x] + a[gid +x]) /2;
             }
             else if (i%2 == 1 && (i/x)%2 == 1)
             {
                c[gid] = (a[gid-1] + a[gid+1]) /2;
             }
             else if ((i%2 == 0) && (i/x)%2 == 1)
             {
                c[gid] = a[gid];
             }
             else
             {
                c[gid] = (a[gid-1-x] + a[gid+1-x] + a[gid-1+x] + a[gid+1+x])/4;
             }
          }
        }
        """
        
        codeblue = codecommon + """
          for (int i = 0; i < len; i++)
          {
             if (i < x || i%x == x-1 || i%x == 1 || i > len - x)  // upper border, right border, left border, lower border
             {
                c[gid] = a[gid];
             }
             else if (i%2 == 0 && (i/x)%2 == 0)
             {
                c[gid] = (a[gid-1] + a[gid+1]) /2;
             }
             else if (i%2 == 1 && (i/x)%2 == 1)
             {
                c[gid] = (a[gid-len] + a[gid +len]) /2;
             }
             else if ((i%2 == 0) && (i/x)%2 == 1)
             {
                c[gid] = (a[gid-1-len] + a[gid+1-len] + a[gid-1+len] + a[gid+1+len])/4;
             }
             else
             {
                c[gid] = a[gid];
             }
          }
        }
        """
        
        prg_green = cl.Program(self.ctx, codegreen).build()
        prg_red   = cl.Program(self.ctx, codered  ).build()
        prg_blue  = cl.Program(self.ctx, codeblue ).build()

        
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
        
        r = np.reshape(image.x,-1)
        g = np.reshape(image.x,-1)
        b = np.reshape(image.x,-1)
        
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
        