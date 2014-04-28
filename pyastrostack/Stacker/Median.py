"""
Class for median stacker.
"""

from .. Stacker.Stacking import Stacking
import numpy as np
import gc
import math
import datetime   # For profiling


class Median(Stacking):
    """
    Each pixel will be a median value of the entire stack.
    """

    def __init__(self):
        #super().__init__()
        pass

    @staticmethod
    def _realstack(frames):
        return np.median(frames, axis=0)
