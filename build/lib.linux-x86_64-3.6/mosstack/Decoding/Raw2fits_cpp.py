#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 22.7.2015

@author: Mikko Laine

"""

from os.path import exists
from subprocess import call
from .. Decoding.Decoder import Decoder
from .. Decoding import raw2fits


class Raw2fits_cpp(Decoder):
    """
    Raw2fits.cpp based decoding
    """

    def __init__(self):
        pass

    @staticmethod
    def decode(rawpath, fitspath):
        """
        Decode file found from rawpath and output it to fitspath

        This implementation uses raw2fits.cpp to do the actual work
        """

        if exists(fitspath):
            print("Image already converted.")
            return

        print("Converting RAW image...")
        if raw2fits.raw2fits(rawpath, fitspath):
            print("Something went wrong... There might be helpful output from Rawtran above this line.")
            if exists(fitspath):
                print("File " + fitspath + " was created but dcraw returned an error.")
            else:
                print("Unable to continue.")
        else:
            print("Conversion successful!")


