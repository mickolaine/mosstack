#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 28.10.2013

@author: micko

Main program for pyAstroStack.

This command line user interface is used to create a project file to store information
about source files and temporary files in working directory. This same UI is then used
to run different stacking operations according to the project file.
'''

import sys, getopt

def main(argv):
    
    try:
        opts, args = getopt.getopt(argv,"hp:o:",["project=","ofile="])
    except getopt.GetoptError:
        print('test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
      
if __name__ == "__main__":
    main(sys.argv[1:])