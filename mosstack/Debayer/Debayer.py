#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 23.10.2013

@author: Mikko Laine
"""


class Debayer:
    """
    Interface for debayering classes. They must inherit this class

    """
    
    def __init__(self):
        """Prepare everything for running the debayer-algorithms."""
        pass

    def debayer(self, file):
        """
        Debayer CFA data and return RGB data

        Arguments:
        image - 2D numpy.array holding the data

        Returns either:
        [red, green, blue] as numpy.array
        None, which means the subroutine has already written the data
        """