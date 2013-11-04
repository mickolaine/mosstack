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
#import getopt
import conf


def main(argv):
    """
    The idea is to call program with
    AstroStack projectname operation arguments
    """

    setup = conf.setup()

    helpstring = """
    pyAstroStack is run with:
    AstroStack.py <operation> <projectfile> <arguments>

    <operation>   - init, adddir, addfile, ... Try AstroStack help for full list
    <projectname> - File in configured working directory. Type the name without extension
    <arguments>   - Depends on <operation>
    """

    if len(argv) == 0:
        print(helpstring)
        exit()

    if argv[0] == "init":
        try:
            pname = argv[1]
        except IndexError:
            print("No project name specified")





    '''
    try:
        opts, args = getopt.getopt(argv, "hp:o:", ["project=", "ofile="])
    except getopt.GetoptError:
        print('test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("""
            test.py --project <projectname>
            """)
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    '''

if __name__ == "__main__":
    main(sys.argv[1:])