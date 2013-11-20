__author__ = 'micko'

from Demosaic.Demosaic import Demosaic
import numpy as np
import pyopencl as cl


class BilinearCl(Demosaic):
    """
    Demosaicing class. I'll start with regular bilinear interpolation but more will come if necessary

    """

    def __init__(self):
        """Prepare everything for running the demosaic-algorithms."""
        self.ctx = cl.create_some_context()

        self.queue = cl.CommandQueue(self.ctx)

    def demosaic(self, image):
        """ Bilinear interpolation using pyOpenCL.

        Arguments:
        image - a pyAstroStack.Photo

        Returns:
        [red, green, blue] as numpy.array

        Interpolated image will be given to image via image.savergb()
        """
        mf = cl.mem_flags

        print("Processing image " + image.imagepath)

        cfar = np.ravel(np.float32(image.data), order='C')
        cfag = np.ravel(np.float32(image.data), order='C')
        cfab = np.ravel(np.float32(image.data), order='C')



        codecommon = """
        __kernel void bilinear(__global const float *a, __global float *c)
        {
          int x = """ + str(image.x) + """;
          int len = """ + str(len(cfar)) + """;
          int gid = get_global_id(0);

        """

        codegreen = codecommon + """
                                                                          // conditions explained
             if (gid < x || gid%x == 0 || gid%x == x-1 || gid > len - x)    // upper border, right, left and lower border
             {
                c[gid] = a[gid];
             }
             else if ((gid%2 == 0 && (gid/x)%2 == 0) ||                   // Green pixels.
                      (gid%2 == 1 && (gid/x)%2 == 1))                     // even on even line, odd on odd line.
             {
                c[gid] = a[gid];
             }
             else                                                         // Non-green pixels. Should be all the rest
             {
                c[gid] = (a[gid-1] + a[gid-x] + a[gid+x] + a[gid+1])/4;
                //c[gid] = 0.0;
             }
        }


        """

        codeblue = codecommon + """

             if (gid < x || gid%x == 0 || gid%x == x-1 || gid > len - x)  // upper border, right, left and lower border
             {
                c[gid] = a[gid];
             }
             else if ((gid%2 == 1) && (gid/x)%2 == 0)            // Red pixels
             {
                c[gid] = a[gid];
             }
             else if ((gid%2 == 0) && (gid/x)%2 == 1)            // Blue pixels
             {
                c[gid] = (a[gid-1-x] + a[gid+1-x] + a[gid-1+x] + a[gid+1+x])/4;
                //c[gid] = 0.0;
             }
             else if (gid%2 == 1 && (gid/x)%2 == 1)          // Green pixels, reds on sides
             {
                c[gid] = (a[gid-x] + a[gid +x]) /2;
                //c[gid] = 0.0;
             }
             else if (gid%2 == 0 && (gid/x)%2 == 0)          // Green pixel, blues on side
             {
                c[gid] = (a[gid-1] + a[gid+1]) /2;
                //c[gid] = 0.0;
             }
             else                                              // You shouldn't end here. Just in case
             {
                c[gid] = a[gid];
             }
        }
        """

        codered = codecommon + """
             if (gid < x || gid%x == 0 || gid%x == x-1 || gid > len - x)  // upper border, right, left and lower border
             {
                c[gid] = a[gid];
                //c[gid] = 0.0;
             }
             else if ((gid%2 == 1) && (gid/x)%2 == 0)            // Red pixels
             {
                c[gid] = (a[gid-1-x] + a[gid+1-x] + a[gid-1+x] + a[gid+1+x])/4;
                //c[gid] = 0.0;
             }
             else if ((gid%2 == 0) && (gid/x)%2 == 1)            // Blue pixels
             {
                c[gid] = a[gid];
                //c[gid] = 0.0;
             }
             else if (gid%2 == 1 && (gid/x)%2 == 1)          // Green pixels, reds on sides
             {
                c[gid] = (a[gid-1] + a[gid+1]) /2;
                //c[gid] = 0.0;
             }
             else if (gid%2 == 0 && (gid/x)%2 == 0)          // Green pixel, blues on side
             {
                c[gid] = (a[gid-x] + a[gid +x]) /2;
                //c[gid] = 0.0;
             }
             else                                              // You shouldn't end here. Just in case
             {
                c[gid] = a[gid];
                //c[gid] = 0.0;
             }
        }
        """

        cfa_bufg = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=cfag)
        dest_bufg = cl.Buffer(self.ctx, mf.WRITE_ONLY, cfag.nbytes)
        prg_green = cl.Program(self.ctx, codegreen).build()
        prg_green.bilinear(self.queue, cfag.shape, None, cfa_bufg, dest_bufg)
        g = np.empty_like(cfag)
        cl.enqueue_copy(self.queue, g, dest_bufg)


        cfa_bufr = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=cfar)
        dest_bufr = cl.Buffer(self.ctx, mf.WRITE_ONLY, cfar.nbytes)
        prg_red   = cl.Program(self.ctx, codered).build()
        prg_red.bilinear(self.queue, cfar.shape, None, cfa_bufr, dest_bufr)
        r = np.empty_like(cfar)
        cl.enqueue_copy(self.queue, r, dest_bufr)

        cfa_bufb = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=cfab)
        dest_bufb = cl.Buffer(self.ctx, mf.WRITE_ONLY, cfab.nbytes)
        prg_blue  = cl.Program(self.ctx, codeblue).build()
        prg_blue.bilinear(self.queue, cfab.shape, None, cfa_bufb, dest_bufb)
        b = np.empty_like(cfab)
        cl.enqueue_copy(self.queue, b, dest_bufb)

        r = np.reshape(r, (image.y, -1), order='C')
        g = np.reshape(g, (image.y, -1), order='C')
        b = np.reshape(b, (image.y, -1), order='C')
        #print("After reshape: " + str(g.shape))
        print("...Done")
        return np.array([r, g, b])
        #image.savergb(np.array([r, g, b]))