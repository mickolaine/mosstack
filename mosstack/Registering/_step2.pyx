#cython: wraparound=False
#cython: language_level=3

from __future__ import division

import numpy as np
cimport numpy as np
cimport cython
from operator import itemgetter

DTYPE = np.float32
ctypedef np.float32_t DTYPE_t

cdef extern from "math.h":
    float sqrtf(float theta)
    float logf(float theta)
    float fabsf(float theta)


def step2(tri1, tri2):

    return _step2(tri1, tri2)


def limit(tri1, tri2):
    """
    Limit the number of triangles before the O(N^6) operation
    """

    newlist = []

    cdef unsigned int i = 0
    cdef unsigned int j = 0

    cdef float previ
    #cdef float prevj
    cdef float eps = 70

    while (i < len(tri1)) and (j < len(tri2)):
        #print(str(tri1[i][0]) + " " + str(tri2[j][0]))
        #print(str(i) + " of " + str(len(tri1)) + " and " + str(j) + " of " + str(len(tri2)))

        if fabsf(tri1[i][0] - tri2[j][0]) < eps:
            newlist.append(tri2[j])
            j = j+1
            #if j == len(tri2):
            #    break
            previ = tri1[i][0]
            #prevj = tri2[j][0]
            #print(tri2)

        else:
            if previ == tri1[i][0]:
                i = i + 1
                #if i == len(tri1):
                #    break
            elif tri1[i][0] < tri2[j][0]:
                i = i + 1
                #if i == len(tri1):
                #    break
            elif tri1[i][0] > tri2[j][0]:
                j = j + 1
                #if j == len(tri2):
                #    break
            else:
                print("Unlikely event.")
                i = i + 1
                #if i == len(tri1):
                #    break

    return newlist


@cython.boundscheck(False)
cdef _step2(np.ndarray[DTYPE_t, ndim=2] tri1, np.ndarray[DTYPE_t, ndim=2] tri2):
#cdef _step2(tri1, tri2):
    """                    0  1  2  3  4  5  6  7   8   9
    tri includes a list [[x1,y1,x2,y2,x3,y3, R, C, tR, tC], ... , ...]
    """

    cdef unsigned int i
    cdef unsigned int j
    cdef unsigned int times
    #cdef float best

    cdef float Ra, Rb, tRa, tRb, Ca, Cb, tCa, tCb, pA, pB
    cdef float x1, x2, x3, y1, y2, y3
    cdef float mean, variance
    cdef float raba2, tra2, tca2

    match = []
    #print(str(len(tri2)))
    #tri2_new = limit(tri1, tri2)
    #tri2_new = tri2
    #print(str(len(tri2_new)))

    for i from 0 <= i < len(tri1):
        #for i in range(0, len(tri1)):
        temp = []

        best = None
        Ra  = tri1[i,6]
        tRa = tri1[i,8]
        Ca  = tri1[i,7]
        tCa = tri1[i,9]

        tra2 = tRa * tRa
        tca2 = tCa * tCa

        for j from 0 <= j < len(tri2):
            #for j in range(0, len(tri2_new)):

            #if fabsf(tri1[i][0] - tri2[j][0]) > 200:
                #print("Skip " + str(tri2[j]))
            #    continue

            Rb  = tri2[j,6]
            tRb = tri2[j,8]
            Cb  = tri2[j,7]
            tCb = tri2[j,9]

            raba2 = (Ra - Rb) ** 2

            # Run the check described in articles equations (7) and (8)
            if (raba2 < (tra2 + tRb*tRb)) & ((Ca - Cb)*(Ca-Cb) < (tca2 + tCb*tCb)):
                if (best is None) or ((Ra-Rb)*(Ra-Rb) < best):
                    #if so, save it for later use
                    best = raba2
                    temp = [tri1[i], tri2[j]]
        if best is not None:
            match.append(temp)
        del temp

    for i in range(0, len(match)):

        x1 = match[i][0][0]
        y1 = match[i][0][1]
        x2 = match[i][0][2]
        y2 = match[i][0][3]
        x3 = match[i][0][4]
        y3 = match[i][0][5]

        pA = (sqrtf((x1 - x2)*(x1-x2) + (y1 - y2)*(y1-y2)) +
              sqrtf((x1 - x3)*(x1-x3) + (y1 - y3)*(y1-y3)) +
              sqrtf((x3 - x2)*(x3-x2) + (y3 - y2)*(y3-y2)))

        x1 = match[i][1][0]
        y1 = match[i][1][1]
        x2 = match[i][1][2]
        y2 = match[i][1][3]
        x3 = match[i][1][4]
        y3 = match[i][1][5]

        pB = (sqrtf((x1 - x2)*(x1-x2) + (y1 - y2)*(y1-y2)) +
              sqrtf((x1 - x3)*(x1-x3) + (y1 - y3)*(y1-y3)) +
              sqrtf((x3 - x2)*(x3-x2) + (y3 - y2)*(y3-y2)))
        match[i].append(logf(pA) - logf(pB))

    do_it_again = True

    times = 0
    while do_it_again:
        newlist = []
        mean = 0.
        variance = 0.
        for m in match:                       # Calculate average value
            mean += m[2] / len(m)
        for m in match:                       # Calculate variance which is sigma**2
            variance += ((mean - m[2])*(mean - m[2])) / len(m)
        sigma = sqrtf(variance)

        do_it_again = False
        for m in match:
            # print(match[2])                             #Debugging
            if fabsf(m[2] - mean) < sigma * 2:
                newlist.append(m)
            else:
                do_it_again = True                        # If you end up here, while has to be run again
        match = newlist                                   # Save new list and do again if necessary
        del newlist
        times += 1

    pairs = {}          # vertex pair as the key and votes as the value

    for m in range(0, len(match)):
        for i in range(3):
            key = ((match[m][1][2*i], match[m][1][2*i+1]),
                   (match[m][0][2*i], match[m][0][2*i+1]))         # This is where source and destination changes places
            if key in pairs:
                pairs[key] += 1
            else:
                pairs[key] = 1

    newpairs = {}
    for key in pairs:
        if pairs[key] > 2:                      # Should be >1 but I really don't need that much points.
            newpairs[key] = pairs[key]
    pairs = newpairs

    final = []
    for key in pairs:
        final.append((key[0], key[1], pairs[key]))

    final = sorted(final, key=itemgetter(2), reverse=True)

    return final