from __future__ import division

from .. Registering.Registering import Registering
from . Sextractor import Sextractor
from . ImTransform import ImTransform
from . SkTransform import SkTransform
import datetime   # For profiling
from shutil import copyfile
from re import sub
from math import sqrt
import pyximport
import numpy as np
pyximport.install(setup_args={'include_dirs': [np.get_include()]})
from . _step2 import step2 as _step2


class Groth(Registering):
    """
    Registering implementation which uses SExtractor to find stars, method by E.J. Groth to do the star matching and
    ImageMagick to do the affine transforms.

    Groth's method is described in his article 'A pattern-matching algorithm for two-dimensional coordinate'
    (http://adsabs.harvard.edu/abs/1986AJ.....91.1244G).
    """

    def __init__(self):
        self.timing = False

    def register(self, imagelist, project):
        """
        Calls everything required for total registration process.
        """

        if self.timing:
            t1 = datetime.datetime.now()

        self.findstars(imagelist, project)

        ref = project.get("Reference images", "light")

        for i in imagelist:
            #if imagelist[i].points is None:
            self.step1(imagelist[i])                      # Step1 has to be finished before the rest

        for i in imagelist:
            if imagelist[i].pairs is None:
                self.step2(imagelist[ref], imagelist[i])

        for i in imagelist:

            self.transformer.affine_transform(imagelist[i], ref)

        if self.timing:
            t2 = datetime.datetime.now()
            print("Triangle calculations took " + str(t2 - t1) + " seconds.")

    def findstars(self, imagelist, project):
        """
        Finds the stars and creates all the triangles from them
        """
        sex = Sextractor(list(imagelist.values())[0], project)    # TODO: Ref image here
        sensitivity = sex.findsensitivity()
        del sex

        for i in imagelist:
            sex = Sextractor(imagelist[i], project)
            sex.setsensitivity(sensitivity[0], sensitivity[1])
            imagelist[i].coordinates = sex.getcoordinates()
            sex.maketriangles()

    def step1(self, image):
        """
        Calculates R,C,tR and tC for every triangle in image. These quantities are described in article #TODO: Cite the article

        Result image.tri = [[x1,y1,x2,y2,x3,y3, R, C, tR, tC], ... , ...]
        """

        ep = 0.3
        #xi = 3. * ep

        newtri = []
        for tri in image.tri:      # tri is a list of coordinates. ((x1,y1),(x2,y2),(x3,y3))

            x1 = tri[0][0]
            y1 = tri[0][1]
            x2 = tri[1][0]
            y2 = tri[1][1]
            x3 = tri[2][0]
            y3 = tri[2][1]

            x3x1 = x3 - x1
            y3y1 = y3 - y1
            x2x1 = x2 - x1
            y2y1 = y2 - y1

            r3 = sqrt(x3x1 * x3x1 + y3y1 * y3y1)
            r2 = sqrt(x2x1 * x2x1 + y2y1 * y2y1)

            R = r3 / r2
            C = (x3x1 * x2x1 + y3y1 * y2y1) / (r3 * r2)     #Cosine of angle at vertex 1

            tR = sqrt(2. * R * R * ep * ep * (1. / (r3 * r3) - C / (r2 * r3) + 1. / (r2 * r2)))

            S = 1. - C ** 2.   #Sine^2 of angle at vertex 1
            # S should be S**2 and on above line S should be sqrt of 1-C**2,
            # but this might be faster. I don't know if python optimizes this.
            tC = sqrt(2. * S * ep * ep * (1. / (r3 * r3) - C / (r2 * r3) + 1. / (r2 * r2)) +
                      3. * C * C * ep * ep * ep * ep * (1. / (r3 * r3) - C / (r2 * r3) + 1. / (r2 * r2)) ** 2.)


            temp = [tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1]]
            temp.append(R)
            temp.append(C)
            temp.append(tR)
            temp.append(tC)
            newtri.append(temp)
        image.tri = np.float32(np.array(newtri))

        print("Step 1 complete for image " + str(image.number) + ". " + str(len(image.tri)) + " triangles found.")

    def step2(self, i1, i2):
        """
        A wrapper for Cython implementation of the algorithm

        i1 and i2 have a list tri = [[(x1,y1),(x2,y2),(x3,y3), R, C, tR, tC], ... , ...]
        """

        print("Matching image " + str(i2.number) + " to reference image " + str(i1.number) + "...")

        i2.pairs = _step2(i1.tri, i2.tri)

        print("Done.")
