#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 23.10.2013

@author: Mikko Laine
"""

import numpy as np
import pyopencl as cl


class Demosaic:
    """
    Interface for Demosaicing classes. They must inherit this class

    """
    
    def __init__(self):
        """Prepare everything for running the demosaic-algorithms."""
        pass

    def demosaic(self, image):
        """
        Demosaic CFA data and return RGB data

        Arguments:
        image - 2D numpy.array holding the data

        Returns:
        [red, green, blue] as numpy.array
        """