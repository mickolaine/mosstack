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
from sys import version_info
from os.path import expanduser, exists, split
from os import makedirs


class ConfigAbstractor:
    """
    Class to read and write configuration files. I'm not sure about the format yet so I'll make this class to handle
    calls from system and project configuration classes.
    """

    def __init__(self):
        """
        Argument type defines what kind of configuration system is used.
        """

        self.conf = configparser.ConfigParser()

    def read(self, file):
        """
        Read values from file
        """
        self.conf.read(file)

    def save(self, key, value, section="Default"):
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
            #print("Config written to " + file)
            self.conf.write(configfile)


class Setup:
    """
    Initial setup. Find all the necessary programs and create paths.

    Old remove this:
    Class to control program settings
    """

    def __init__(self, file="/.config/mosstack/settings"):
        """
        Checks the settings-file from specified location.

        Default location is ~/.config/mosstack but it might be possible to change it somehow.
        I'm not sure how just yet. Or why would someone need to do that.
        """

        self.file = os.getenv("HOME") + file

        if not os.path.exists(os.path.split(self.file)[0]):
            os.makedirs(os.path.split(self.file)[0])

        # If file does not exists, load some default values and write it
        if not os.path.exists(self.file):

            print("Seems like this is the first time you run mosstack. Creating the setup file.")
            self.input("Press enter to continue.")

            try:
                print("Looking for SExtractor binaries...")
                try:
                    sexpath = self.findsex()
                    version_string = check_output([sexpath, "--version"]).split()[2]
                    if version_string == "2.4.4":
                        print("SExtractor version 2.4.4 found. This is an old version which contains a serious bug.")
                        print("Mosstack will not work with this version. Please upgrade SExtractor.")
                        exit()
                except CalledProcessError:
                    print("SExtractor executable not found in $PATH.")
                    sexpath = input("Give full path to SExtractor executable, eg. ~/bin/sex")
                    if not os.path.exists(sexpath):
                        raise IOError("File not found:", sexpath)
                Global.set("Programs", "SExtractor", sexpath)
                print("Found " + Global.get("Programs", "SExtractor"))
            except IOError as e:
                print(e.args[0])

            self.temppath()

    def temppath(self):
        """
        Ask for temporary path, do all necessary checks and create path if needed.
        """

        print("Mosstack requires a dedicated directory for temporary files.")
        print("Be aware that temp files can take a lot of space (from 1 GB to 20 GB) depending on your project.\n")
        temppath = input("Path for temporary files: ")

        # Make sure path ends in /
        if temppath[len(temppath) - 1] != "/":
            temppath += "/"

        if not exists(temppath):
            print("Path " + temppath + " not found. Creating...")
            try:
                makedirs(temppath)
                print("Done")
            except OSError:
                print("Failed to create directory " + temppath)

        Global.set("Default", "Path", temppath)
        if not exists(Global.get("Default", "Path") + "default.conv") or \
           not exists(Global.get("Default", "Path") + "default.param"):
            self.createSExConf()

    def createSExConf(self):
        """
        SExtractor requires two configuration files in the temp dir. This creates them. Files are from
        SExtractor distribution package and all rights belong to it's author.
        """

        # default.param
        param = """
NUMBER
FLUXERR_ISO
FLUX_AUTO
FLUXERR_AUTO
X_IMAGE
Y_IMAGE
FLAGS
        """

        # default.conv
        conv = """CONV NORM
# 3x3 ``all-ground'' convolution mask with FWHM = 2 pixels.
1 2 1
2 4 2
1 2 1"""

        defaultparam = open(Global.get("Default", "Path") + "default.param", 'w')
        defaultparam.write(param)
        defaultparam.close()

        defaultconv = open(Global.get("Default", "Path") + "default.conv", 'w')
        defaultconv.write(conv)
        defaultconv.close()

    def input(self, string):
        """
        Wrapper for input - raw_input differences between Python 2 and 3
        """

        version = version_info[0]

        if version == 2:
            return raw_input(string)
        elif version == 3:
            return input(string)
        else:
            print(version)
            print("It appears there's a new version of Python...")

    @staticmethod
    def findsex():
        """
        SExtractor executable is sometimes sex and sometimes sextractor. This finds out.
        """
        try:
            sexpath = check_output(["which", "sex"])
        except CalledProcessError:
            sexpath = check_output(["which", "sextractor"])

                #print("SExtractor executable not found in $PATH.")
                #sexpath = input("Give full path to SExtractor executable, eg. ~/bin/sex")
                #if not os.path.exists(sexpath):
                #    raise IOError("File not found:", sexpath)
        return sexpath.decode().strip()


class Config:
    """
    Configuration keeper object.
    """

    def __init__(self, conffile):
        """
        Create a new configuration file or open an existing one.

        Arguments
        conffile - file to hold the configurations
        """
        self.conffile = conffile
        self.conf = configparser.ConfigParser()

        if os.path.exists(self.conffile):
            return

        self.write(self.conffile)

    def get(self, section, key=None):
        """
        Return frame information under defined section

        Arguments:
        section = string to look for in configuration
        key     = key to look for in section, not needed

        Returns:
        dict {key: value}
        string value, if key defined

        If key or section is not found, KeyError is raised
        """

        self.conf.read(self.conffile)

        if section not in self.conf:
            raise KeyError("Section not found!")
        if key:
            if key not in self.conf[section]:
                raise KeyError("Key not found!")
            return self.conf[section][key]
        else:
            return dict(self.conf._sections[section])

    def set(self, section, key, value):
        """
        Set key: value under section in frame info

        Arguments:
        section
        key
        value

        Returns:
        Nothing
        """

        self.conf.read(self.conffile)

        if section not in self.conf:
            self.conf[section] = {}
        #print("Writing " + section + ", " + key + ", " + value)
        self.conf[section][key] = value
        #print("Setting " + key + " in section " + section + " changed to " + value)
        self.write(self.conffile)

    def remove(self, section, key):
        """
        Remove key from section

        return True if successful, False if key or section not found
        """

        self.conf.read(self.conffile)

        try:
            state = self.conf.remove_option(section, key)
            self.write(self.conffile)

        except configparser.NoSectionError:
            state = False

        return state

    def write(self, file):
        """
        Write values in file
        """
        with open(file, 'w') as configfile:
            #print("Config written to " + file)
            self.conf.write(configfile)


class Frame(Config):

    pass


class Project(Config):
    """
    A configurator object for project information. Inherits Config but adds some project specific stuff.
    This is something I probably should get rid off and do all the specific stuff elsewhere. Now for legacy reasons.
    """

    def __init__(self, pname=None):
        """
        Initialize project

        Arguments:
        pname - project name
        """

        try:
            self.sex   = Global.get("Programs", "SExtractor")
            self.path  = Global.get("Default", "path")
        except KeyError:
            self.setup = Setup()

        if pname is not None:

            pfile = self.path + "/" + pname + ".project"

            self.projectfile = pfile

            super().__init__(pfile)

            try:
                self.get("Default", "Initialized")
            except KeyError:
                self.set("Default", "Project name", pname)
                self.set("Setup", "Path", self.path)
                self.setdefaults()
                self.set("Default", "Initialized", "True")

    @staticmethod
    def load(pfile):
        """
        Load project from disc
        """

        #path  = Global.get("Default", "path")

        project = Project()
        project.conf = configparser.ConfigParser()
        project.conffile = pfile
        project.projectfile = project.conffile

        try:
            project.readproject()
        except:
            print("Project not found. This shouldn't happen.")

        return project

    def __init__old(self, pfile):
        """
        Initialize project

        Arguments:
        pfile - frame info file to use
        """

        super().__init__(pfile)

        self.projectfile = pfile

        self.sex  = Global.get("Programs", "SExtractor")
        self.path = Global.get("Default", "Path")

    @staticmethod
    def input(string):
        """
        Wrapper for input - raw_input differences between Python 2 and 3
        """

        version = version_info[0]

        if version == 2:
            return raw_input(string)
        elif version == 3:
            return input(string)
        else:
            print(version)
            print("It appears there's a new version of Python...")

    def readproject(self):
        """
        Read project settings from specified project file
        """
        if self.projectfile is None:
            raise NameError("Project file not set, yet trying to access one. This shouldn't happen.")
        if os.path.exists(self.projectfile):
            self.conf.read(self.projectfile)

    def initproject(self, pname):
        """
        Initialize a project and project file
        """
        pfile = self.path + "/" + pname + ".project"

        self.projectfile = pfile
        self.conffile = pfile
        self.conf = configparser.ConfigParser()
        if os.path.exists(self.projectfile):

            print("Trying to initialize a new project, but the file already exists.")
            if self.input("Type y to rewrite: ") != "y":
                print("Try again using a file not already in use.")
                exit()
            else:
                print("Using project file " + self.projectfile)
                os.unlink(self.projectfile)
        self.set("Default", "Project name", pname)
        self.set("Setup", "Path", Global.get("Default", "Path"))
        self.setdefaults()
        self.write(self.projectfile)

    def setdefaults(self):
        """
        Set default settings
        """
        self.set("Default", "debayer", "VNGCython")
        self.set("Default", "matcher", "Groth")
        self.set("Default", "transformer", "SkTransform")
        self.set("Default", "stack", "SigmaMedian")
        self.set("Default", "Kappa", "3")


class Global(object):
    """
    Global configurations
    """

    home = expanduser("~")
    configfile = home + "/.config/mosstack/settings"
    conf = configparser.ConfigParser()

    @staticmethod
    def get(section, key):

        Global.conf.read(Global.configfile)
        return Global.conf[section][key]

    @staticmethod
    def set(section, key, value):

        Global.conf.read(Global.configfile)
        if section not in Global.conf:
            Global.conf[section] = {}
        Global.conf[section][key] = value

        if not exists(split(Global.configfile)[0]):
            makedirs(split(Global.configfile)[0])

        with open(Global.configfile, 'w') as configfile:
            #print("Config written to " + Global.configfile)
            Global.conf.write(configfile)
