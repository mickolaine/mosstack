__author__ = 'micko'

from .. Demosaic.Demosaic import Demosaic
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
        self.mf = cl.mem_flags
        self.init = False

        self.dest_bufr = None
        self.dest_bufg = None
        self.dest_bufb = None

        self.prg_red = None
        self.prg_green = None
        self.prg_blue = None

        self.r = None
        self.g = None
        self.b = None

        self.x = None
        self.y = None
        self.lencfa = None

    def real_init(self):
        """
        Do the real initialization. This requires information about the frames, so it has to be called
        the first time self.demosaic is called
        """

        self.init = True
        self.build()

    def demosaic(self, image):
        """ LaRoche-Prescott interpolation using pyOpenCL.

        Arguments:
        image - a pyAstroStack.Photo

        Returns:
        Nothing

        Interpolated image will be given to image via image.savergb()
        """

        if not self.init:
            self.x = image.shape[1]
            self.y = image.shape[0]
            cfa = np.ravel(np.float32(image, order='C'))
            self.lencfa = len(cfa)
            self.real_init()
        else:
            cfa = np.ravel(np.float32(image, order='C'))

        self.mf = cl.mem_flags

        cfa_buf = cl.Buffer(self.ctx, self.mf.READ_ONLY | self.mf.COPY_HOST_PTR, hostbuf=cfa)
        dest_bufr = cl.Buffer(self.ctx, self.mf.WRITE_ONLY, cfa.nbytes)
        dest_bufg = cl.Buffer(self.ctx, self.mf.WRITE_ONLY, cfa.nbytes)
        dest_bufb = cl.Buffer(self.ctx, self.mf.WRITE_ONLY, cfa.nbytes)

        self.prg_red.bilinear(self.queue, cfa.shape, None, cfa_buf, dest_bufr)
        self.prg_green.bilinear(self.queue, cfa.shape, None, cfa_buf, dest_bufg)
        self.prg_blue.bilinear(self.queue, cfa.shape, None, cfa_buf, dest_bufb)

        self.r = np.empty_like(cfa)
        self.g = np.empty_like(cfa)
        self.b = np.empty_like(cfa)

        cl.enqueue_copy(self.queue, self.r, dest_bufr)
        cl.enqueue_copy(self.queue, self.g, dest_bufg)
        cl.enqueue_copy(self.queue, self.b, dest_bufb)

        self.r = np.reshape(self.r, (self.y, -1), order='C')
        self.g = np.reshape(self.g, (self.y, -1), order='C')
        self.b = np.reshape(self.b, (self.y, -1), order='C')

        return np.array([self.r, self.g, self.b])

    def build(self):
        """
        Parse code and build program
        """

        bayer = "RGGB"      # This goes somewhere outside this file. Now for testing here

        if bayer == "RGGB":
            r_condition  = "(gid%2 == 0) && (gid/x)%2 == 1"
            g_nexttored  = "(gid%2 == 0  && (gid/x)%2 == 0)"
            g_nexttoblue = "(gid%2 == 1  && (gid/x)%2 == 1)"
            g_condition  = g_nexttored + " || " + g_nexttoblue
            b_condition  = "(gid%2 == 1) && (gid/x)%2 == 0"
        elif bayer == "RGBG":
            pass  # TODO: Implement other bayer filters
        elif bayer == "GRGB":
            pass
        else:
            print("Unknown Bayer configuration. Please inform the developer.")

        codecommon = """
        __kernel void bilinear(__global const float *a, __global float *c)
        {
          int x = """ + str(self.x) + """;
          int len = """ + str(self.lencfa) + """;
          int gid = get_global_id(0);

        """

        codegreen = codecommon + """
                                                                          // conditions explained
             if (gid < x || gid%x < 1 || gid%x > x - 1 || gid > len - x)  // upper border, right, left and lower border
             {
                c[gid] = a[gid];
             }
             else if (""" + g_condition + """)                     // Green pixels.
             {
                c[gid] = a[gid];
             }
             else                                                         // Non-green pixels. Should be all the rest
             {
                c[gid] = (a[gid-1] + a[gid-x] + a[gid+x] + a[gid+1])/4;
             }
        }


        """

        codered = codecommon + """

             if (gid < x || gid%x == 0 || gid%x == x-1 || gid > len - x)  // upper border, right, left and lower border
             {
                c[gid] = a[gid];
             }
             else if (""" + r_condition + """)            // Red pixels
             {
                c[gid] = a[gid];
             }
             else if (""" + b_condition + """)            // Blue pixels
             {
                c[gid] = (a[gid-1-x] + a[gid+1-x] + a[gid-1+x] + a[gid+1+x])/4;
             }
             else if (""" + g_nexttored + """)          // Green pixels, reds on sides
             {
                c[gid] = (a[gid-x] + a[gid +x]) /2;
             }
             else if (""" + g_nexttoblue + """)          // Green pixel, blues on side
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
             if (gid < x || gid%x == 0 || gid%x == x-1 || gid > len - x)  // upper border, right, left and lower border
             {
                c[gid] = a[gid];
                //c[gid] = 0.0;
             }
             else if (""" + r_condition + """)            // Red pixels
             {
                c[gid] = (a[gid-1-x] + a[gid+1-x] + a[gid-1+x] + a[gid+1+x])/4;
             }
             else if (""" + b_condition + """)            // Blue pixels
             {
                c[gid] = a[gid];
             }
             else if (""" + g_nexttored + """)          // Green pixels, reds on sides
             {
                c[gid] = (a[gid-1] + a[gid+1]) /2;
             }
             else if (""" + g_nexttoblue + """)          // Green pixel, blues on side
             {
                c[gid] = (a[gid-x] + a[gid +x]) /2;
             }
             else                                              // You shouldn't end here. Just in case
             {
                c[gid] = a[gid];
             }
        }
        """

        self.prg_red = cl.Program(self.ctx, codered).build()
        self.prg_green = cl.Program(self.ctx, codegreen).build()
        self.prg_blue = cl.Program(self.ctx, codeblue).build()

