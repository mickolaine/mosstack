"""
Classes related to user interface. Main program "AstroStack.py" parses the input (at least for now), but
this file controls all the actions after that.
"""

from . import Conf
from . Photo import Photo, Batch
from . import Registering
from . import Demosaic
from . import Stacker

__author__ = 'Mikko Laine'


class UserInterface:
    """
    Command line user interface for pyAstroStack. The script AstroStack.py parses the arguments
    but this class holds all the functionality
    """

    setup = Conf.Setup()

    shorthelp = """
    pyAstroStack is run with:
    AstroStack.py <operation> <arguments>

    <operation>   - init, adddir, addfile, ... Try AstroStack help for full list
    <arguments>   - Depends on <operation>
    """
    """
    String to print when program run with no parameters or false parameters.
    """

    longhelp = """
Using pyAstroStack
=========

The program does nothing automatically. It's designed by the process
calibrate -> demosaic -> align -> stack and user has to call each of these
individually. User can also skip any of these steps, if for example no
demosaicing is required or images are already aligned.

UI is a command line one. User calls AstroStack with proper arguments and the
program does that step. Most commands work with pattern

    ``AstroStack <operation> <arguments>``

where <operation> and <arguments> are something from following list.

<operation> | <arguments>
-------------------------
help        |
init        | <project name>
set         | <project name>
adddir      | <path to dir> <image type>
addfile     | <path to file> <image type>
demosaic    | <generic name>
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
AstroStack uses the project file to store information about the photo frames
and development of the process. Project file will have an extension
``project``, but as an argument init takes only project name without extension.

Example:

    ``AstroStack init Andromeda``

This will initialize a new project called Andromeda. Most files will be named
after this name. If the project already exists, program will inform and ask
how to proceed.

Initialization also sets the project active. Active project name is stored in
$HOME/.config/pyAstroStack/settings.

set
------------
Set the specified project name as the active project. Active project name is
stored in $HOME/.config/pyAstroStack/settings.

Example:

    ``AstroStack set Andromeda``

Activating the project means all the commands will be run using information of
that project file. User can have many simultaneous projects in his working
directory.

adddir
------------
Add all supported raw photos in specified directory into active project. In
addition to path this also requires type of the frames as an argument.
Program understands the types light, bias, dark and flat. Easiest way to add
files in the project is to separate these types to their own directories.

Example:

    ``AstroStack adddir /media/data/Astro/2013-11-25/Andromeda/ light``
    ``AstroStack adddir /media/data/Astro/2013-11-25/flat/ flat``

addfile
------------
Add specified raw photo into active project. In addition to file path this also
requires type of the frame as an argument. Program understands the types light,
bias, dark and flat.

Example:

    ``AstroStack addfile /media/data/Astro/2013-11-25/Andromeda/IMG_5423.CR2``

subtract
------------
Subtract master frame from specified batch of images pixel by pixel. A master
frame of some kind is required for this operation. Master means a stacked
frame.

Usage:

    ``AstroStack subtract <batch> <master>``

Example:

    ``AstroStack subtract light dark``

This example takes all frames identified by light and subtracts master dark
from them one by one. After operation there are images identified by name
"calib" in the work directory. Note that if you subtract or divide batch named
calib, the images will be overwritten.

divide
------------
Divide a batch of frames by a specified master frame pixel by pixel. A master
frame is required for this operation. Master means a stacked frame.

Usage:

    ``AstroStack divide <batch> <master>``

Example:

    ``AstroStack divide light flat``

This example takes all frames identified by light and divides them by master
dark from them one by one. After operation there are images identified by name
"calib" in the work directory. Note that if you subtract or divide batch named
calib, the images will be overwritten.

demosaic
------------
Demosaic CFA-images into RGB. At this moment program supports only images taken
with Canon 1100D or a camera with similar Bayer matrix. Output files will be
separate files and identified by "rgb" followed by one letter to tell the
channel.

Usage:

    ``AstroStack demosaic <batch>``

Example:

    ``AstroStack demosaic calib``

register
------------
Register (locate and match stars, calculate and perform affine transformation)
the frames. All registering will be done against a specified reference frame.
Output files will be identified with "reg".

Usage:

    ``AstroStack register <batch>``

Example:

    ``AstroStack register rgb``

stack
------------
Stack frames in specified batch. At the moment the stacking will consume a lot
of memory. This will be fixed in later versions of the software. Output files
will be identified either with "master" (if batch name is bias, dark or flat)
or "final" (if batch name is anything else).

Usage:

    ``AstroStack stack <batch>``

Example:

    ``AstroStack stack bias``
    ``AstroStack stack reg``
    """

    """
    String to print when program run with 'help' parameter. Will include short explanations on every
    command line argument available.

    For now is just a copy of shorthelp.
    """

    def __init__(self, project=None):
        """
        Initialize user interface and set project name if specified
        """
        self.project = project

    def setproject(self, project):
        """
        Set project name
        """
        self.project = project

    def register(self, section):
        """
        Register project files under specified section.
        """

        batch = Batch(section=section, project=self.project, load=False)
        batch.register(Registering.Sextractor2())

    def demosaic(self, section):
        """
        Demosaic project files under specified section. Use demosaicing algorithm TODO:
        """

        batch = Batch(section=section, project=self.project, load=False)
        batch.demosaic(Demosaic.VNG())

    def stack(self, section):
        """
        Stack project files under specified section. Stacker read from TODO: do this
        """

        batch = Batch(section=section, project=self.project, load=False)
        batch.stack(Stacker.Median())

    def subtract(self, section, calib):
        """
        Subtract calibration frame from main frame or frames.

        Arguments:
        section - section code or name for master frame (light, dark, flat, bias)
        calib - name for master frame (dark, bias)
        """

        batch = Batch(section=section, project=self.project, load=False)
        batch.subtract(calib, Stacker.Mean())

    def divide(self, section, calib):
        """
        Divide main frame with calibration frame.

        Arguments:
        section - section code or name for master frame
        calib - name for master frame (most likely flat)
        """

        batch = Batch(section=section, project=self.project, load=False)
        batch.divide(calib, Stacker.Mean())