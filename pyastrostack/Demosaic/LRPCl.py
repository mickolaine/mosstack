

__author__ = 'micko'

from .. Demosaic.Demosaic import Demosaic
import numpy as np
import pyopencl as cl


class LRPCl(Demosaic):
    """
    LaRoche-Prescott interpolation using pyOpenCL.

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
        dest_buf = cl.Buffer(self.ctx, self.mf.WRITE_ONLY, cfa.nbytes)

        self.prg_green.bilinear(self.queue, cfa.shape, None, cfa_buf, dest_buf)
        self.g = np.empty_like(cfa)
        cl.enqueue_copy(self.queue, self.g, dest_buf)

        green_buf = cl.Buffer(self.ctx, self.mf.READ_ONLY | self.mf.COPY_HOST_PTR, hostbuf=self.g)

        dest_buf = cl.Buffer(self.ctx, self.mf.WRITE_ONLY, cfa.nbytes)
        self.prg_red.bilinear(self.queue, cfa.shape, None, cfa_buf, green_buf, dest_buf)
        self.r = np.empty_like(cfa)
        cl.enqueue_copy(self.queue, self.r, dest_buf)

        dest_buf = cl.Buffer(self.ctx, self.mf.WRITE_ONLY, cfa.nbytes)
        self.prg_blue.bilinear(self.queue, cfa.shape, None, cfa_buf, green_buf, dest_buf)
        self.b = np.empty_like(cfa)
        cl.enqueue_copy(self.queue, self.b, dest_buf)

        self.r = np.uint16(np.reshape(self.r, (self.y, -1), order='C'))
        self.g = np.uint16(np.reshape(self.g, (self.y, -1), order='C'))
        self.b = np.uint16(np.reshape(self.b, (self.y, -1), order='C'))

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

        codegreen = """
        __kernel void bilinear(__global const float *a, __global float *c)
        {
            int x = """ + str(self.x) + """;
            int len = """ + str(self.lencfa) + """;
            int gid = get_global_id(0);
            float alpha;
            float beta;
                                                                 // conditions explained
            if (gid < x || gid%x == x-1 || gid%x == 0 || gid > len - x)  // upper border, right, left, lower border
            {
                c[gid] = a[gid];
            }
            else if (""" + r_condition + """ ||                   // Non-green pixels
                    """ + b_condition + """)                     // even on even line, odd on odd line.
            {
                if ((a[gid-2]+a[gid+2])/2 < a[gid]) {
                    alpha = a[gid] - (a[gid-2]+a[gid+2])/2;
                }
                else {
                    alpha = (a[gid-2]+a[gid+2])/2 - a[gid];
                }
                if ((a[gid-2*x]+a[gid+2*x])/2 < a[gid]) {
                    beta = a[gid] - (a[gid-2*x]+a[gid+2*x])/2;
                }
                else {
                    beta = (a[gid-2*x]+a[gid+2*x])/2 - a[gid];
                }

                if (alpha < beta) {
                    c[gid] = (a[gid-1] + a[gid+1])/2.0;
                }
                else if (alpha > beta) {
                    c[gid] = (a[gid-x] + a[gid+x])/2.0;
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

        # Red and blue require interpolated green pixels but otherwise they're about the same
        codecommon = """
        __kernel void bilinear(__global const float *a, __global const float *g, __global float *c)
        {
          int x = """ + str(self.x) + """;
          int len = """ + str(self.lencfa) + """;
          int gid = get_global_id(0);

        """

        codeblue = codecommon + """

            if (gid < x || gid%x == 0 || gid%x == x-1 || gid > len - x)  // upper border, right, left and lower border
            {
                c[gid] = a[gid];
            }
            else if (""" + b_condition + """)        // Blue pixels
            {
                c[gid] = a[gid];
            }
            else if (""" + r_condition + """)        // Red pixels
            {
                c[gid] = ((a[gid-1-x]-g[gid-1-x]) + (a[gid+1-x]-g[gid+1-x])
                       +  (a[gid-1+x]-g[gid-1+x]) + (a[gid+1+x]-g[gid+1+x]))/4 + g[gid];
            }
            else if (""" + g_nexttored + """)          // Green pixels, reds on sides
            {
                c[gid] = ((a[gid-x]-g[gid-x]) + (a[gid+x]-g[gid+x]))/2 + g[gid];
            }
            else if (""" + g_nexttoblue + """)          // Green pixel, blues on side
            {
                c[gid] = ((a[gid-1]-g[gid-1]) + (a[gid+1]-g[gid+1]))/2 + g[gid];
            }
            else                                            // You shouldn't be here. Just in case
            {
                c[gid] = a[gid];
            }
        }
        """

        codered = codecommon + """
            if (gid < x || gid%x == 0 || gid%x == x-1 || gid > len - x)  // upper border, right, left and lower border
            {
                c[gid] = a[gid];
            }
            else if (""" + b_condition + """)        // Blue pixels
            {
                c[gid] = ((a[gid-1-x]-g[gid-1-x]) + (a[gid+1-x]-g[gid+1-x])
                       +  (a[gid-1+x]-g[gid-1+x]) + (a[gid+1+x]-g[gid+1+x]))/4 + g[gid];
            }
            else if (""" + r_condition + """)        // Red pixels
            {
                c[gid] = a[gid];
            }
            else if (""" + g_nexttored + """)          // Green pixels, reds on sides
            {
                c[gid] = ((a[gid-1]-g[gid-1]) + (a[gid+1]-g[gid+1]))/2 + g[gid];
            }
            else if (""" + g_nexttoblue + """)          // Green pixel, blues on side
            {
                c[gid] = ((a[gid-x]-g[gid-x]) + (a[gid+x]-g[gid+x]))/2 + g[gid];
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

