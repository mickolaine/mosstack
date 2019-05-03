#cython: boundscheck=False
#cython: wraparound=False
#cython: language_level=3

from __future__ import division

import numpy as np
cimport numpy as np

DTYPE = np.float32
ctypedef np.float32_t DTYPE_t

cdef extern from "math.h":
    float fabsf(float theta)


def _sigmaClip(np.ndarray[DTYPE_t, ndim=4] clip, np.ndarray[DTYPE_t, ndim=3] sigma,
               np.ndarray[DTYPE_t, ndim=3] median, float sigmaFactor):

    cdef int framen = len(clip)
    cdef int colorn = len(clip[0])
    cdef int maxx = len(clip[0][0])
    cdef int maxy = len(clip[0][0][0])

    cdef np.ndarray result = np.zeros([colorn, maxx, maxy], dtype=DTYPE)

    cdef int frame = 0
    cdef int color = 0
    cdef int x = 0
    cdef int y = 0
    cdef float tempSum = 0
    cdef float tempDivider

    for color from 0 <= color < colorn:
        for x from 0 <= x < maxx:
            for y from 0 <= y < maxy:
                tempSum = 0
                tempDivider = 0
                for frame from 0 <= frame < framen:
                    if fabsf(clip[frame, color, x, y] - median[color, x, y]) < (sigmaFactor * sigma[color, x, y]):
                        tempSum += clip[frame, color, x, y]
                        tempDivider += 1
                result[color, x, y] = tempSum / tempDivider

    return result


def _sigmaMedian(np.ndarray[DTYPE_t, ndim=4] clip, np.ndarray[DTYPE_t, ndim=3] sigma,
               np.ndarray[DTYPE_t, ndim=3] median, float sigmaFactor):

    cdef int framen = len(clip)
    cdef int colorn = len(clip[0])
    cdef int maxx = len(clip[0][0])
    cdef int maxy = len(clip[0][0][0])

    cdef np.ndarray result = np.zeros([colorn, maxx, maxy], dtype=DTYPE)

    cdef int frame = 0
    cdef int color = 0
    cdef int x = 0
    cdef int y = 0
    cdef float tempSum = 0

    for color from 0 <= color < colorn:
        for x from 0 <= x < maxx:
            for y from 0 <= y < maxy:
                tempSum = 0
                tempDivider = 0
                for frame from 0 <= frame < framen:
                    if fabsf(clip[frame, color, x, y] - median[color, x, y]) < sigmaFactor * sigma[color, x, y]:
                        tempSum += clip[frame, color, x, y]
                    else:
                        tempSum += median[color, x, y]
                tempSum /= framen
                result[color, x, y] = tempSum

    return result