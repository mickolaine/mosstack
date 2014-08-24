"""
Class for Sigma clipping stacker.
"""

from .. Stacker.Stacking import Stacking
import numpy as np
import pyximport
pyximport.install(setup_args={'include_dirs': [np.get_include()]})
from . _math import _sigmaClip


class SigmaClip(Stacking):
    """
    Sigma clipping will clip off values that are too far from median value and calculate the average from the remaining
    """

    def __init__(self):
        #super().__init__()
        self.name = "sigma clipping"
        pass

    @staticmethod
    def _realstack(frames):
        return _sigmaClip(frames, np.std(frames, axis=0), np.median(frames, axis=0), 3.0)