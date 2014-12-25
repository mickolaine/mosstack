"""
Class for sigma median stacker.
"""

from .. Stacker.Stacking import Stacking
import numpy as np
import pyximport
pyximport.install(setup_args={'include_dirs': [np.get_include()]})
from . _math import _sigmaMedian


class SigmaMedian(Stacking):
    """
    Sigma median will check which values are too far from the median, replace them with the median and calculate
    average afterwards.
    """

    def __init__(self, kappa=3.0):
        #super().__init__()
        self.name = "sigma median"
        self.kappa = kappa
        pass

    #@staticmethod
    def _realstack(self, frames):
        return _sigmaMedian(frames, np.std(frames, axis=0), np.median(frames, axis=0), self.kappa)
