#!/usr/bin/python
# -*- coding: utf-8 -*-


'''
This file includes classes for "global" configuration and for project configuration.

Global includes stuff like paths to programs, path for program data ...
Project holds lists of source files and information what has been done for them. Idea is you can continue the process
from any point forward.
'''

import configparser
import os
from subprocess import check_output, CalledProcessError


class ConfigAbstractor:
    """
    Class to read and write configuration files. I'm not sure about the format yet so I'll make this class to handle
    calls from system and project configuration classes.
    """

    def __init__(self, conftype="configparser"):
        """
        Argument type defines what kind of configuration system is used.

        I'll try configparser first. If it suits me, no need to try other
        """

        self.conf = configparser.ConfigParser()

    def read(self, file):
        """
        Read values from file
        """
        self.conf.read(file)

    def save(self, key, value, section="default"):
        """
        Save key and value under section in config file
        """

        if section not in self.conf:
            self.conf[section] = {}
        self.conf[section][key] = value

    def write(self, file):
        """
        Write values in file
        """
        with open(file, 'w') as configfile:
            self.conf.write(configfile)

class setup:
    """
    Class to control program settings
    """


    def __init__(self, file="/.config/pyAstroStack/settings"):
        """
        Checks the settings-file from specified location.

        Default location is ~/.config/pyAstroStack but it might be possible to change it somehow.
        I'm not sure how just yet. Or why would someone need to do that.
        """

        self.conf = ConfigAbstractor()
        self.file = os.getenv("HOME") + file

        if not os.path.exists(os.path.split(self.file)[0]):
            os.makedirs(os.path.split(self.file)[0])


        # If file does not exists, load some default values and write it
        if not os.path.exists(self.file):
            print("Seems like this is the first time you run pyAstroStack. Creating the setup file.")
            input("Press enter to continue.")
            try:
                print("Looking for SExtractor binaries...")
                self.conf.save("SExtractor", self.findSEx(), "Programs")
                print("Found " + self.conf.conf["Programs"]["SExtractor"])
            except IOError as e:
                print(e.args[0])
            print("Be aware that the temporary files can take a lot of space (from 1 GB to 20 GB)")
            path = input("Path for temporary files: ")
            self.conf.save("Path", path)
            self.conf.write(self.file)

        self.conf.read(self.file)


    def findSEx(self):
        """
        SExtractor executable is sometimes sex and sometimes sextractor. This finds out.
        """
        try:
            sexpath = check_output(["which", "sex"])
        except CalledProcessError:
            try:
                sexpath = check_output(["which", "sextractor"])
            except CalledProcessError:
                print("Can't find SExtractor executable. Only $PATH has been checked.")
                sexpath = input("Give full path to SExtractor executable, eg. ~/bin/sex")
                if not os.path.exists(sexpath):
                    raise IOError("File not found:", sexpath)
        #else:
        #    raise IOError("SExtractor not found.")
        return sexpath.decode().strip()



class project:
    """
    Class to control project information

    Project holds lists of source files and information what has been done for them. Idea is you can continue the
    process from any point forward.
    """

    extensions = (".CR2", ".cr2")   # TODO: Add here all supported extensions


    def __init__(self, pfile):
        """
        Initialize project

        Arguments:
        pfile - project file to use
        """

        self.projectfile = pfile
        self.conf = ConfigAbstractor()

    def readproject(self):
        """
        Read project settings from specified project file
        """
        if self.projectfile is None:
            # TODO: Change this error to a better one
            raise NameError("Project file not set, yet trying to access one. This shouldn't happen.")
        self.conf.read(self.projectfile)

    def initproject(self):
        """
        Initialize a project and project file
        """
        if os.path.exists(self.projectfile):
            print("Trying to initialize a new project, but the file already exists.")
            if input("Type y to rewrite: ") != "y":
                print("Try again using a file not already in use.")
                exit()


    def adddir(self, directory, imagetype):
        """
        Adds all suitable files in requested directory to project

        Arguments:
        path = directory to add
        imagetype is in (light, dark, bias, flat)
        """
        #directory = os.getcwd()
        print("Looking for RAW-files in current directory...")

        temp = os.listdir()
        filelist = []
        string = ""
        tempstr = ""
        for i in temp:
            tempstr += i + ", "
            if os.path.splitext(i)[1] in self.extensions:
                filelist.append(i)
                string += i + ", "

        if len(filelist) != 0:
            print("Found files " + string)
        else:
            print("None found. All files found are listed here: " + tempstr)
            ext = input("Please specify the extension for your files: ")
            for i in temp:
                if os.path.splitext(i)[1] == ext:
                    filelist.append(i)
                    string += i + ", "
        if len(filelist) == 0:
            print("No files found. Doing nothing.")

        # Check how many images are already in the list.
        if imagetype in self.conf.conf:
            n = max(self.conf.conf[imagetype]) + 1
        else:
            n = 1

        for i in filelist:
            self.conf.save(str(n), directory + "/" + i, imagetype)
            n += 1

        # Set reference only if not already set
        if "Reference" not in self.conf.conf:
            print("Setting first image in list as reference image.")
            ref = 1
            if input("Type y to change the reference image: ") == "y":
                pass  # TODO: Implementation
            self.conf.save("Reference", ref, imagetype)

        self.conf.write(self.projectfile)

    def addfile(self, rawpath, imagetype):
        """
        Adds a single file to project

        """
        print("Adding file " + rawpath)

        # Check how many images are already in the list.
        if imagetype in self.conf.conf:
            n = max(self.conf.conf[imagetype]) + 1
        else:
            n = 1

        self.conf.save(str(n), rawpath, imagetype)
        self.conf.write(self.projectfile)



path     = "/media/data/Temp/astrostack/"            # Working path to use during procedure

sex      = "sex"                                     # Name of SExtractor executable. sex is default

rawprefix  = "/media/Dee/Astrokuvat/2013-09-25/Andromeda/"
rawprefix2 = "/media/Dee/Astrokuvat/2013-10-21/Andromeda/"
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
rawlist2 = ("andromeda10.CR2",  "andromeda19.CR2",  "andromeda28.CR2",  "andromeda37.CR2",  "andromeda46.CR2",
"andromeda11.CR2",  "andromeda20.CR2",  "andromeda29.CR2",  "andromeda38.CR2",  "andromeda47.CR2",
"andromeda12.CR2",  "andromeda21.CR2",  "andromeda30.CR2",  "andromeda39.CR2",  "andromeda48.CR2",
"andromeda13.CR2",  "andromeda22.CR2",  "andromeda31.CR2",  "andromeda40.CR2",  "andromeda49.CR2",
"andromeda14.CR2",  "andromeda23.CR2",  "andromeda32.CR2",  "andromeda41.CR2",  "andromeda5.CR2",
"andromeda15.CR2",  "andromeda24.CR2",  "andromeda33.CR2",  "andromeda42.CR2",  "andromeda50.CR2",
"andromeda16.CR2",  "andromeda25.CR2",  "andromeda34.CR2",  "andromeda43.CR2",  "andromeda8.CR2",
"andromeda17.CR2",  "andromeda26.CR2",  "andromeda35.CR2",  "andromeda44.CR2",
"andromeda18.CR2",  "andromeda27.CR2",  "andromeda36.CR2",  "andromeda45.CR2")

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