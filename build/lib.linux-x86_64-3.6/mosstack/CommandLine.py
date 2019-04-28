"""
The Command Line Interface for mosstack
"""

from . import Debayer, Config, Registering, Stacker, Batch
#from . Debayer import VNGCython, BilinearCython, VNGOpenCl, BilinearOpenCl
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
        self.debayerwrap = Debayer.VNGC
        self.matcher = Registering.Groth
        self.transformer = Registering.SkTransform
        self.stackerwrap = Stacker.SigmaMedian

        self.masterbias = None
        self.masterflat = None
        self.masterdark = None

        self.batch = {}

    def start(self, argv):
        """
        Start the program. This is called from main script
        """

        self.initparser()
        self.args = self.parser.parse_args(argv)

        if not argv:
            self.parser.print_usage()

        # ##### Start workflow

        # ## Initiate project
        if self.args.project:
            self.set_project(self.args.project[0])
            print("Working with project " + self.args.project[0])
        elif self.args.init:
            print("Initializing new project")
            self.init_project()
        elif not self.initialized():
            print("No project initialized. Start a new with mosstack --init \"Foo\"")
            exit()

        """
        for ftype in ("light", "bias", "flat", "dark"):
            try:
                if self.project.get(ftype):
                    self.batch[ftype] = Batch.Batch(self.project, ftype=ftype)
            except KeyError:
                pass
        """
        # ## Project ready

        # ## Check and load all files necessary
        if not self.checkfiles():
            exit("\nSome files weren't found. Please check your input.")

        # Settings

        # Autostack chooses good general settings which work for most stacks.
        if self.args.autostack:
            self.args.calibrate = True
            self.args.debayer = True
            self.args.register = True
            self.args.stack = True

        if self.args.setdebayer:
            options = Debayer.__all__
            self.set("Debayer", options, self.args.setdebayer[0])

        if self.args.setmatcher:
            options = Registering.matcher
            self.set("Matcher", options, self.args.setmatcher[0])

        if self.args.settransformer:
            options = Registering.transformer
            self.set("Transformer", options, self.args.settransformer[0])

        if self.args.setstacker:
            options = Stacker.__all__
            self.set("Stack", options, self.args.setstacker[0])

        if self.args.setkappa:
            try:
                kappa = float(self.args.setkappa[0])
                self.project.set("Default", "Kappa", kappa)
                print("Kappa set to " + str(self.args.setkappa[0]))
            except ValueError:
                print("Setting Kappa to " + str(self.args.setkappa[0]) + " failed. Try a small float.")
                exit()

        if self.args.reference:
            self.batch["light"].setRef(self.args.reference[0])

        # Printouts, implies exiting with printed message

        if self.args.list:
            self.listframes()
        if self.args.settings:
            self.settings()
        if self.args.size:
            self.size()

        # Single operations

        if self.args.clean:
            print("Cleaning up project files.")
            for i in self.project.filelist(temp=True):
                if os.path.isfile(i):
                    os.remove(i)

            print("Files:")
            for i in self.project.filelist():
                print(i)
            print("are not removed. They must be removed manually.")
            exit()

        if self.args.fixsex:
            Config.Setup.createSExConf()
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

        self.batch = {}

        for ftype in ("light", "bias", "flat", "dark"):
            try:
                if self.project.get(ftype):
                    self.batch[ftype] = Batch.Batch(self.project, ftype=ftype)
            except KeyError:
                pass

        if self.args.masterbias:
            self.addmaster("bias", self.args.masterbias)
        elif self.args.biaslevel:
            try:
                self.batch["light"].setbiaslevel(self.args.biaslevel[0])
            except ValueError:
                print(str(self.args.biaslevel[0]) + " not a valid biaslevel. Try an integer or float.")
                exit()
        if self.args.masterflat:
            self.addmaster("flat", self.args.masterflat)
        if self.args.masterdark:
            self.addmaster("dark", self.args.masterdark)

        if self.args.calibrate:
            print("Calibrating...")
            self.preparecalib()

            for i in self.batch["light"].frames:
                self.batch["light"].frames[i].fphase = "orig"
                self.batch["light"].calibrate(bias=self.masterbias, 
                                              dark=self.masterdark, 
                                              flat=self.masterflat)
                #self.batch["light"].frames[i].calibrate(self.stackerwrap(), bias=self.masterbias,
                #                                        dark=self.masterdark, flat=self.masterflat)

        if self.args.debayer:
            for i in self.batch["light"].frames:
                self.batch["light"].frames[i].fphase = "calib"
                print(self.batch["light"].frames[i].getpath())
            self.batch["light"].debayer(self.debayerwrap)

        if self.args.register:
            for i in self.batch["light"].frames:
                self.batch["light"].frames[i].fphase = "rgb"
            matcher = self.matcher()
            matcher.tform = self.transformer
            self.batch["light"].register(matcher)

        if self.args.crop:
            try:
                crop = self.args.crop
                xrange = int(crop[0]), int(crop[1])
                yrange = int(crop[2]), int(crop[3])
            except ValueError:
                print("Values " + crop[0] + ", " + crop[1] + ", " + crop[2] +
                      " and " + crop[3] + " should be integers.")
                exit()
            for i in self.batch["light"].frames:
                self.batch["light"].fphase = "reg"
                self.batch["light"].frames[i].crop(xrange, yrange)

        if self.args.stack:
            for i in self.batch["light"].frames:
                self.batch["light"].frames[i].fphase = "reg"
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
        self.parser.add_argument("--setmatcher", nargs=1, metavar="ID", help='Set matching algorithm')
        self.parser.add_argument("--settransformer", nargs=1, metavar="ID", help='Set transforming algorithm')
        self.parser.add_argument("--setstacker", nargs=1, metavar="ID", help='Set stacking algorithm')

        self.parser.add_argument("--setkappa", nargs=1, metavar="float", help="Set kappa for sigma stackers")

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
        try:
            pfile = Config.Global.get("Default", "Project file")
        except KeyError:
            return False
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
            self.project.initproject(self.project_name)

            Config.Global.set("Default", "Project", self.project_name)
            Config.Global.set("Default", "Project file", self.project.projectfile)
            print("New project started: \n" + self.project.projectfile)

        except IndexError:
            print("Project name not specified. Try \"mosstack help\" and see what went wrong.")
            exit()

    def set_project(self, pname):
        """
        Set project to match pname

        Returns False and prints an error if no such project in working directory
        """

        if not Config.Project.projectexists(pname):
            print("No such project " + pname + ". Start a new one with mosstack --init " + pname)
            return False

        self.project = Config.Project(pname=pname)
        self.project_name = pname
        Config.Global.set("Default", "Project", self.project_name)
        Config.Global.set("Default", "Project file", self.project.projectfile)
        print("Project set to " + self.project.path)

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
            self.batch[ftype] = Batch.Batch(self.project, ftype=ftype)

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
        if ftype == "bias":
            self.masterbias = self.batch["bias"].master
        if ftype == "flat":
            self.masterflat = self.batch["flat"].master
        if ftype == "dark":
            self.masterdark = self.batch["dark"].master
        self.batch[ftype].addmaster(file, ftype)

    def preparecalib(self):
        """
        Prepare calibration frames.

        This belongs in workflow, but is too long to fit there properly
        """

        # Prepare masterbias
        if "bias" in self.batch.keys():
            print("Preparing bias master frame")
            self.batch["bias"].stack(self.stackerwrap())
            self.masterbias = self.batch["bias"].master

        # Prepare masterdark
        if "dark" in self.batch.keys():
            print("Preparing dark master frame")
            if self.masterbias:
                for i in self.batch["dark"].frames:
                    self.batch["dark"].frames[i].fphase = "orig"
                    self.batch["dark"].frames[i].calibrate(self.stackerwrap(), bias=self.masterbias)
            self.batch["dark"].stack(self.stackerwrap())
            self.masterdark = self.batch["dark"].master

        # Prepare masterflat
        if "flat" in self.batch.keys():
            print("Preparing flat master frame")
            if self.masterbias or self.masterdark:
                for i in self.batch["flat"].frames:
                    self.batch["flat"].frames[i].fphase = "orig"
                    self.batch["flat"].frames[i].calibrate(self.stackerwrap(),
                                                           bias=self.masterbias,
                                                           dark=self.masterdark)
            self.batch["flat"].stack(self.stackerwrap())
            self.masterflat = self.batch["flat"].master

    def settings(self):
        """
        Show all configurable settings
        """

        for i in ("debayer", "matcher", "transformer", "stack"):
            if i == "debayer":
                options = Debayer.__all__
            elif i == "matcher":
                options = Registering.matcher
            elif i == "transformer":
                options = Registering.transformer
            elif i == "stack":
                options = Stacker.__all__
            print("\nOptions for the setting \"" + i + "\" are:\n")
            n = 0
            for j in options:
                n += 1
                print(str(n) + ".  " + j)
            print("\nActive choice is " + self.project.get("Default", i))

    def listframes(self):
        """
        List all frames in project
        :return:
        """

        for i in self.batch["light"].frames:
            print(i + ": " + self.batch["light"].frames[i].rawpath)

    def size(self):
        """
        Print the size of all files in project
        """

        size = 0
        for i in self.project.filelist():
            size += os.path.getsize(i)
        divisions = 0
        while size >= 1.0:
            divisions += 1
            size /= 1024
            if divisions == 3:
                break

        if divisions == 0:
            unit = "B"
        elif divisions == 1:
            unit = "kiB"
        elif divisions == 2:
            unit = "MiB"
        elif divisions == 3:
            unit = "GiB"

        print("Size of all the files on project is {0:.2f} {1}.".format(size, unit))

    def set(self, setting, options, value):
        """
        Save settings with command line mosstack set operation

        Arguments:
        setting - setting to alter
        options - list of options for the setting
        value   - int or name of value to set
        """

        if value.isdigit():
            number = int(value) - 1
            value = options[number]
        else:
            if value in options:
                number = options.index(value)
            else:
                print("Value " + value + " not recognized.")
                exit()

        if number <= len(options):
            # print("Setting \"" + setting + "\" changed to value \"" + value + "\"")
            self.project.set("Default", setting, value)
            print("Setting " + setting + " set to " + value)
            # self.project.write()
        else:
            print("Invalid value")

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
