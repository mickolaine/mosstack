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
            self.conf.write(configfile)


class Setup:
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
            self.input("Press enter to continue.")

            try:
                print("Looking for SExtractor binaries...")
                self.conf.save("SExtractor", self.findsex(), "Programs")
                print("Found " + self.conf.conf["Programs"]["SExtractor"])
            except IOError as e:
                print(e.args[0])

            print("Be aware that the temporary files can take a lot of space (from 1 GB to 20 GB)")
            temppath = self.input("Path for temporary files: ")

            # Make sure path ends in /
            if temppath[len(temppath)-1] != "/":
                temppath += "/"

            print("You have to manually copy SExtractor files default.param adn default.conv to temp directory.")
            self.conf.save("Path", temppath)
            self.conf.write(self.file)

        self.conf.read(self.file)

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

    def findsex(self):
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
                sexpath = self.input("Give full path to SExtractor executable, eg. ~/bin/sex")
                if not os.path.exists(sexpath):
                    raise IOError("File not found:", sexpath)
        #else:
        #    raise IOError("SExtractor not found.")
        return sexpath.decode().strip()

    def get(self, section, key=None):
        """
        Return project information under defined section

        Arguments:
        section = string to look for in configuration
        key     = key to look for in section, not needed

        Returns:
        dict {key: value}
        string value, if key defined
        """

        self.conf.read(self.file)

        if key:
            return self.conf.conf[section][key]
        else:
            return dict(self.conf.conf._sections[section])

    def set(self, section, key, value):
        """
        Set key: value under section in project settings

        Arguments:
        section
        key
        value

        Returns:
        Nothing
        """

        self.conf.read(self.file)
        self.conf.save(key, value, section)
        self.conf.write(self.file)


class Project_old:
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
        self.setup = Setup()
        self.sex   = self.setup.get("Programs", "SExtractor")
        self.path  = self.setup.get("Default", "path")

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

    def readproject(self):
        """
        Read project settings from specified project file
        """
        if self.projectfile is None:
            # TODO: Change this error to a better one
            raise NameError("Project file not set, yet trying to access one. This shouldn't happen.")
        if os.path.exists(self.projectfile):
            self.conf.read(self.projectfile)

    def initproject(self, pname):
        """
        Initialize a project and project file
        """
        if os.path.exists(self.projectfile):
            print("Trying to initialize a new project, but the file already exists.")
            if self.input("Type y to rewrite: ") != "y":
                print("Try again using a file not already in use.")
                exit()
            else:
                print("Using project file " + self.projectfile)
                os.unlink(self.projectfile)
        self.conf.save("Project name", pname)
        self.set("Setup", "Path", self.setup.conf.conf["Default"]["Path"])
        self.set("Default", "demosaic", "VNGCython")
        self.set("Default", "register", "Groth_Skimage")
        self.set("Default", "stack", "Median")
        self.conf.write(self.projectfile)

    def adddir(self, directory, imagetype):
        """
        Adds all suitable files in requested directory to project

        Arguments:
        path = directory to add
        imagetype is in (light, dark, bias, flat)
        """
        self.readproject()
        print("Looking for RAW-files in specified directory...")

        # Make sure path ends in /
        if directory[-1] != "/":
            directory += "/"

        temp = os.listdir(directory)
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
            ext = self.input("Please specify the extension for your files: ")
            for i in temp:
                if os.path.splitext(i)[1] == ext:
                    filelist.append(i)
                    string += i + ", "
        if len(filelist) == 0:
            print("No files found. Doing nothing.")

        # Check how many images are already in the list.
        if imagetype in self.conf.conf:
            print(max(self.conf.conf[imagetype]))
            n = int(max(self.conf.conf[imagetype])) + 1
        else:
            n = 1

        for i in filelist:
            print(directory + i)
            self.conf.save(str(n), directory + i, imagetype)
            n += 1

        # Set reference only if not already set
        if "Reference" not in self.conf.conf:
            print("Setting first image in list as reference image.")
            ref = "1"
            if self.input("Type y to change the reference image (anything else to continue): ") == "y":
                pass  # TODO: Implementation
            self.conf.save(imagetype, ref, "Reference images")

        self.conf.write(self.projectfile)

    def hassection(self, section):
        """
        Check if project file has section

        Arguments:
        section - string to check

        Returns:
        Boolean
        """

        if section in self.conf.conf:
            return True
        else:
            return False

    def haskey(self, section, key):
        """
        Check if project file has key in section

        Also check the section first and return False if not
        """

        if not self.hassection(section):
            return False

        if key in self.conf.conf[section]:
            return True
        else:
            return False

    def addfile(self, rawpath, imagetype):
        """
        Adds a single file to project

        """
        self.readproject()
        print("Adding file " + rawpath)

        # Check how many images are already in the list.
        if imagetype in self.conf.conf:
            n = int(max(self.conf.conf[imagetype])) + 1
        else:
            n = 1

        self.conf.save(str(n), rawpath, imagetype)
        self.conf.write(self.projectfile)

    def write(self):
        self.conf.write(self.projectfile)

    def get(self, section, key=None):
        """
        Return project information under defined section

        Arguments:
        section = string to look for in configuration
        key     = key to look for in section, not needed

        Returns:
        dict {key: value}
        string value, if key defined
        """

        self.conf.read(self.projectfile)

        if key:
            return self.conf.conf[section][key]
        else:
            return dict(self.conf.conf._sections[section])

    def set(self, section, key, value):
        """
        Set key: value under section in project settings

        Arguments:
        section
        key
        value

        Returns:
        Nothing
        """

        self.conf.read(self.projectfile)

        self.conf.save(key, value, section)


class Frame_old:
    """
    Class to save frame information.

    Frame has information of one photo frame and what has been done for it.
    At the moment project file holds most of this, but for 0.2 this might change # TODO: check this before 0.2
    At first Frame will include information about image dimensions so the files won't have to be loaded every time
    Image.shape is asked.
    """

    def __init__(self, ffile, project):
        """
        Initialize project

        Arguments:
        ffile - frame info file to use
        project - project configurator. remove if not needed
        """

        self.framefile = ffile
        self.conf = ConfigAbstractor()
        self.project = project

        if os.path.exists(self.framefile):
            return

        #self.set("Default", "Loaded", "0")
        self.conf.write(self.framefile)

    def readproject(self):
        """
        Read frame info from specified file
        """
        if self.framefile is None:
            self.initproject(self.fname)
        if os.path.exists(self.projectfile):
            self.conf.read(self.projectfile)

    def initproject(self, fnumber):
        """
        Initialize a frame file

        If file exists, do nothing. TODO: Change this
        """
        if os.path.exists(self.framefile):
            print("File already exists yet trying to create a new one.")

        self.conf.save("Frame number", fnumber)
        self.set("Default", "Loaded", "0")
        self.conf.write(self.framefile)

    def get(self, section, key=None):
        """
        Return frame information under defined section

        Arguments:
        section = string to look for in configuration
        key     = key to look for in section, not needed

        Returns:
        dict {key: value}
        string value, if key defined
        """

        self.conf.read(self.framefile)
        if key:
            return self.conf.conf[section][key]
        else:
            return dict(self.conf.conf._sections[section])

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
        self.conf.read(self.framefile)
        self.conf.save(key, value, section)
        self.conf.write(self.framefile)

    def hassection(self, section):
        """
        Check if project file has section

        Arguments:
        section - string to check

        Returns:
        Boolean
        """

        if section in self.conf.conf:
            return True
        else:
            return False

    def haskey(self, section, key):
        """
        Check if project file has key in section

        Also check the section first and return False if not
        """

        if not self.hassection(section):
            return False

        if key in self.conf.conf[section]:
            return True
        else:
            return False


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
        self.conf[section][key] = value

        self.write(self.conffile)

    def write(self, file):
        """
        Write values in file
        """
        with open(file, 'w') as configfile:
            self.conf.write(configfile)


class Frame(Config):

    pass


class Project(Config):
    """
    A configurator object for project information. Inherits Config but adds some project specific stuff.
    This is something I probably should get rid off and do all the specific stuff elsewhere. Now for legacy reasons.
    """

    def __init__(self, pname):
        """
        Initialize project

        Arguments:
        pname - project name
        """

        self.setup = Setup()
        self.path  = self.setup.get("Default", "path")
        pfile = self.path + "/" + pname + ".project"

        super().__init__(pfile)
        self.projectfile = pfile

        self.sex   = self.setup.get("Programs", "SExtractor")

        try:
            self.get("Default", "Initialized")
            print("Trying to initialize a new project, but the file already exists.")
            if self.input("Type y to rewrite: ") != "y":
                print("Try again using a file not already in use.")
                exit()
            else:
                print("Using project file " + self.projectfile)
                os.unlink(self.projectfile)
        except KeyError:
            pass
        self.set("Default", "Project name", pname)
        self.set("Setup", "Path", self.path)
        self.set("Default", "demosaic", "VNGCython")
        self.set("Default", "register", "Groth_Skimage")
        self.set("Default", "stack", "Median")
        self.set("Default", "Initialized", "True")
        self.write(self.projectfile)

    def __init__old(self, pfile):
        """
        Initialize project

        Arguments:
        pfile - frame info file to use
        """

        super().__init__(pfile)

        self.projectfile = pfile
        self.setup = Setup()
        self.sex   = self.setup.get("Programs", "SExtractor")
        self.path  = self.setup.get("Default", "path")

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
            # TODO: Change this error to a better one
            raise NameError("Project file not set, yet trying to access one. This shouldn't happen.")
        if os.path.exists(self.projectfile):
            self.conf.read(self.projectfile)

    def initproject(self, pname):
        """
        Initialize a project and project file
        """
        if os.path.exists(self.projectfile):
            print("Trying to initialize a new project, but the file already exists.")
            if self.input("Type y to rewrite: ") != "y":
                print("Try again using a file not already in use.")
                exit()
            else:
                print("Using project file " + self.projectfile)
                os.unlink(self.projectfile)
        self.set("Default", "Project name", pname)
        self.set("Setup", "Path", self.setup.conf.conf["Default"]["Path"])
        self.set("Default", "demosaic", "VNGCython")
        self.set("Default", "register", "Groth_Skimage")
        self.set("Default", "stack", "Median")
        self.write(self.projectfile)


    '''
    def adddir(self, directory, imagetype):
        """
        Adds all suitable files in requested directory to project

        Arguments:
        path = directory to add
        imagetype is in (light, dark, bias, flat)
        """
        self.readproject()
        print("Looking for RAW-files in specified directory...")

        # Make sure path ends in /
        if directory[-1] != "/":
            directory += "/"

        temp = os.listdir(directory)
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
            ext = self.input("Please specify the extension for your files: ")
            for i in temp:
                if os.path.splitext(i)[1] == ext:
                    filelist.append(i)
                    string += i + ", "
        if len(filelist) == 0:
            print("No files found. Doing nothing.")

        # Check how many images are already in the list.
        if imagetype in self.conf.conf:
            print(max(self.conf.conf[imagetype]))
            n = int(max(self.conf.conf[imagetype])) + 1
        else:
            n = 1

        for i in filelist:
            print(directory + i)
            self.conf.save(str(n), directory + i, imagetype)
            n += 1

        # Set reference only if not already set
        if "Reference" not in self.conf.conf:
            print("Setting first image in list as reference image.")
            ref = "1"
            if self.input("Type y to change the reference image (anything else to continue): ") == "y":
                pass  # TODO: Implementation
            self.conf.save(imagetype, ref, "Reference images")

        self.conf.write(self.projectfile)

    def hassection(self, section):
        """
        Check if project file has section

        Arguments:
        section - string to check

        Returns:
        Boolean
        """

        if section in self.conf.conf:
            return True
        else:
            return False

    def haskey(self, section, key):
        """
        Check if project file has key in section

        Also check the section first and return False if not
        """

        if not self.hassection(section):
            return False

        if key in self.conf.conf[section]:
            return True
        else:
            return False

    def addfile(self, rawpath, imagetype):
        """
        Adds a single file to project

        """
        self.readproject()
        print("Adding file " + rawpath)

        # Check how many images are already in the list.
        if imagetype in self.conf.conf:
            n = int(max(self.conf.conf[imagetype])) + 1
        else:
            n = 1

        self.conf.save(str(n), rawpath, imagetype)
        self.conf.write(self.projectfile)

    def write(self):
        self.conf.write(self.projectfile)

    def get(self, section, key=None):
        """
        Return project information under defined section

        Arguments:
        section = string to look for in configuration
        key     = key to look for in section, not needed

        Returns:
        dict {key: value}
        string value, if key defined
        """

        self.conf.read(self.projectfile)

        if key:
            return self.conf.conf[section][key]
        else:
            return dict(self.conf.conf._sections[section])

    def set(self, section, key, value):
        """
        Set key: value under section in project settings

        Arguments:
        section
        key
        value

        Returns:
        Nothing
        """

        self.conf.read(self.projectfile)

        self.conf.save(key, value, section)
    '''
