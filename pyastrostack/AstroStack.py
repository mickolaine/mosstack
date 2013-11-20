#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 28.10.2013

@author: Mikko Laine

Main program for pyAstroStack.

This command line user interface is used to create a project file to store information
about source files and temporary files in working directory. This same UI is then used
to run different stacking operations according to the project file.
"""

import sys
import Conf
import os
import Photo
from UserInterface import UserInterface
from Stacker import Mean
#from Registering import *
#from Demosaic import *


def imagetype():
    """
    Ask user light, bias, dark or flat

    return 1, 2, 3 or 4

    Consider moving this elsewhere. Maybe a class for user interactions?
    """

    print("Specify the type of images.")
    print("1 Light")
    print("2 Bias")
    print("3 Dark")
    print("4 Flat")
    number = int(input("Select number: "))
    if number == 1:
        imaget = "light"
    elif number == 2:
        imaget = "bias"
    elif number == 3:
        imaget = "dark"
    elif number == 4:
        imaget = "flat"
    else:
        "Invalid input. Try again."

    return imaget


def main(argv):
    """
    The idea is to call program with
    AstroStack projectname operation arguments
    """

    ui = UserInterface()

    setup = Conf.Setup()

    shorthelp = """
    pyAstroStack is run with:
    AstroStack.py <operation> <projectfile> <arguments>

    <operation>   - init, adddir, addfile, ... Try AstroStack help for full list
    <projectname> - File in configured working directory. Type the name without extension
    <arguments>   - Depends on <operation>
    """

    longhelp = shorthelp

    if len(argv) == 0:
        print(shorthelp)
        exit()

    if len(argv) == 1:
        if argv[0] == "help":
            print(longhelp)
        exit()

    if argv[0] == "init":
        project = Conf.Project(setup.get("Default", "Path") + argv[1] + ".project")
        project.initproject(argv[1])
        setup.set("Default", "Project", argv[1])

    try:
        pname = setup.get("Default", "Project")
        ppath = setup.get("Default", "Path") + pname + ".project"
        print(ppath)
        project = Conf.Project(ppath)
        project.readproject()
        ui.setproject(project)

    except IndexError:
        print("No project name specified")
        exit()

    if argv[0] == "set":
        if argv[1]:
            pname = argv[1]
            setup.set("Default", "Project", pname)
            ppath = setup.get("Default", "Path") + pname + ".project"
            project = Conf.Project(ppath)
        else:
            print("No project name specified. Available projects are: Implement this")
            print("Try AstroStack set <project name>, without extension.")

    if argv[0] == "adddir":

        if argv[1]:
            directory = argv[1]
        else:
            directory = os.getcwd()

        itype = argv[2]
        project.adddir(directory, itype)

    if argv[0] == "addfile":

        itype = argv[2]
        project.addfile(argv[1], itype)

    if argv[0] == "stack":
        # AstroStack stack <srcname>
        srclist = ("light", "dark", "bias", "flat", "rgb", "calib", "reg")
        if argv[1] in srclist:
            section = argv[1]
        else:
            print("Invalid argument: " + argv[1])
            print("<itype> has to be one of: " + str(srclist))

        ui.stack(section)

    if argv[0] == "demosaic":
        # AstroStack demosaic <srcname>

        if argv[1]:
            section = argv[1]
        else:
            print("Srcname not defined. Exiting...")
            exit()

        ui.demosaic(section)

    if argv[0] == "register":
        # AstroStack register <srcname>

        if argv[1]:
            section = argv[1]
        else:
            print("Srcname not defined. Exiting...")
            exit()

        ui.register(section)

    if argv[0] == "subtract":
        # AstroStack subtract <srcname> <calibname>

        if argv[1]:
            section = argv[1]
            if argv[2]:
                calib = argv[2]
            else:
                print("Calibname not defined. Exiting...")
                exit()
        else:
            print("Srcname not defined. Exiting...")
            exit()

        ui.subtract(section, calib)

    if argv[0] == "divide":
        # AstroStack divide <srcname> <calibname>

        if argv[1]:
            section = argv[1]
            if argv[2]:
                calib = argv[2]
            else:
                print("Calibname not defined. Exiting...")
                exit()
        else:
            print("Srcname not defined. Exiting...")
            exit()

        ui.divide(section, calib)

if __name__ == "__main__":
    main(sys.argv[1:])