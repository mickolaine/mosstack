

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

    def demosaic(self, image):
        """ LaRoche-Prescott interpolation using pyOpenCL.

        Arguments:
        image - a pyAstroStack.Photo

        Returns:
        Nothing

        Interpolated image will be given to image via image.savergb()
        """
        print("Processing image " + image.imagepath)
        mf = cl.mem_flags

        print(image.data.shape)
        cfa = np.ravel(np.float32(image.data), order='C')
        print(cfa.shape)

        codegreen = """
        __kernel void bilinear(__global const float *a, __global float *c)
        {
            int x = """ + str(image.x) + """;
            int len = """ + str(len(cfa)) + """;
            int gid = get_global_id(0);
            float alpha;
            float beta;
                                                                 // conditions explained
            if (gid < x || gid%x == x-1 || gid%x == 0 || gid > len - x)  // upper border, right, left, lower border
            {
                c[gid] = a[gid];
                //c[gid] = 0;
            }
            else if ((gid%2 == 0 && (gid/x)%2 == 1) ||                   // Non-green pixels
                     (gid%2 == 1 && (gid/x)%2 == 0))                     // even on even line, odd on odd line.
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
                    //c[gid] = 0.0;
                    //c[gid] = a[gid];
                }
                else if (alpha > beta) {
                    c[gid] = (a[gid-x] + a[gid+x])/2.0;
                    //c[gid] = 0.0;
                    //c[gid] = a[gid];
                }
                else {
                    c[gid] = (a[gid-1] + a[gid-x] + a[gid+x] + a[gid+1])/4;
                    //c[gid] = 0.0;
                    //c[gid] = a[gid];
                }
            }
            else                                                         // Green pixels
            {
                c[gid] = a[gid];
                //c[gid] = 0.0;
            }
        }
        """

        # Red and blue require interpolated green pixels but otherwise they're about the same
        codecommon = """
        __kernel void bilinear(__global const float *a, __global const float *g, __global float *c)
        {
          int x = """ + str(image.x) + """;
          int len = """ + str(len(cfa)) + """;
          int gid = get_global_id(0);

        """

        codeblue = codecommon + """

            if (gid < x || gid%x == 0 || gid%x == x-1 || gid > len - x)  // upper border, right, left and lower border
            {
                c[gid] = a[gid];
            }
            else if ((gid%2 == 1) && (gid/x)%2 == 0)        // Blue pixels
            {
                c[gid] = a[gid];
                //c[gid] = 0.0;
            }
            else if ((gid%2 == 0) && (gid/x)%2 == 1)        // Red pixels
            {
                c[gid] = ((a[gid-1-x]-g[gid-1-x]) + (a[gid+1-x]-g[gid+1-x])
                       +  (a[gid-1+x]-g[gid-1+x]) + (a[gid+1+x]-g[gid+1+x]))/4 + g[gid];
                //c[gid] = 0.0;
            }
            else if (gid%2 == 1 && (gid/x)%2 == 1)          // Green pixels, reds on sides
            {
                c[gid] = ((a[gid-x]-g[gid-x]) + (a[gid+x]-g[gid+x]))/2 + g[gid];
                //c[gid] = 0.0;
            }
            else if (gid%2 == 0 && (gid/x)%2 == 0)          // Green pixel, blues on side
            {
                c[gid] = ((a[gid-1]-g[gid-1]) + (a[gid+1]-g[gid+1]))/2 + g[gid];
                //c[gid] = 0.0;
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
            else if ((gid%2 == 1) && (gid/x)%2 == 0)        // Blue pixels
            {
                c[gid] = ((a[gid-1-x]-g[gid-1-x]) + (a[gid+1-x]-g[gid+1-x])
                       +  (a[gid-1+x]-g[gid-1+x]) + (a[gid+1+x]-g[gid+1+x]))/4 + g[gid];
            }
            else if ((gid%2 == 0) && (gid/x)%2 == 1)        // Red pixels
            {
                c[gid] = a[gid];
            }
            else if (gid%2 == 1 && (gid/x)%2 == 1)          // Green pixels, reds on sides
            {
                c[gid] = ((a[gid-1]-g[gid-1]) + (a[gid+1]-g[gid+1]))/2 + g[gid];
            }
            else if (gid%2 == 0 && (gid/x)%2 == 0)          // Green pixel, blues on side
            {
                c[gid] = ((a[gid-x]-g[gid-x]) + (a[gid+x]-g[gid+x]))/2 + g[gid];
            }
            else                                              // You shouldn't end here. Just in case
            {
                c[gid] = a[gid];
            }
        }
        """

        cfa_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=cfa)
        dest_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, cfa.nbytes)

        prg_green = cl.Program(self.ctx, codegreen).build()
        prg_green.bilinear(self.queue, cfa.shape, None, cfa_buf, dest_buf)
        g = np.empty_like(cfa)
        cl.enqueue_copy(self.queue, g, dest_buf)

        green_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=g)

        prg_red   = cl.Program(self.ctx, codered).build()
        prg_blue  = cl.Program(self.ctx, codeblue).build()

        dest_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, cfa.nbytes)    # Reset dest_buf just in case. Maybe not necessary
        prg_red.bilinear(self.queue, cfa.shape, None, cfa_buf, green_buf, dest_buf)
        r = np.empty_like(cfa)
        cl.enqueue_copy(self.queue, r, dest_buf)

        dest_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, cfa.nbytes)    # Reset dest_buf just in case. Maybe not necessary
        prg_blue.bilinear(self.queue, cfa.shape, None, cfa_buf, green_buf, dest_buf)
        b = np.empty_like(cfa)
        cl.enqueue_copy(self.queue, b, dest_buf)

        r = np.reshape(r, (image.y, -1), order='C')
        g = np.reshape(g, (image.y, -1), order='C')
        b = np.reshape(b, (image.y, -1), order='C')
        print(r)
        print(g)
        print(b)

        print("...Done")
        return np.uint16(np.array([r, g, b]))
