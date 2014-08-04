#cython: boundscheck=False
#cython: wraparound=False

from __future__ import division

import numpy as np
cimport numpy as np

DTYPE = np.float32
ctypedef np.float32_t DTYPE_t

cdef extern from "math.h":
    float fabsf(float theta)

cdef fmin(float a, float b):
    if a < b:
        return a
    else:
        return b

cdef fmax(float a, float b):
    if a > b:
        return a
    else:
        return b

def _debayer(np.ndarray[DTYPE_t, ndim=2] cfa, np.ndarray[DTYPE_t, ndim=2] r,
              np.ndarray[DTYPE_t, ndim=2] g, np.ndarray[DTYPE_t, ndim=2] b):

    cdef int maxi = len(cfa)
    cdef int maxj = len(cfa[0])

    cdef int i = 0
    cdef int j = 0

    cdef float r1, g2, r3, g4, r5, g6, b7, g8, b9, g10, r11, g12, r13
    cdef float g14, r15, g16, b17, g18, b19, g20, r21, g22, r23, g24, r25

    cdef float g1, r2, g3, r4, g5, b6, g7, b8, g9, b10, g11, r12, g13
    cdef float r14, g15, b16, g17, b18, g19, b20, g21, r22, g23, r24, g25

    cdef float grn, gre, grs, grw, grne, grse, grnw, grsw

    cdef float mini, maxim, t1, t2, t3, t4

    cdef float T
    cdef int n

    cdef float rsum, gsum, bsum

    for i from 0 <= i < maxi:
        for j from 0 <= j < maxj:

            # Two row borders
            if i < 2 or i > (maxi - 3) or j < 2 or j > (maxj - 3):
                r[i,j] = cfa[i,j]
                g[i,j] = cfa[i,j]
                b[i,j] = cfa[i,j]

            # Red and blue pixels
            elif ((i % 2 == 1) & (j % 2 == 0)) or ((i % 2 == 0) & (j % 2 == 1)):
                r1  = cfa[i - 2, j - 2]
                g2  = cfa[i - 2, j - 1]
                r3  = cfa[i - 2, j    ]
                g4  = cfa[i - 2, j + 1]
                r5  = cfa[i - 2, j + 2]
                g6  = cfa[i - 1, j - 2]
                b7  = cfa[i - 1, j - 1]
                g8  = cfa[i - 1, j    ]
                b9  = cfa[i - 1, j + 1]
                g10 = cfa[i - 1, j + 2]
                r11 = cfa[i    , j - 2]
                g12 = cfa[i    , j - 1]
                r13 = cfa[i    , j    ]
                g14 = cfa[i    , j + 1]
                r15 = cfa[i    , j + 2]
                g16 = cfa[i + 1, j - 2]
                b17 = cfa[i + 1, j - 1]
                g18 = cfa[i + 1, j    ]
                b19 = cfa[i + 1, j + 1]
                g20 = cfa[i + 1, j + 2]
                r21 = cfa[i + 2, j - 2]
                g22 = cfa[i + 2, j - 1]
                r23 = cfa[i + 2, j    ]
                g24 = cfa[i + 2, j + 1]
                r25 = cfa[i + 2, j + 2]

                grn  = fabsf(g8  - g18) + fabsf(r3  - r13) + fabsf(b7  - b17)/2.0 + \
                       fabsf(b9  - b19)/2.0 + fabsf(g2  - g12)/2.0 + fabsf(g4  - g14)/2.0
                gre  = fabsf(g14 - g12) + fabsf(r15 - r13) + fabsf(b9  - b7 )/2.0 + \
                       fabsf(b19 - b17)/2.0 + fabsf(g10 - g8 )/2.0 + fabsf(g20 - g18)/2.0
                grs  = fabsf(g18 - g8 ) + fabsf(r23 - r13) + fabsf(b19 - b9 )/2.0 + \
                       fabsf(b17 - b7 )/2.0 + fabsf(g24 - g14)/2.0 + fabsf(g22 - g12)/2.0
                grw  = fabsf(g12 - g14) + fabsf(r11 - r13) + fabsf(b17 - b19)/2.0 + \
                       fabsf(b7  - b9 )/2.0 + fabsf(g16 - g18)/2.0 + fabsf(g6  - g8 )/2.0
                grne = fabsf(b9  - b17) + fabsf(r5  - r13) + fabsf(g8  - g12)/2.0 + \
                       fabsf(g14 - g18)/2.0 + fabsf(g4  - g8 )/2.0 + fabsf(g10 - g14)/2.0
                grse = fabsf(b19 - b7 ) + fabsf(r25 - r13) + fabsf(g14 - g8 )/2.0 + \
                       fabsf(g18 - g12)/2.0 + fabsf(g20 - g14)/2.0 + fabsf(g24 - g18)/2.0
                grnw = fabsf(b7  - b19) + fabsf(r1  - r13) + fabsf(g12 - g18)/2.0 + \
                       fabsf(g8  - g14)/2.0 + fabsf(g6  - g12)/2.0 + fabsf(g2  - g8 )/2.0
                grsw = fabsf(b17 - b9 ) + fabsf(r21 - r13) + fabsf(g18 - g14)/2.0 + \
                       fabsf(g12 - g8 )/2.0 + fabsf(g22 - g18)/2.0 + fabsf(g16 - g12)/2.0

                t1 = fmin(grn, gre)
                t2 = fmin(grs, grw)
                t3 = fmin(grne, grse)
                t4 = fmin(grnw, grsw)
                t1 = fmin(t1, t2)
                t3 = fmin(t3, t4)
                mini = fmin(t1, t3)

                t1 = fmax(grn, gre)
                t2 = fmax(grs, grw)
                t3 = fmax(grne, grse)
                t4 = fmax(grnw, grsw)
                t1 = fmax(t1, t2)
                t3 = fmax(t3, t4)
                maxim = fmax(t1, t3)

                T = 1.5*mini + 0.5*(maxim-mini)

                n = 0
                rsum = 0
                gsum = 0
                bsum = 0

                if grn <= T:
                    rsum += (r3 + r13)/2.0
                    gsum += g8
                    bsum += (b7 + b9)/2.0
                    n += 1

                if gre <= T:
                    rsum += (r15 + r13)/2.0
                    gsum += g14
                    bsum += (b19 + b9)/2.0
                    n += 1

                if grs <= T:
                    rsum += (r23 + r13)/2.0
                    gsum += g18
                    bsum += (b17 + b19)/2.0
                    n += 1

                if grw <= T:
                    rsum += (r11 + r13)/2.0
                    gsum += g12
                    bsum += (b7 + b17)/2.0
                    n += 1

                if grne <= T:
                    rsum += (r5 + r13)/2.0
                    gsum += (g4 + g8 + g10 + g14)/4.0
                    bsum += b9
                    n += 1

                if grse <= T:
                    rsum += (r25 + r13)/2.0
                    gsum += (g14 + g18 + g20 + g24)/4.0
                    bsum += b19
                    n += 1

                if grnw <= T:
                    rsum += (r1 + r13)/2.0
                    gsum += (g2 + g6 + g8 + g12)/4.0
                    bsum += b7
                    n += 1

                if grsw <= T:
                    rsum += (r21 + r13)/2.0
                    gsum += (g12 + g16 + g18 + g22)/4.0
                    bsum += b17
                    n += 1

                if n == 0:
                    n = 1

                # Red
                if (i % 2 == 1) & (j % 2 == 0):
                    #print("red" + str(i) + " " + str(j))
                    r[i,j] = r13
                    g[i,j] = r13 + (gsum - rsum)/n
                    b[i,j] = r13 + (bsum - rsum)/n

                # Blue should be symmetrical with red. Should. If I got this right...
                if (i % 2 == 0) & (j % 2 == 1):
                    #print("blue" + str(i) + " " + str(j))
                    r[i,j] = r13 + (bsum - rsum)/n
                    g[i,j] = r13 + (gsum - rsum)/n
                    b[i,j] = r13

            # Green pixels
            elif ((i % 2 == 1) & (j % 2 == 1)) or ((i % 2 == 0) & (j % 2 == 0)):

                g1  = cfa[i - 2, j - 2]
                r2  = cfa[i - 2, j - 1]
                g3  = cfa[i - 2, j    ]
                r4  = cfa[i - 2, j + 1]
                g5  = cfa[i - 2, j + 2]
                b6  = cfa[i - 1, j - 2]
                g7  = cfa[i - 1, j - 1]
                b8  = cfa[i - 1, j    ]
                g9  = cfa[i - 1, j + 1]
                b10 = cfa[i - 1, j + 2]
                g11 = cfa[i    , j - 2]
                r12 = cfa[i    , j - 1]
                g13 = cfa[i    , j    ]
                r14 = cfa[i    , j + 1]
                g15 = cfa[i    , j + 2]
                b16 = cfa[i + 1, j - 2]
                g17 = cfa[i + 1, j - 1]
                b18 = cfa[i + 1, j    ]
                g19 = cfa[i + 1, j + 1]
                b20 = cfa[i + 1, j + 2]
                g21 = cfa[i + 2, j - 2]
                r22 = cfa[i + 2, j - 1]
                g23 = cfa[i + 2, j    ]
                r24 = cfa[i + 2, j + 1]
                g25 = cfa[i + 2, j + 2]

                grn  = fabsf(g3  - g13) + fabsf(b8  - b18) + fabsf(g7  - g17)/2.0 + \
                       fabsf(g9  - g19)/2.0 + fabsf(r2  - r12)/2.0 + fabsf(r4  - r14)/2.0
                gre  = fabsf(r14 - r12) + fabsf(g15 - g13) + fabsf(g9  - g7 )/2.0 + \
                       fabsf(g19 - g17)/2.0 + fabsf(b10 - b8 )/2.0 + fabsf(b20 - b18)/2.0
                grs  = fabsf(b18 - b8 ) + fabsf(g23 - g13) + fabsf(g19 - g9 )/2.0 + \
                       fabsf(g17 - g7 )/2.0 + fabsf(r24 - r14)/2.0 + fabsf(r22 - r12)/2.0
                grw  = fabsf(r12 - r14) + fabsf(g11 - g13) + fabsf(g17 - g19)/2.0 + \
                       fabsf(g7  - g9 )/2.0 + fabsf(b16 - b18)/2.0 + fabsf(b6  - b8 )/2.0
                grne = fabsf(g9  - g17) + fabsf(g5  - g13) + fabsf(r4  - r12) + fabsf(b10 - b18)
                grse = fabsf(g19 - g7 ) + fabsf(g25 - g13) + fabsf(b20 - b8 ) + fabsf(r24 - r12)
                grnw = fabsf(g7  - g19) + fabsf(g1  - g13) + fabsf(b6  - b18) + fabsf(r2  - r14)
                grsw = fabsf(g17 - g9 ) + fabsf(g21 - g13) + fabsf(r22 - r14) + fabsf(b16 - b8 )

                t1 = fmin(grn, gre)
                t2 = fmin(grs, grw)
                t3 = fmin(grne, grse)
                t4 = fmin(grnw, grsw)
                t1 = fmin(t1, t2)
                t3 = fmin(t3, t4)
                mini = fmin(t1, t3)

                t1 = fmax(grn, gre)
                t2 = fmax(grs, grw)
                t3 = fmax(grne, grse)
                t4 = fmax(grnw, grsw)
                t1 = fmax(t1, t2)
                t3 = fmax(t3, t4)
                maxim = fmax(t1, t3)

                T = 1.5*mini + 0.5*(maxim-mini)

                n = 0
                rsum = 0
                gsum = 0
                bsum = 0

                if grn <= T:
                    rsum += (r2 + r4 + r12 + r14)/4.0
                    gsum += (g3 + g13)/2.0
                    bsum += b8
                    n += 1

                if gre <= T:
                    rsum += r14
                    gsum += (g13 + g15)/2.0
                    bsum += (b8 + b10 + b18 + b20)/4.0
                    n += 1

                if grs <= T:
                    rsum += (r12 + r14 + r22 + r24)/4.0
                    gsum += (g13 + g23)/2.0
                    bsum += b18
                    n += 1

                if grw <= T:
                    rsum += r12
                    gsum += (g11 + g13)/2.0
                    bsum += (b6 + b8 + b16 + b18)/4.0
                    n += 1

                if grne <= T:
                    rsum += (r4 + r14)/2.0
                    gsum += g9
                    bsum += (b8 + b10)/2.0
                    n += 1

                if grse <= T:
                    rsum += (r14 + r24)/2.0
                    gsum += g19
                    bsum += (b18 + b20)/2.0
                    n += 1

                if grnw <= T:
                    rsum += (r2 + r12)/2.0
                    gsum += g7
                    bsum += (b6 + b8)/2.0
                    n += 1

                if grsw <= T:
                    rsum += (r12 + r22)/2.0
                    gsum += g17
                    bsum += (b16 + b18)/2.0
                    n += 1

                if n == 0:
                    n = 1

                # Red row
                if (i % 2 == 1) & (j % 2 == 1):
                    #print("Green on red" + str(i) + " " + str(j))
                    r[i,j] = g13 + (rsum - gsum)/n
                    g[i,j] = g13
                    b[i,j] = g13 + (bsum - gsum)/n

                # Blue row
                if (i % 2 == 0) & (j % 2 == 0):
                    #print("green on blue" + str(i) + " " + str(j))
                    b[i,j] = g13 + (rsum - gsum)/n
                    g[i,j] = g13
                    r[i,j] = g13 + (bsum - gsum)/n

    return np.array([r, g, b])
