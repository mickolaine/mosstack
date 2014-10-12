"""
Classes related to user interface. Main program "AstroStack.py" parses the input (at least for now), but
this file controls all the actions after that.
"""

from . import Config
from . Batch import Batch
from . import Registering
from . import Debayer
from . import Stacker
import os


class UserInterface:
    """
    Command line user interface for pyAstroStack. The script AstroStack parses the arguments
    but this class holds all the functionality
    """

    setup = Config.Setup()

    shorthelp = """
    Mikko's Open Source Stacker is run with:
    mosstack <operation> <arguments>

    <operation>   - init, dir, file, ... Try mosstack help for full list
    <arguments>   - Depends on <operation>

    Gui is started with:
    mosstackgui
    """
    """
    String to print when program run with no parameters or false parameters.
    """

    longhelp = """
Using Mikko's Open Source Stacker
=========

The program does nothing automatically. It's designed by the process
calibrate -> debayer -> align -> stack and user has to call each of these
individually. User can also skip any of these steps, if for example no
debayering is required or images are already aligned.

UI is a command line one. User calls mosstack with proper arguments and the
program does that step. Most commands work with pattern

    ``astrostack <operation> <arguments>``

where <operation> and <arguments> are something from following list.

<operation> | <arguments>
-------------------------
help        |
init        | <project name>
set         | <setting> <option>
dir         | <path to dir> <image type>
file        | <path to file> <image type>
master      | <path to file> <image type>
debayer     | <generic name>
register    | <generic name>
stack       | <generic name>
subtract    | <generic name> <master>
divide      | <generic name> <master>


Full documentation of operations
=========

help
------------
No arguments. Prints full help string which is about the same than this
portion of documentation.

init
------------
Initializes a new project. Project has to be initialized before anything else.
Mosstack uses the project file to store information about the photo frames
and development of the process. Project file will have an extension
``project``, but as an argument init takes only project name without extension.

Example:

    ``astrostack init Andromeda``

This will initialize a new project called Andromeda. Most files will be named
after this name. If the project already exists, program will inform and ask
how to proceed.

Initialization also sets the project active. Active project name is stored in
$HOME/.config/mosstack/settings.

set project
------------
Set the specified project name as the active project. Active project name is
stored in $HOME/.config/mosstack/settings.

Example:

    ``mosstack set project Andromeda``

Activating the project means all the commands will be run using information of
that project file. User can have many simultaneous projects in his working
directory.

dir
------------
Add all supported raw photos in specified directory into active project. In
addition to path this also requires type of the frames as an argument.
Program understands the types light, bias, dark and flat. Easiest way to add
files in the project is to separate these types to their own directories.

Example:

    ``mosstack dir /media/data/Astro/2013-11-25/Andromeda/ light``
    ``mosstack dir /media/data/Astro/2013-11-25/flat/ flat``

file
------------
Add specified raw photo into active project. In addition to file path this also
requires type of the frame as an argument. Program understands the types light,
bias, dark and flat.

Example:

    ``mosstack file /media/data/Astro/2013-11-25/Andromeda/IMG_5423.CR2``

master
------------
Add a finished master frame for bias, dark or flat. Accepts FITS or TIFF files.
This is a nice feature if you do several images with the same data.

Example:

    ``mosstack master /media/data/astrostack/Andro_bias_master_orig.fits bias``

subtract
------------
Subtract master frame from specified batch of images pixel by pixel. A master
frame of some kind is required for this operation. Master means a stacked
frame.

Usage:

    ``mosstack subtract <batch> <master>``

Example:

    ``mosstack subtract light dark``

This example takes all frames identified by light and subtracts master dark
from them one by one. After operation there are images identified by name
"calib" in the work directory. Note that if you subtract or divide batch named
calib, the images will be overwritten.

divide
------------
Divide a batch of frames by a specified master frame pixel by pixel. A master
frame is required for this operation. Master means a stacked frame.

Usage:

    ``mosstack divide <batch> <master>``

Example:

    ``mosstack divide light flat``

This example takes all frames identified by light and divides them by master
dark from them one by one. After operation there are images identified by name
"calib" in the work directory. Note that if you subtract or divide batch named
calib, the images will be overwritten.

Debayer
------------
Debayer CFA-images into RGB. At this moment program supports only images taken
with Canon 1100D or a camera with similar Bayer matrix. Output files will be
separate files and identified by "rgb" followed by one letter to tell the
channel.

Usage:

    ``mosstack debayer <batch>``

Example:

    ``mosstack debayer calib``

register
------------
Register (locate and match stars, calculate and perform affine transformation)
the frames. All registering will be done against a specified reference frame.
Output files will be identified with "reg".

Usage:

    ``mosstack register <batch>``

Example:

    ``mosstack register rgb``

stack
------------
Stack frames in specified batch. At the moment the stacking will consume a lot
of memory. This will be fixed in later versions of the software. Output files
will be identified either with "master" (if batch name is bias, dark or flat)
or "final" (if batch name is anything else).

Usage:

    ``mosstack stack <batch>``

Example:

    ``mosstack stack bias``
    ``mosstack stack reg``

list
------------
List available settings and their options. Prelude to full ui. These can also
be manually edited in the project file.

Usage

    ``mosstack list <setting>``

Examples:

List of settings to adjust
    ``mosstack list``

List of options for setting
    ``mosstack list debayer``

set
------------
Set can also be used to adjust settings. See operation 'list' to see them

Usage

    ``mosstack set <setting> <option>``

Examples:

    ``mosstack set debayer Bilinear``
    ``mosstack set debayer 2``

You can use either name or number as operation 'list' shows them.

    """

    """
    String to print when program is run with 'help' parameter. Includes short explanations on every
    command line argument available.

    """

    def __init__(self):
        """
        Initialize user interface and set project name if specified
        """
        self.project = None

        # Set default values.
        self.debayerwrap = Debayer.VNGCython
        self.matcher = Registering.Groth
        self.transformer = Registering.SkTransform
        self.stackerwrap = Stacker.SigmaMedian

    def start(self, argv):
        """
        Parse arguments and run functions according
        """

        if len(argv) == 0:
            print(self.shorthelp)
            exit()

        if argv[0] == "help":
            print(self.longhelp)
            exit()

        if argv[0] == "init":
            try:
                project = Config.Project()
                project.initproject(argv[1])
                Config.Global.set("Default", "Project", argv[1])
                print("New project started: \n" + Config.Global.get("Default", "Path") + "/" + argv[1] + ".project")
                exit()
            except IndexError:
                print("Project name not specified. Try \"mosstack help\" and see what went wrong.")
                exit()

        try:
            pname = Config.Global.get("Default", "Project")
            ppath = Config.Global.get("Default", "Path") + "/" + pname + ".project"
            if argv[0] == "set" and argv[1] == "project":
                pass
            else:
                print("Current project is " + ppath + "\n")
            project = Config.Project(pname)
            project.readproject()
            self.setproject(project)

        except IndexError:
            print("Something went wrong. Check your input. Refer to \"mosstack help\" if needed.")
            exit()

        if argv[0] == "set":

            if argv[1] == "project":
                if argv[2]:
                    pname = argv[2]
                    Config.Global.set("Default", "Project", pname)
                    ppath = Config.Global.get("Default", "Path") + pname + ".project"
                    self.setproject(Config.Project(pname))
                    print("Project set to " + ppath)
                else:
                    print("No project name specified.")
                    print("Try mosstack set project <project name>, without path or extension.")

            elif argv[1] == "debayer":
                options = Debayer.__all__
                self.set("Debayer", options, argv[2])
            elif argv[1] == "matcher":
                options = Registering.matcher
                self.set("Matcher", options, argv[2])
            elif argv[1] == "transformer":
                options = Registering.transformer
                self.set("Transformer", options, argv[2])
            elif argv[1] == "stack":
                options = Stacker.__all__
                self.set("Stack", options, argv[2])
            elif argv[1] == "kappa":
                self.project.set("Default", "Kappa", argv[2])

            else:
                print("Don't know how to set " + argv[1])
                print("Possible options to set are \n project\n debayer\n matcher\n transformer\n stack")

        elif argv[0] == "list":

            if len(argv) == 1:
                print("Settings to list are \n debayer\n matcher\n transformer\n stack")
            else:
                if argv[1] == "debayer":
                    options = Debayer.__all__
                elif argv[1] == "matcher":
                    options = Registering.matcher
                elif argv[1] == "transformer":
                    options = Registering.transformer
                elif argv[1] == "stack":
                    options = Stacker.__all__
                else:
                    print("No such setting " + argv[1])
                    print("Possible settings are \n debayer\n matcher\n transformer\n stack")
                    exit()
                self.list(argv[1], options)

        elif argv[0] == "dir":

            if argv[1]:
                try:
                    directory = UserInterface.absolutepath(argv[1], directory=True)
                except IOError:
                    print("Directory " + argv[1] + " not found. Check your input")
                    exit()
            else:
                directory = UserInterface.absolutepath(os.getcwd(), directory=True)

            itype = argv[2]
            self.adddir(directory, itype)

        elif argv[0] == "file":

            try:
                path = UserInterface.absolutepath(argv[1])
                itype = argv[2]
                self.addfile(path, itype)
            except IOError:
                print("File " + argv[1] + " not found. Check your input")
                exit()

        elif argv[0] == "master":

            try:
                path = UserInterface.absolutepath(argv[1])
            except IOError:
                print("File " + argv[1] + " not found. Check your input")
                exit()
            if argv[2] in ("flat", "dark", "bias"):
                ftype = argv[2]
                self.addmaster(path, ftype)
            else:
                print("Master frame has to be either flat, dark or bias")
                print("Try again:")
                print("          mosstack master <path to file> <flat, dark or bias>")
                exit()

        elif argv[0] == "biaslevel":

            try:
                level = float(argv[2])
            except IndexError:
                print("Biaslevel not defined. Try mosstack biaslevel <ftype> <level>")
            except ValueError:
                print("Value " + argv[2] + " not understood. Try an integer or a decimal number eg. 21 or 30.2")

            self.biaslevel(argv[1], level)

        elif argv[0] == "stack":
            # AstroStack stack <srcname>
            srclist = ("light", "dark", "bias", "flat", "rgb", "calib", "reg", "crop")
            if argv[1] in srclist:
                section = argv[1]
                self.stack(section)
            else:
                print("Invalid argument: " + argv[1])
                print("<itype> has to be one of: " + str(srclist))

        elif argv[0] == "debayer":
            # AstroStack debayer <srcname>

            if argv[1]:
                fphase = argv[1]
                self.debayer(fphase)

            else:
                print("Scrname not defined. Try 'mosstack debayer calib' or 'mosstack debayer light'\nExiting...")
                exit()

        elif argv[0] == "register":
            # AstroStack register <srcname>

            if argv[1]:
                fphase = argv[1]
                self.register(fphase)
            else:
                print("Srcname not defined. Exiting...")
                exit()

        elif argv[0] == "subtract":
            # AstroStack subtract <srcname> <calibname>

            if argv[1]:
                section = argv[1]
                if argv[2]:
                    calib = argv[2]
                    self.subtract(section, calib)
                else:
                    print("Calibname not defined. Exiting...")
                    exit()
            else:
                print("Srcname not defined. Exiting...")
                exit()

        elif argv[0] == "divide":
            # AstroStack divide <srcname> <calibname>

            if argv[1]:
                section = argv[1]
                if argv[2]:
                    calib = argv[2]
                    self.divide(section, calib)
                else:
                    print("Calibname not defined. Exiting...")
                    exit()
            else:
                print("Srcname not defined. Exiting...")
                exit()

        elif argv[0] == "crop":

            if len(argv) == 6:
                try:
                    xrange = int(argv[2]), int(argv[3])
                    yrange = int(argv[4]), int(argv[5])
                except ValueError:
                    print("Values " + argv[2] + ", " + argv[3] + ", " + argv[4] +
                          " and " + argv[5] + " should be integers.")

                self.crop(argv[1], xrange, yrange)

            else:
                print("Invalid input. Please refer to mosstack help.")

        elif argv[0] == "frames":

            if len(argv) == 2:
                self.listframes(argv[1])
            else:
                print("Invalid input. Try mosstack frames <frame type>")
                exit()

        elif argv[0] == "remove":

            if len(argv) == 3:
                self.remove(argv[1], argv[2])
            else:
                print("Invalid input. Try mosstack remove <frame type> <frame id>")
                exit()

        elif argv[0] == "reference":

            if len(argv) == 2:
                try:
                    self.setRef(argv[1])
                    print("Reference frame changed to " + argv[1])
                except KeyError:
                    print("Frame id " + argv[1] + " not found.")
            else:
                print("Invalid input. Try mosstack reference <frame id>")

        elif argv[0] == "size":

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

        elif argv[0] == "clean":
            print("Cleaning up project files.")
            for i in self.project.filelist(temp=True):
                if os.path.isfile(i):
                    os.remove(i)

            print("Files:")

            for i in self.project.filelist():
                print(i)

            print("are not removed. They must be removed manually.")

        else:
            print("Invalid operation: " + argv[0])
            print(self.shorthelp)
            exit()

    @staticmethod
    def absolutepath(path, directory=False):
        """
        Check if path is relative and if so, return absolute path.

        Raise IOError if path does not exist.
        """

        if directory:
            check = os.path.isdir
        else:
            check = os.path.isfile

        if check(path):
            return path

        if check(os.path.join(os.getcwd(), path)):
            return os.path.join(os.getcwd(), path)

        else:
            raise IOError()

    def setproject(self, project):
        """
        Set project name
        """
        self.project = project
        if project.get("Default", "debayer") not in Debayer.__all__ or \
           project.get("Default", "matcher") not in Registering.matcher or \
           project.get("Default", "transformer") not in Registering.transformer or \
           project.get("Default", "stack") not in Stacker.__all__:
            print("Invalid entries in project file. Using default")
            return

        try:
            self.debayerwrap = eval("Debayer." + project.get("Default", "Debayer"))
        except ImportError:
            print("Looks like OpenCL isn't working. Refer to manual.")
            print("Setting debayer algorithm to pure Python module (slow but working).")
            self.debayerwrap = Debayer.VNGCython
        self.matcher = eval("Registering." + project.get("Default", "matcher") + "()")
        self.transformer = eval("Registering." + project.get("Default", "transformer") + "()")
        self.stackerwrap = eval("Stacker." + project.get("Default", "stack"))

    def register(self, fphase):
        """
        Register project files under specified section.
        """

        batch = Batch(self.project, ftype="light", fphase=fphase)

        self.matcher.tform = self.transformer

        # Reference frame first
        batch.frames[batch.refId].register(self.matcher)

        for i in batch.frames:
            if i == batch.refId:
                continue
            batch.frames[i].register(self.matcher)

    def debayer(self, fphase):
        """
        Debayer project files under specified section.
        """

        # Create new batch with ftype hardcoded. No need to debayer other than light
        batch = Batch(self.project, ftype="light", fphase=fphase)

        for i in batch.frames:
            batch.frames[i].debayer(self.debayerwrap())
        #batch.debayerAll(self.debayerwrap())

    def stack(self, genname):
        """
        Stack project files under specified section.
        """

        if genname in ("bias", "dark", "flat"):
            batch = Batch(self.project, ftype=genname)
        else:
            batch = Batch(self.project, fphase=genname)

        if self.project.get("Default", "Stack") == "SigmaMedian" or self.project.get("Default", "Stack") == "SigmaClip":
            batch.stack(self.stackerwrap(kappa=int(self.project.get("Default", "Kappa"))))
        else:
            batch.stack(self.stackerwrap())

        if genname == "reg":
            print("\nProject finished. Remove temporary files with mosstack clean if needed.")

    def subtract(self, genname, calib):
        """
        Subtract calibration frame from main frame or frames.

        Arguments:
        genname - section code or name for frames (light, dark, flat, bias)
        calib - name for master frame (dark, bias)
        """

        if genname == "calib":
            batch = Batch(self.project, ftype="light", fphase="calib")
        else:
            batch = Batch(self.project, ftype=genname)
        batch.subtract(calib, self.stackerwrap())

    def biaslevel(self, ftype, level):
        """
        Subtract given biaslevel from frames
        """

        batch = Batch(self.project, ftype=ftype)

        for i in batch.frames:
            batch.frames[i].calibrate(self.stackerwrap(), biaslevel=level)

    def divide(self, genname, calib):
        """
        Divide main frame with calibration frame.

        Arguments:
        genname - section code or name for frames (light, dark, flat, bias)
        calib - name for master frame (most likely flat)
        """

        if genname == "calib":
            batch = Batch(self.project, ftype="light", fphase="calib")
        else:
            batch = Batch(self.project, ftype=genname)
        batch.divide(calib, self.stackerwrap())

    def list(self, setting, options):
        """
        List current and available options of the setting
        """

        value = self.project.get("Default", setting)

        print("Options for the setting \"" + setting + "\" are:\n")
        n = 0
        for i in options:
            n += 1
            print(str(n) + ".  " + i)
        print("\nCurrent setting is \"" + value + "\".")

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
            #print("Setting \"" + setting + "\" changed to value \"" + value + "\"")
            self.project.set("Default", setting, value)
            print("Setting " + setting + " set to " + value)
            #self.project.write()
        else:
            print("Invalid value")

    def adddir(self, directory, ftype):
        """
        Add files in directory to project

        Arguments:
        directory - unix path to add
        ftype - light, flat, bias, dark
        """

        batch = Batch(project=self.project, ftype=ftype)
        batch.directory(directory, ftype)

    def addfile(self, path, ftype):
        """
        Add a single file to project

        Arguments:
        path - unix path to file
        ftype - light, flat, bias, dark
        """

        batch = Batch(project=self.project, ftype=ftype)
        batch.addfile(path, ftype)

    def addmaster(self, path, ftype):
        """
        Add a ready master frame to project

        Arguments:
        path - unix path to file
        ftype - flat, bias or dark
        """

        batch = Batch(project=self.project, ftype=ftype)
        batch.addmaster(path, ftype)

    def crop(self, fphase, xrange, yrange):
        """
        Crop frames according to given coordinates.
        """

        batch = Batch(project=self.project, ftype="light", fphase=fphase)

        for i in batch.frames:
            batch.frames[i].crop(xrange, yrange)

    def listframes(self, ftype):
        """
        List frames by ftype.
        """

        batch = Batch(project=self.project, ftype=ftype)
        for i in batch.frames:
            print(i + ": " + batch.frames[i].rawpath)

    def remove(self, ftype, frameId):
        """
        Remove frame from project
        """

        batch = Batch(project=self.project, ftype=ftype)
        batch.removeFrame(frameId)

    def setRef(self, frameId):
        """
        Set the reference frame. Possible only for light frames since there's no sense changing reference from other
        """

        batch = Batch(project=self.project, ftype="light")
        try:
            batch.setRef(frameId)
        except KeyError:
            raise