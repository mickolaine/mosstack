"""
Classes related to user interface. Main program "AstroStack.py" parses the input (at least for now), but
this file controls all the actions after that.
"""

from . import Config
from . Batch import Batch
from . import Registering
from . import Debayer
from . import Stacker
#from sys import version_info

__author__ = 'Mikko Laine'


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

    def __init__(self, project=None):
        """
        Initialize user interface and set project name if specified
        """
        self.project = project

        # Set default values.
        self.debayerwrap = Debayer.VNGCython
        self.registerwrap = Registering.Groth_Skimage
        self.stackerwrap = Stacker.SigmaMedian

    def setproject(self, project):
        """
        Set project name
        """
        self.project = project
        if project.get("Default", "debayer") not in Debayer.__all__ or \
           project.get("Default", "register") not in Registering.__all__ or \
           project.get("Default", "stack") not in Stacker.__all__:
            print("Invalid entries in project file. Using default")
            return

        try:
            self.debayerwrap = eval("Debayer." + project.get("Default", "Debayer"))
        except ImportError:
            print("Looks like OpenCL isn't working. Refer to manual.")
            print("Setting debayer algorithm to pure Python module (slow but working).")
            self.debayerwrap = Debayer.BilinearCython
        self.registerwrap = eval("Registering." + project.get("Default", "register"))
        self.stackerwrap = eval("Stacker." + project.get("Default", "stack"))

    def register(self, fphase):
        """
        Register project files under specified section.
        """

        batch = Batch(self.project, ftype="light", fphase=fphase)
        batch.registerAll(self.registerwrap())

    def debayer(self, fphase):
        """
        Debayer project files under specified section. Use debayering algorithm TODO:
        """

        # Create new batch with ftype hardcoded. No need to debayer other than light
        batch = Batch(self.project, ftype="light", fphase=fphase)
        batch.debayerAll(self.debayerwrap())

    def stack(self, genname):
        """
        Stack project files under specified section. Stacker read from TODO: do this
        """

        if genname in ("bias", "dark", "flat"):
            batch = Batch(self.project, ftype=genname)
        else:
            batch = Batch(self.project, fphase=genname)
        batch.stack(self.stackerwrap())

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
            print("Setting \"" + setting + "\" changed to value \"" + value + "\"")
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