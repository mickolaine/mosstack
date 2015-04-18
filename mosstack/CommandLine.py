"""
The Command Line Interface for mosstack
"""

from . import Config, Debayer, Registering, Stacker
import argparse


class CommandLine:
    """
    The Command line interface. This class parses command line arguments and calls for everything necessary
    """

    setup = Config.Setup()

    def __init__(self):
        """
        Initialize user interface and set project name if specified
        """

        self.project = None
        self.parser = argparse.ArgumentParser()
        self.subparsers = self.parser.add_subparsers()

        # Set default values.
        self.debayerwrap = Debayer.VNGCython
        self.matcher = Registering.Groth
        self.transformer = Registering.SkTransform
        self.stackerwrap = Stacker.SigmaMedian

    def start(self, argv):

        self.initparser()
        self.args = self.parser.parse_args(argv)


    def initparser(self):
        """
        Initialize parser and add all the necessary options
        """

        self.parser.add_argument("--init", nargs=1, metavar="name", help="Initialize project.")
        self.parser.add_argument("--set", nargs=1, metavar="name", help="Change active project.")

        self.parser.add_argument("--files", nargs='*', metavar=("ftype", "files"), help='Add files to project.')

        self.parser.add_argument("--list", action='store_true', help='List all files in project')

        self.parser.add_argument("--remove", nargs=1, metavar="ID", help='Remove file from project')
        self.parser.add_argument("--reference", nargs=1, metavar="ID", help='Set reference frame')

        self.parser.add_argument("--setdebayer", nargs=1, metavar="ID", help='Set debayering algorithm')
        self.parser.add_argument("--setregister", nargs=1, metavar="ID", help='Set registering algorithm')
        self.parser.add_argument("--setstacker", nargs=1, metavar="ID", help='Set stacking algorithm')

        self.parser.add_argument("--size", action='store_true', help='Print size of project files')
        self.parser.add_argument("--clean", action='store_true', help='Remove temporary files')
        self.parser.add_argument("--fixsex", action='store_true', help='Fix SExtractor config files')
        self.parser.add_argument("--settings", action='store_true', help='Show all the settings')

        self.parser.add_argument("--addmaster", nargs=2, metavar=("ftype", "file"), help='Add master frame')
        self.parser.add_argument("--biaslevel", nargs=1, type=float, metavar="float", help='Set bias level')

        self.parser.add_argument("--subtract", nargs=2, metavar=("batch", "calib"), help="Subtract calib from batch")
        self.parser.add_argument("--divide", nargs=2, metavar=("batch", "calib"), help="Divide batch by calib")

        self.parser.add_argument("--crop", nargs=4, type=int, metavar=("x0", "x1", "y0", "y1"), help='Crop image to coordinates')

        self.parser.add_argument("-c", "--calibrate", action='store_true', help='Calibrate frames')
        self.parser.add_argument("-d", "--debayer", action='store_true', help='Debayer frames')
        self.parser.add_argument("-r", "--register", action='store_true', help='Register frames')
        self.parser.add_argument("-s", "--stack", action='store_true', help='Stack frames')

        self.parser.add_argument("--autostack", action='store_true', help="Use default settings and do everything.")
