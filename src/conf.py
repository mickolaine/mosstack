#!/usr/bin/python
# -*- coding: utf-8 -*-


'''
This file includes global variables. Someone on the Internet said declaring a variable global is a bad idea and
suggested something like this.
'''

from subprocess import check_output
class configurator:
    def __init__(self):
        pass
    
    def findSEx(self):
        pass

path     = "/media/data/Temp/astrostack/"             # Working path to use during procedure

sex      = "sex"                                     # Name of SExtractor executable. sex is default

rawprefix = "/media/Dee/Astrokuvat/2013-09-25/Andromeda/"
shortlist = ("Andromeda_2013-09-25_19.06.54.175028.cr2", "Andromeda_2013-09-25_19.15.11.803218.cr2", "Andromeda_2013-09-25_19.08.09.317766.cr2", "Andromeda_2013-09-25_19.15.40.536755.cr2")
             #"Andromeda_2013-09-25_19.15.40.536755.cr2", "Andromeda_2013-09-25_19.08.37.571008.cr2", "Andromeda_2013-09-25_19.16.08.441205.cr2",
             #"Andromeda_2013-09-25_19.09.05.428895.cr2", "Andromeda_2013-09-25_19.16.36.976464.cr2", "Andromeda_2013-09-25_19.09.33.511740.cr2")
rawlist = (
"Andromeda_2013-09-25_19.06.54.175028.cr2", "Andromeda_2013-09-25_19.15.11.803218.cr2", "Andromeda_2013-09-25_19.08.09.317766.cr2", "Andromeda_2013-09-25_19.15.40.536755.cr2",
"Andromeda_2013-09-25_19.08.37.571008.cr2", "Andromeda_2013-09-25_19.16.08.441205.cr2", "Andromeda_2013-09-25_19.09.05.428895.cr2", "Andromeda_2013-09-25_19.16.36.976464.cr2",
"Andromeda_2013-09-25_19.09.33.511740.cr2", "Andromeda_2013-09-25_19.17.04.994163.cr2", "Andromeda_2013-09-25_19.10.01.946076.cr2", "Andromeda_2013-09-25_19.17.33.131743.cr2",
"Andromeda_2013-09-25_19.10.30.087332.cr2", "Andromeda_2013-09-25_19.18.01.504639.cr2", "Andromeda_2013-09-25_19.10.58.246614.cr2", "Andromeda_2013-09-25_19.18.29.477342.cr2",
"Andromeda_2013-09-25_19.11.26.339471.cr2", "Andromeda_2013-09-25_19.18.57.431874.cr2", "Andromeda_2013-09-25_19.11.55.225213.cr2", "Andromeda_2013-09-25_19.19.26.545332.cr2",
"Andromeda_2013-09-25_19.12.23.153909.cr2", "Andromeda_2013-09-25_19.19.54.459613.cr2", "Andromeda_2013-09-25_19.12.50.976853.cr2", "Andromeda_2013-09-25_19.20.22.529075.cr2",
"Andromeda_2013-09-25_19.13.18.917980.cr2", "Andromeda_2013-09-25_19.20.50.918664.cr2", "Andromeda_2013-09-25_19.13.47.252966.cr2", "Andromeda_2013-09-25_19.21.18.982024.cr2",
"Andromeda_2013-09-25_19.14.15.240230.cr2", "Andromeda_2013-09-25_19.21.47.276579.cr2", "Andromeda_2013-09-25_19.14.43.169013.cr2"
            )

biasprefix = "/media/Dee/Astrokuvat/2013-09-25/Bias/"
biaslist   = (
"bias1.CR2",  "bias2.CR2",  "bias3.CR2",  "bias4.CR2",  "bias5.CR2",  "bias6.CR2",  "bias7.CR2",  "bias8.CR2",  "bias9.CR2",  "bias10.CR2", 
"bias11.CR2", "bias12.CR2", "bias13.CR2", "bias14.CR2", "bias15.CR2", "bias16.CR2", "bias17.CR2", "bias18.CR2", "bias19.CR2", "bias20.CR2",
"bias21.CR2", "bias22.CR2", "bias23.CR2", "bias24.CR2", "bias25.CR2", "bias26.CR2", "bias27.CR2", "bias28.CR2", "bias29.CR2", "bias30.CR2"
              )

darkprefix = "/media/Dee/Astrokuvat/2013-09-25/Dark/"
darklist   = (
"dark1.cr2", "dark2.cr2", "dark3.cr2", "dark4.cr2", "dark5.cr2", "dark6.cr2", "dark7.cr2", "dark8.cr2", "dark9.cr2", "dark10.cr2"
              )

flatprefix = "/media/Dee/Astrokuvat/2013-09-25/Flätit/"
flatlist   = (
"flat1.CR2", "flat2.CR2", "flat3.CR2", "flat4.CR2", "flat5.CR2", "flat6.CR2", "flat7.CR2"
              )