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
import Stacking
import Registering
import Demosaic


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

    try:
        pname = argv[1]
        ppath = setup.conf.conf["Default"]["Path"] + pname + ".project"
        print(ppath)
        project = Conf.Project(ppath)
        project.readproject()

    except IndexError:
        print("No project name specified")
        exit()

    if argv[0] == "init":
        project.initproject(argv[1])

    if argv[0] == "adddir":

        if argv[2]:
            directory = argv[2]
        else:
            directory = os.getcwd()

        itype = imagetype()

        project.adddir(directory, itype)

    if argv[0] == "addfile":

        itype = imagetype()

        project.addfile(argv[2], itype)

    if argv[0] == "stack":
        # AstroStack stack <project> <itype> (<iname>)
        if argv[2] in ("light", "dark", "bias", "flat"):
            itype = argv[2]
        else:
            print("Invalid argument: " + argv[2])

        if itype == "light":
            batch = Photo.Batch(itype=itype, name=project.conf.conf["Default"]["project name"], project=project)
            # If you want to stack lights, they should be registered.
            # TODO: Test if they are
            for value in project.conf.conf["Registered frames"]:
                batch.add(project.conf.conf["Registered frames"][value])
        else:
            batch = Photo.Batch(itype=itype, name="master" + argv[2], project=project)
            for value in project.conf.conf[itype]:
                batch.add(project.conf.conf[itype][value])

        stacker = Stacking.Mean()
        try:
            stacker.stack(batch)
        #except:
        #    print("Something went wrong in stacking.")
        #    exit()
        finally:
            pass

    if argv[0] == "demosaic":
        # AstroStack demosaic <project>
        batch = Photo.Batch(itype="light", name=project.conf.conf["Default"]["project name"], project=project)
        for value in project.conf.conf["light"]:
            batch.add(project.conf.conf["light"][value])

        batch.demosaic(Demosaic.demosaic())

    if argv[0] == "register":
        # AstroStack register <project>
        batch = Photo.Batch(itype="light", name=project.conf.conf["Default"]["project name"], project=project)

        for value in project.conf.conf["light"]:
            batch.add(project.conf.conf["light"][value])

        reg = Registering.Reg()
        reg.register(batch)


if __name__ == "__main__":
    main(sys.argv[1:])