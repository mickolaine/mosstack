#cython: boundscheck=False
#cython: wraparound=False
#cython: language_level=3

from __future__ import division

import numpy as np
cimport numpy as np

DTYPE = np.float32
ctypedef np.float32_t DTYPE_t

def _debayer(np.ndarray[DTYPE_t, ndim=2] cfa, np.ndarray[DTYPE_t, ndim=2] r,
              np.ndarray[DTYPE_t, ndim=2] g, np.ndarray[DTYPE_t, ndim=2] b):

    maxi = len(cfa)
    maxj = len(cfa[0])

    cdef int i = 0
    cdef int j = 0

    for i from 0 <= i < maxi:
        for j from 0 <= j < maxj:
            if i == 0 or i == maxi - 1 or j == 0 or j == maxj - 1:      # Border
                r[i,j] = cfa[i,j]
                g[i,j] = cfa[i,j]
                b[i,j] = cfa[i,j]

            elif (i % 2 == 1) & (j % 2 == 1):                                 # At green on red row
                r[i,j] = (cfa[i,j - 1] + cfa[i,j + 1]) / 2.
                b[i,j] = (cfa[i - 1,j] + cfa[i + 1,j]) / 2.
                g[i,j] = cfa[i,j]

            elif (i % 2 == 0) & (j % 2 == 0):                                 # At green on blue row
                r[i,j] = (cfa[i - 1,j] + cfa[i + 1,j]) / 2.
                b[i,j] = (cfa[i,j - 1] + cfa[i,j + 1]) / 2.
                g[i,j] = cfa[i,j]

            elif (i % 2 == 1) & (j % 2 == 0):                                 # At red position
                r[i,j] = cfa[i,j]
                b[i,j] = (cfa[i - 1,j - 1] + cfa[i - 1,j + 1] + cfa[i + 1,j - 1] + cfa[i + 1,j + 1]) / 4.
                g[i,j] = (cfa[i - 1,j] + cfa[i,j - 1] + cfa[i,j + 1] + cfa[i + 1,j]) / 4.

            elif (i % 2 == 0) & (j % 2 == 1):                                 # At blue position
                r[i,j] = (cfa[i - 1,j - 1] + cfa[i - 1,j + 1] + cfa[i + 1,j - 1] + cfa[i + 1,j + 1]) / 4.
                b[i,j] = cfa[i,j]
                g[i,j] = (cfa[i - 1,j] + cfa[i,j - 1] + cfa[i,j + 1] + cfa[i + 1,j]) / 4.

    return [r, g, b]