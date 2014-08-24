from __future__ import division
from . Groth import Groth
from . SkTransform import SkTransform

class Groth_Skimage(Groth):
    """
    Registering implementation which uses SExtractor to find stars, method by E.J. Groth to do the star matching and
    Scikit-image to do the affine transforms.

    Groth's method is described in his article 'A pattern-matching algorithm for two-dimensional coordinate'
    (http://adsabs.harvard.edu/abs/1986AJ.....91.1244G).
    """

    def __init__(self):
        self.timing = False
        self.transformer = SkTransform()
        self.sensitivity = None
        self.ref = None