"""
The Command Line Interface for mosstack
"""

from . import Config, Debayer, Registering, Stacker, Batch
import argparse
import os


class CommandLine:
    """
    The Command line interface. This class parses command line arguments and calls for everything necessary
    """

    setup = Config.Setup()

    def __init__(self):
        """
        Initialize user interface and set project name if specified
        """

        self.wdir = Config.Global.get("Default", "Path")

        self.project = None
        self.project_name = None
        self.parser = argparse.ArgumentParser(
            description="Mosstack - an open source stacker for astronomical images."
        )
        self.subparsers = self.parser.add_subparsers()
        self.args = None

        # Set default values.
        self.debayerwrap = Debayer.VNGOpenCl
        self.matcher = Registering.Groth
        self.transformer = Registering.SkTransform
        self.stackerwrap = Stacker.SigmaMedian

        self.batch = {}

    def start(self, argv):
        """
        Start the program. This is called from main script
        """

        self.initparser()
        self.args = self.parser.parse_args(argv)
        self.parser.print_usage()

        # ##### Start workflow

        # ## Initiate project
        if self.args.project:
            print("Working with project " + self.args.project[0])
            self.set_project(self.args.project[0])
        elif self.args.init:
            print("Initializing new project")
            self.init_project()
        elif not self.initialized():
            print("No project initialized. Start a new with mosstack --init \"Foo\"")
        # ## Project ready

        # ## Check and load all files necessary
        if not self.checkfiles():
            exit("\nSome files weren't found. Please check your input.")

        # Settings

        if self.args.autostack:
            pass
        if self.args.setdebayer:
            pass
        if self.args.setregister:
            pass
        if self.args.setstacker:
            pass
        if self.args.reference:
            pass

        # Printouts, implies exiting with printed message

        if self.args.list:
            pass
        if self.args.settings:
            pass
        if self.args.size:
            pass

        # Single operations

        if self.args.clean:
            pass
        if self.args.fixsex:
            pass
        if self.args.remove:
            pass

        # The workflow of stacking process

        if self.args.light:
            self.addframes("light", self.args.light)
        if self.args.bias:
            self.addframes("bias", self.args.bias)
        if self.args.flat:
            self.addframes("flat", self.args.flat)
        if self.args.dark:
            self.addframes("dark", self.args.dark)

        if self.args.masterbias:
            self.addmaster("bias", self.args.masterbias)
        # elif self.args.biaslevel:
        #     pass
        if self.args.masterflat:
            self.addmaster("flat", self.args.masterflat)
        if self.args.masterdark:
            self.addmaster("dark", self.args.masterdark)

        if self.args.calibrate:
            # biaslevel
            pass
        if self.args.debayer:
            self.batch["light"].debayer(self.debayerwrap())
        if self.args.register:
            matcher = self.matcher()
            matcher.tform = self.transformer
            self.batch["light"].register(matcher)
        if self.args.crop:
            pass
        if self.args.stack:
            self.batch["light"].stack(self.stackerwrap())

    def print_values(self):
        """
        Testing function to check input and test functionality
        """
        print(self.args)

    def initparser(self):
        """
        Initialize parser and add all the necessary options
        """

        self.parser.add_argument("--init", nargs=1, metavar="name", help="Initialize project.")
        self.parser.add_argument("--project", nargs=1, metavar="name", help="Change active project.")

        self.parser.add_argument("--light", nargs='*', metavar="file", help='Add light frames  to project.')
        self.parser.add_argument("--bias", nargs='*', metavar="file", help='Add bias frames to project.')
        self.parser.add_argument("--flat", nargs='*', metavar="file", help='Add flat frames to project.')
        self.parser.add_argument("--dark", nargs='*', metavar="file", help='Add dark frames to project.')

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

        self.parser.add_argument("--masterbias", nargs=1, metavar="file", help="Add master bias frame")
        self.parser.add_argument("--masterflat", nargs=1, metavar="file", help="Add master flat frame")
        self.parser.add_argument("--masterdark", nargs=1, metavar="file", help="Add master dark frame")
        self.parser.add_argument("--biaslevel", nargs=1, type=float, metavar="float", help='Set bias level')

        self.parser.add_argument("--subtract", nargs=2, metavar=("batch", "calib"), help="Subtract calib from batch")
        self.parser.add_argument("--divide", nargs=2, metavar=("batch", "calib"), help="Divide batch by calib")

        self.parser.add_argument("--crop", nargs=4, type=int,
                                 metavar=("x0", "x1", "y0", "y1"),
                                 help='Crop image to coordinates')

        self.parser.add_argument("-c", "--calibrate", action='store_true', help='Calibrate frames')
        self.parser.add_argument("-d", "--debayer", action='store_true', help='Debayer frames')
        self.parser.add_argument("-r", "--register", action='store_true', help='Register frames')
        self.parser.add_argument("-s", "--stack", action='store_true', help='Stack frames')

        self.parser.add_argument("--autostack", action='store_true', help="Use default settings and do everything.")

    def initialized(self):
        """
        Check if project is initialized.

        :return: true if initialized, false if not
        """

        pfile = Config.Global.get("Default", "Project file")
        if os.path.isfile(pfile):
            self.project = Config.Project(pfile=pfile)
            return True
        else:
            return False

    def init_project(self):
        """
        Initialize the project

        :return: nothing
        """
        try:
            self.project = Config.Project()
            self.project_name = self.args.init[0]
            print(self.project_name)
            self.project.initproject(self.project_name)

            Config.Global.set("Default", "Project file", self.project.projectfile)
            print("New project started: \n" + self.project.projectfile)
            exit()
        except IndexError:
            print("Project name not specified. Try \"mosstack help\" and see what went wrong.")
            exit()

    def set_project(self, pfile):
        """
        Set project to match pname

        Returns False and prints an error if no such project in working directory
        """

        Config.Global.set("Default", "Project file", pfile)
        self.project = Config.Project(pfile=pfile)
        self.project_name = self.project.get("Default", "Project name")

        Config.Global.set("Default", "Project", self.project_name)

        print("Project set to " + pfile)

    def list_projects(self):
        """
        List all *.project files in working directory
        """
        pass

    def checkfiles(self):
        """
        Check all the files from all inputs before calling any functions

        :return: True, if all checks out. False if files not found. Also print out missing paths
        """
        filelist = []
        allfound = True
        for i in self.args.light, self.args.bias, self.args.flat, self.args.dark:
            if i:
                filelist = filelist + i

        for i in self.args.masterbias, self.args.masterflat, self.args.masterdark:
            if i:
                filelist.append(i)

        for i in filelist:
            try:
                CommandLine.absolutepath(i)
            except IOError:
                allfound = False
                print("File " + i + " not found. Check your input")
        if not allfound:
            return False
        return True

    def addframes(self, ftype, files):
        """
        Add frames to project. Files already checked in this point, so it's safe to assume
        paths are working

        :param ftype: Frame type (light, bias, flat, dark)
        :param files: List of file paths
        :return:
        """

        if ftype not in self.batch:
            self.batch[ftype] = Batch.Batch(self.project, ftype)

        for i in files:
            self.batch[ftype].addfile(CommandLine.absolutepath(i), ftype)

    def addmaster(self, ftype, file):
        """
        Add master frame

        :param ftype: Frame type (bias, flat, dark)
        :param file: Unix path of file to add
        """

        if ftype not in self.batch:
            self.batch[ftype] = Batch.Batch(project=self.project, ftype=ftype)
        self.batch[ftype].addmaster(file, ftype)

    @staticmethod
    def absolutepath(path, directory=False):
        """
        Check if path is relative and if so, return absolute path.

        Raise IOError if path does not exist.
        # TODO: Move to a better file
        """

        if directory:
            check = os.path.isdir
        else:
            check = os.path.isfile

        if check("/" + path):
            return path

        elif check(os.path.join(os.getcwd(), path)):
            return os.path.join(os.getcwd(), path)

        else:
            raise IOError()
