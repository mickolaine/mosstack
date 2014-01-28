__author__ = 'micko'

from .. Demosaic.Demosaic import Demosaic
import numpy as np
import pyopencl as cl
import datetime   # For profiling


class VNG(Demosaic):
    """
    Variable Number of Gradients algorithm for demosaicing

    """

    def __init__(self):
        """Prepare everything for running the demosaic-algorithms."""
        self.ctx = cl.create_some_context()

        self.queue = cl.CommandQueue(self.ctx)

    def demosaic(self, image):
        """ VNG interpolation using pyOpenCL.

        Arguments:
        image - a pyAstroStack.Photo

        Returns:
        [red, green, blue] as numpy.array
        """
        mf = cl.mem_flags

        print("Processing image " + image.imagepath)

        cfa = np.ravel(np.float32(image.data), order='C')
        t1 = datetime.datetime.now()
        bayer = "RGGB"      # This goes somewhere outside this file. Now for testing here

        if bayer == "RGGB":
            r_condition  = "(gid%2 == 0) && (gid/x)%2 == 1"
            g_nexttored  = "(gid%2 == 0  && (gid/x)%2 == 0)"
            g_nexttoblue = "(gid%2 == 1  && (gid/x)%2 == 1)"
            g_condition  = g_nexttored + " || " + g_nexttoblue
            b_condition  = "(gid%2 == 1) && (gid/x)%2 == 0"
        elif bayer == "RGBG":
            pass
        elif bayer == "GRGB":
            pass
        else:
            print("Unknown Bayer configuration. Please inform the developer.")

        code = """

__kernel void vng(__global const float *a,
                   __global float *r,
                   __global float *g,
                   __global float *b)
{
int x = """ + str(image.x) + """;
int len = """ + str(len(cfa)) + """;
int gid = get_global_id(0);

if (gid < 2*x || gid%x < 2 || gid%x > x-3 || gid > len - 2*x)    // Two row borders
{
    // Just copy the border values from CFA until I think up something better
    // Perhaps this is good enough
    r[gid] = a[gid];
    g[gid] = a[gid];
    b[gid] = a[gid];
}

// Red pixels
else if (""" + r_condition + """ || """ + b_condition + """)
{
    float r1,  g2,  r3,  g4,  r5,
          g6,  b7,  g8,  b9,  g10,
          r11, g12, r13, g14, r15,
          g16, b17, g18, b19, g20,
          r21, g22, r23, g24, r25;

    r1  = a[gid - 2*x - 2];
    g2  = a[gid -   x - 2];
    r3  = a[gid       - 2];
    g4  = a[gid +   x - 2];
    r5  = a[gid + 2*x - 2];
    g6  = a[gid - 2*x - 1];
    b7  = a[gid -   x - 1];
    g8  = a[gid       - 1];
    b9  = a[gid +   x - 1];
    g10 = a[gid + 2*x - 1];
    r11 = a[gid - 2*x    ];
    g12 = a[gid -   x    ];
    r13 = a[gid];
    g14 = a[gid +   x    ];
    r15 = a[gid + 2*x    ];
    g16 = a[gid - 2*x + 1];
    b17 = a[gid -   x + 1];
    g18 = a[gid       + 1];
    b19 = a[gid +   x + 1];
    g20 = a[gid + 2*x + 1];
    r21 = a[gid - 2*x + 2];
    g22 = a[gid -   x + 2];
    r23 = a[gid       + 2];
    g24 = a[gid +   x + 2];
    r25 = a[gid + 2*x + 2];

    float grn, gre, grs, grw, grne, grse, grnw, grsw;

    grn  = fabs(g8  - g18) + fabs(r3  - r13) + fabs(b7  - b17)/2 + fabs(b9  - b19)/2 + fabs(g2  - g12)/2 + fabs(g4  - g14)/2;
    gre  = fabs(g14 - g12) + fabs(r15 - r13) + fabs(b9  - b7 )/2 + fabs(b19 - b17)/2 + fabs(g10 - g8 )/2 + fabs(g20 - g18)/2;
    grs  = fabs(g18 - g8 ) + fabs(r23 - r13) + fabs(b19 - b9 )/2 + fabs(b17 - b7 )/2 + fabs(g24 - g14)/2 + fabs(g22 - g12)/2;
    grw  = fabs(g12 - g14) + fabs(r11 - r13) + fabs(b17 - b19)/2 + fabs(b7  - b9 )/2 + fabs(g16 - g18)/2 + fabs(g6  - g8 )/2;
    grne = fabs(b9  - b17) + fabs(r5  - r13) + fabs(g8  - g12)/2 + fabs(g14 - g18)/2 + fabs(g4  - g8 )/2 + fabs(g10 - g14)/2;
    grse = fabs(b19 - b7 ) + fabs(r25 - r13) + fabs(g14 - g8 )/2 + fabs(g18 - g12)/2 + fabs(g20 - g14)/2 + fabs(g24 - g18)/2;
    grnw = fabs(b7  - b19) + fabs(r1  - r13) + fabs(g12 - g18)/2 + fabs(g8  - g14)/2 + fabs(g6  - g12)/2 + fabs(g2  - g8 )/2;
    grsw = fabs(b17 - b9 ) + fabs(r21 - r13) + fabs(g18 - g14)/2 + fabs(g12 - g8 )/2 + fabs(g22 - g18)/2 + fabs(g16 - g12)/2;

    // min = gn;
    // if (ge  < min) min = ge;
    // if (gs  < min) min = gs;
    // if (gw  < min) min = gw;
    // if (gne < min) min = gne;
    // if (gse < min) min = gse;
    // if (gnw < min) min = gnw;
    // if (gsw < min) min = gsw;

    // max = gn;
    // if (ge  > max) max = ge;
    // if (gs  > max) max = gs;
    // if (gw  > max) max = gw;
    // if (gne > max) max = gne;
    // if (gse > max) max = gse;
    // if (gnw > max) max = gnw;
    // if (gsw > max) max = gsw;

    float min, max, t1, t2, t3, t4;

    t1 = fmin(grn, gre);
    t2 = fmin(grs, grw);
    t3 = fmin(grne, grse);
    t4 = fmin(grnw, grsw);
    t1 = fmin(t1, t2);
    t3 = fmin(t3, t4);
    min = fmin(t1, t3);

    t1 = fmax(grn, gre);
    t2 = fmax(grs, grw);
    t3 = fmax(grne, grse);
    t4 = fmax(grnw, grsw);
    t1 = fmax(t1, t2);
    t3 = fmax(t3, t4);
    max = fmax(t1, t3);

    float T = 1.5*min + 0.5*(max-min);

    int n = 0;
    float rsum = 0,
          gsum = 0,
          bsum = 0;

    if (grn  <= T) {
        rsum = rsum + (r3 + r13)/2;
        gsum = gsum + g8;
        bsum = bsum + (b7 + b9)/2;
        n++;
    }
    if (gre  <= T) {
        rsum = rsum + (r15 + r13)/2;
        gsum = gsum + g14;
        bsum = bsum + (b19 + b9)/2;
        n++;
    }
    if (grs  <= T) {
        rsum = rsum + (r23 + r13)/2;
        gsum = gsum + g18;
        bsum = bsum + (b17 + b19)/2;
        n++;
    }
    if (grw  <= T)  {
        rsum = rsum + (r11 + r13)/2;
        gsum = gsum + g12;
        bsum = bsum + (b7 + b17)/2;
        n++;
    }
    if (grne <= T)  {
        rsum = rsum + (r5 + r13)/2;
        gsum = gsum + (g4 + g8 + g10 + g14)/4;
        bsum = bsum + b9;
        n++;
    }
    if (grse <= T)  {
        rsum = rsum + (r25 + r13)/2;
        gsum = gsum + (g14 + g18 + g20 + g24)/4;
        bsum = bsum + b19;
        n++;
    }
    if (grnw <= T) {
        rsum = rsum + (r1 + r13)/2;
        gsum = gsum + (g2 + g6 + g8 + g12)/4;
        bsum = bsum + b7;
        n++;
    }
    if (grsw <= T) {
        rsum = rsum + (r21 + r13)/2;
        gsum = gsum + (g12 + g16 + g18 + g22)/4;
        bsum = bsum + b17;
        n++;
    }

    if(n==0){
        n = 1;
    }

    if (""" + r_condition + """) {
        r[gid] = r13;
        g[gid] = r13 + (gsum - rsum)/n;
        b[gid] = r13 + (bsum - rsum)/n;
        //r[gid] = 0;
        //g[gid] = 0;
        //b[gid] = 0;
    }
    // Blue should be symmetrical with red. Should. If I got this right...
    if (""" + b_condition + """) {
        r[gid] = r13 + (bsum - rsum)/n;
        g[gid] = r13 + (gsum - rsum)/n;
        b[gid] = r13;
        //r[gid] = 0;
        //g[gid] = 0;
        //b[gid] = 0;
    }

}

// Green pixels
else if (""" + g_condition + """)
{
    float g1,  r2,  g3,  r4,  g5,
          b6,  g7,  b8,  g9,  b10,
          g11, r12, g13, r14, g15,
          b16, g17, b18, g19, b20,
          g21, r22, g23, r24, g25;

    g1  = a[gid - 2*x - 2];
    r2  = a[gid -   x - 2];
    g3  = a[gid       - 2];
    r4  = a[gid +   x - 2];
    g5  = a[gid + 2*x - 2];
    b6  = a[gid - 2*x - 1];
    g7  = a[gid -   x - 1];
    b8  = a[gid       - 1];
    g9  = a[gid +   x - 1];
    b10 = a[gid + 2*x - 1];
    g11 = a[gid - 2*x    ];
    r12 = a[gid -   x    ];
    g13 = a[gid];
    r14 = a[gid +   x    ];
    g15 = a[gid + 2*x    ];
    b16 = a[gid - 2*x + 1];
    g17 = a[gid -   x + 1];
    b18 = a[gid       + 1];
    g19 = a[gid +   x + 1];
    b20 = a[gid + 2*x + 1];
    g21 = a[gid - 2*x + 2];
    r22 = a[gid -   x + 2];
    g23 = a[gid       + 2];
    r24 = a[gid +   x + 2];
    g25 = a[gid + 2*x + 2];

    float grn, gre, grs, grw, grne, grse, grnw, grsw;

    grn  = fabs(g3  - g13) + fabs(b8  - b18) + fabs(g7  - g17)/2 + fabs(g9  - g19)/2 + fabs(r2  - r12)/2 + fabs(r4  - r14)/2;
    gre  = fabs(r14 - r12) + fabs(g15 - g13) + fabs(g9  - g7 )/2 + fabs(g19 - g17)/2 + fabs(b10 - b8 )/2 + fabs(b20 - b18)/2;
    grs  = fabs(b18 - b8 ) + fabs(g23 - g13) + fabs(g19 - g9 )/2 + fabs(g17 - g7 )/2 + fabs(r24 - r14)/2 + fabs(r22 - r12)/2;
    grw  = fabs(r12 - r14) + fabs(g11 - g13) + fabs(g17 - g19)/2 + fabs(g7  - g9 )/2 + fabs(b16 - b18)/2 + fabs(b6  - b8 )/2;
    grne = fabs(g9  - g17) + fabs(g5  - g13) + fabs(r4  - r12) + fabs(b10 - b18);
    grse = fabs(g19 - g7 ) + fabs(g25 - g13) + fabs(b20 - b8 ) + fabs(r24 - r12);
    grnw = fabs(g7  - g19) + fabs(g1  - g13) + fabs(b6  - b18) + fabs(r2  - r14);
    grsw = fabs(g17 - g9 ) + fabs(g21 - g13) + fabs(r22 - r14) + fabs(b16 - b8 );

    float min, max, t1, t2, t3, t4;

    t1 = fmin(grn, gre);
    t2 = fmin(grs, grw);
    t3 = fmin(grne, grse);
    t4 = fmin(grnw, grsw);
    t1 = fmin(t1, t2);
    t3 = fmin(t3, t4);
    min = fmin(t1, t3);

    t1 = fmax(grn, gre);
    t2 = fmax(grs, grw);
    t3 = fmax(grne, grse);
    t4 = fmax(grnw, grsw);
    t1 = fmax(t1, t2);
    t3 = fmax(t3, t4);
    max = fmax(t1, t3);

    float T = 1.5*min + 0.5*(max-min);

    int n = 0;
    float rsum = 0,
          gsum = 0,
          bsum = 0;

    if (grn  <= T) {
        rsum = rsum + (r2 + r4 + r12 + r14)/4;
        gsum = gsum + (g3 + g13)/2;
        bsum = bsum + b8;
        n++;
    }
    if (gre  <= T) {
        rsum = rsum + r14;
        gsum = gsum + (g13 + g15)/2;
        bsum = bsum + (b8 + b10 + b18 + b20)/4;
        n++;
    }
    if (grs  <= T) {
        rsum = rsum + (r12 + r14 + r22 + r24)/4;
        gsum = gsum + (g13 + g23)/2;
        bsum = bsum + b18;
        n++;
    }
    if (grw  <= T)  {
        rsum = rsum + r12;
        gsum = gsum + (g11 + g13)/2;
        bsum = bsum + (b6 + b8 + b16 + b18)/4;
        n++;
    }
    if (grne <= T)  {
        rsum = rsum + (r4 + r14)/2;
        gsum = gsum + g9;
        bsum = bsum + (b8 + b10)/2;
        n++;
    }
    if (grse <= T)  {
        rsum = rsum + (r14 + r24)/2;
        gsum = gsum + g19;
        bsum = bsum + (b18 + b20)/2;
        n++;
    }
    if (grnw <= T) {
        rsum = rsum + (r2 + r12)/2;
        gsum = gsum + g7;
        bsum = bsum + (b6 + b8)/2;
        n++;
    }
    if (grsw <= T) {
        rsum = rsum + (r12 + r22)/2;
        gsum = gsum + g17;
        bsum = bsum + (b16 + b18)/2;
        n++;
    }
    if(n==0){
        n = 1;
    }

    if (""" + g_nexttored + """) {
        r[gid] = g13 + (rsum - gsum)/n;
        g[gid] = g13;
        b[gid] = g13 + (bsum - gsum)/n;
    }
    if (""" + g_nexttoblue + """) {
        b[gid] = g13 + (rsum - gsum)/n;
        g[gid] = g13;
        r[gid] = g13 + (bsum - gsum)/n;
    }
    //r[gid] = 0;
    //g[gid] = 0;
    //b[gid] = 0;

}
}
        """

        cfa_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=cfa)
        dest_bufr = cl.Buffer(self.ctx, mf.WRITE_ONLY, cfa.nbytes)
        dest_bufg = cl.Buffer(self.ctx, mf.WRITE_ONLY, cfa.nbytes)
        dest_bufb = cl.Buffer(self.ctx, mf.WRITE_ONLY, cfa.nbytes)

        program = cl.Program(self.ctx, code).build()
        program.vng(self.queue, cfa.shape, None, cfa_buf, dest_bufr, dest_bufg, dest_bufb)
        r = np.empty_like(cfa)
        g = np.empty_like(cfa)
        b = np.empty_like(cfa)
        cl.enqueue_copy(self.queue, r, dest_bufr)
        cl.enqueue_copy(self.queue, g, dest_bufg)
        cl.enqueue_copy(self.queue, b, dest_bufb)
        t2 = datetime.datetime.now()
        r = np.reshape(r, (image.y, -1), order='C')
        g = np.reshape(g, (image.y, -1), order='C')
        b = np.reshape(b, (image.y, -1), order='C')

        print("...Done")
        print("Debayering took " + str(t2-t1) + " seconds.")
        return np.array([r, g, b])