#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 22.7.2015

@author: Mikko Laine


"""


class Decoder:
    """
    Abstract class for decoding Raw files.

    Decoder needs to get path to raw file and path for file to create
    """

    def __init__(self):
        pass

    def decode(self, rawpath, fitspath):
        """
        Decode file found from rawpath and output it to fitspath
        """

