#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 2.10.2013

@author: Mikko Laine


"""

from abc import abstractmethod


class Registering:
    """
    Abstract class to show what Registering-type classes need to have.

    Not much as you see. self.register is the only one required and that handles everything. Implementations
    may have lots of other functions, but this is the only one called from outside.

    There's one problem with the design. Idea is for this class to work like Debayer or Stacker, to get an image or
    image list and return processed data. I implemented the transformation (TODO: which could be moved to it's own
    class) with command line ImageMagick tool 'convert'. That's why self.register does not return anything but instead
    saves new file on disk and writes information to project
    """

    def __init__(self):
        self.tform = None

    def register(self, frame):
        """
        Call everything necessary to register one frame

        Arguments:
        frame - a Frame-type object
        """

        # find stars
        self.match_stars(frame)

        # calculate transform
        self.tform.calculate_transform(frame)

        # do the transform
        return self.tform.affine_transform(frame)

    def register_old(self, imagelist, project):
        """
        Calls everything required for total registration process.

        Arguments:
        imagelist - a dict ('key': Photo)
        project - a Project-type object

        Return:
        Nothing, see classdoc
        """

    @abstractmethod
    def match_stars(self, frame):
        pass
    