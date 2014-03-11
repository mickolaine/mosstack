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
from pyastrostack import Conf, Demosaic, Registering, Stacker
import os
from pyastrostack.UserInterface import UserInterface
#import cProfile


def main(argv):
    """
    The idea is to call program with
    AstroStack projectname operation arguments
    """

    ui = UserInterface()

    setup = Conf.Setup()

    shorthelp = ui.shorthelp

    longhelp = ui.longhelp
    project  = None
    section  = None
    calib    = None

    if len(argv) == 0:
        print(shorthelp)
        exit()

    if argv[0] == "init":
        project = Conf.Project(setup.get("Default", "Path") + argv[1] + ".project")
        project.initproject(argv[1])
        setup.set("Default", "Project", argv[1])

    try:
        pname = setup.get("Default", "Project")
        ppath = setup.get("Default", "Path") + pname + ".project"
        print("Current project is " + ppath + "\n")
        project = Conf.Project(ppath)
        project.readproject()
        ui.setproject(project)

    except IndexError:
        print("No project name specified")
        exit()

    if argv[0] == "help":
        print(longhelp)

    if argv[0] == "init":
        exit()

    elif argv[0] == "set":

        if argv[1] == "project":
            if argv[2]:
                pname = argv[2]
                setup.set("Default", "Project", pname)
                ppath = setup.get("Default", "Path") + pname + ".project"
                project = Conf.Project(ppath)
            else:
                print("No project name specified. Available projects are: Implement this")
                print("Try AstroStack set project <project name>, without extension.")
        elif argv[1] == "demosaic":
            options = Demosaic.__all__
            ui.set("Demosaic", options, argv[2])
        elif argv[1] == "register":
            options = Registering.__all__
            ui.set("Register", options, argv[2])
        elif argv[1] == "stack":
            options = Stacker.__all__
            ui.set("Stack", options, argv[2])

        else:
            print("Don't know how to set " + argv[1])
            print("Possible options to set are \n project\n demosaic\n register\n stack")

    elif argv[0] == "list":

        if len(argv) == 1:
            print("Settings to list are \n demosaic\n register\n stack")
        else:
            if argv[1] == "demosaic":
                options = Demosaic.__all__
            elif argv[1] == "register":
                options = Registering.__all__
            elif argv[1] == "stack":
                options = Stacker.__all__
            else:
                print("No such setting " + argv[1])
                print("Possible settings are \n demosaic\n register\n stack")
            ui.list(argv[1], options)

    elif argv[0] == "dir":

        if argv[1]:
            directory = argv[1]
        else:
            directory = os.getcwd()

        itype = argv[2]
        ui.adddir(directory, itype)
        #project.adddir(directory, itype)

    elif argv[0] == "file":

        itype = argv[2]
        project.addfile(argv[1], itype)

    elif argv[0] == "stack":
        # AstroStack stack <srcname>
        srclist = ("light", "dark", "bias", "flat", "rgb", "calib", "reg")
        if argv[1] in srclist:
            section = argv[1]
        else:
            print("Invalid argument: " + argv[1])
            print("<itype> has to be one of: " + str(srclist))

        ui.stack(section)

    elif argv[0] == "demosaic":
        # AstroStack demosaic <srcname>

        if argv[1]:
            genname = argv[1]
        else:
            print("Srcname not defined. Exiting...")
            exit()

        ui.demosaic(genname)

    elif argv[0] == "register":
        # AstroStack register <srcname>

        if argv[1]:
            section = argv[1]
        else:
            print("Srcname not defined. Exiting...")
            exit()

        ui.register(section)

    elif argv[0] == "subtract":
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

    elif argv[0] == "divide":
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

    else:
        print("Invalid operation: " + argv[0])
        print(shorthelp)
        exit()

if __name__ == "__main__":
    main(sys.argv[1:])