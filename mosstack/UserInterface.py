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

    ``mosstack <operation> <arguments>``

where <operation> and <arguments> are something from following list.

  help        print help
  ----------- -------------------------------------
  init        initialize a new project
  list        list settings
  set         change settings
  dir         add whole directory of images
  file        add a single image
  frames      list frames
  remove      remove frame
  reference   change reference frame
  debayer     debayer frames
  register    register frames
  crop        crop frames
  stack       stack frames
  subtract    subtract image from a set
  divide      divide set by an image
  biaslevel   subtract constant int from a set
  master      add master frame
  size        show projects size on disc
  clean       remove temporary files from project


Full documentation of operations
=========

### help

Print the long help. Long help is mostly the section [cli] from this
manual. My plan is to make it generate straight from this LaTeXdocument.

How to run:

     mosstack help

### init

Initialize the project. Mosstack always does everything for the active
project and this command is used to create one.

For example

     mosstack init Andromeda

creates a new .project file in mosstack’s working directory. This file
holds information about progress of the project as well as locations to
all the files project uses.

Each diffrerent data set should be a separate project. One project can
be used to stack the same data in different ways, for example a maximum
stack to find satellite trails and a sigma median stack to do the ”real”
final image. A project leaves all the temporary files behind so changing
settings and continuing on any point of the process should be possible.

Since all the temporary data is left behind, in the end user should
clean that with command `clean` [clean].

### list

List settings. Running just

     mosstack list

gives a list of possible settings. At the moment there are four
settings:

-   debayer - How to debayer CFA images (see Sections [debayering] and
    [debayeringmath])

-   matcher - How to find matching stars on different photos (see
    Sections [registering] and [registeringmath])

-   transformer - How to perform affine transformations.

-   stack - How to calculate image stacks (see Sections [stacking] and
    [stackingmath])

Running

     mosstack list <setting>

for example

     mosstack list debayer

gives a list of different debayering algorithms available. The current
setting is also printed.

### set

Change settings or the active project.

Command

     mosstack set project <project name>

changes active project to given name. Project has to be initiated and
the .project file has to be in working directory. The option
`<project name>` is given without path or suffix, exactly the same way
it was written to command `init`. There’s no other way to see available
projects than to `ls *.project` in mosstack’s working directory.

Settings are changed with options seen with command `list` as described
in section [list]. First see what options there are available with

     mosstack list <setting>

and change them with

     mosstack set <setting> <option>

For example

     mosstack list debayer

prints out

    Options for the setting "debayer" are:

    1.  BilinearOpenCl
    2.  VNGOpenCl
    3.  BilinearCython
    4.  VNGCython

    Current setting is "VNGCython".

Now the setting can be change with either one of

     mosstack set debayer VNGOpenCl
     mosstack set debayer 2

The text has to be written exactly as in the example, so number might be
a better choice. Although for scripting the text is better choice since
it’s not guaranteed that the options are always in the same order. They
should be, but there’s nothing to check that.

### dir

Add whole directory of files to the project. Command works by listing
contents of a Unix path, absolute or relative, and checking each file
with `dcraw -i`. If file is recognized as a DSLR Raw photo, it is added
to project. Frame type (light, bias, dark or flat) must also be defined.

Example

     mosstack dir /path/to/photos/2014-10-22/Andromeda light

adds all files in path */path/to/photos/2014-10-22/Andromeda* to project
as light frames. Path can also be a relative path:

     mosstack dir 2014-10-22/Bias bias

Be sure not to give wild cards \* in your path since this is not ”add
multiple files” but ”add directory”.

### file

Add a file to active project. Does not support wild cards (0.6, maybe
later will) so each file must be added one at a time. Like this:

     mosstack file /path/.../2014-10-22/Andro/IMG_5423.cr2 light

As with `dir` command, the path can be either relative or absolute and
command must end with frame type (light, dark, bias, flat).

The file will be tested with `dcraw -i` and if DCRaw can decode it, it
will be added to project.

### frames

List all the frames of given type. This is required for commands
`remove` and `reference`.

Command is run with:

     mosstack frames <ftype>

where `<ftype>` is frame type to list.

Example: List all the light frames:

     mosstack frames light

### remove

Remove frame from the project. Use command `frames` to list frames and
see their identifying numbers.

Command is run with:

     mosstack remove <ftype> <number>

where `<ftype>` is frame type and `<number>` the identifying number for
the frame.

Example: Check light frames and remove number 12.

     mosstack frames light
     mosstack remove light 12

### reference

Change the reference frame. When adding frames the first one is always
selected the reference frame. This means all the other frames are
matched to its stars and aligned as such.

Command is run with:

     mosstack reference <number>

where `<number>` is identifying number for the frame. Check with command
`frames`. The frame type is not defined since setting reference frame is
sensible only for light frames. This will operate on light only.

### debayer {#debayering}

Batch of frames will be debayered. Debayering process is explained in
Section [debayeringmath].

Command is run with

     mosstack debayer <fphase>

where `<phase>` is identifier for the batch.

Example: Run debayer for light frames

     mosstack debayer light

Example: Run debayer for calibrated light frames saved with identifier
*calib*

     mosstack debayer calib

Debayer will save batch with identifier *rgb*.

There are two different language for debayering algorithms. These
operations are quite processor intensive so pure Python isn’t a good
choice. NumPy itself can’t help either. There are two implementations:
Cython and PyOpenCL.

Cython uses CPU to do the math. There’s no multithreading and the
process takes about 10 seconds for a 12Mpix data on AMD FX-6300. This
uses only one core so multithreading could be possible. It’s just not
implemented yet on CLI.

PyOpenCL uses GPU for the math. This is *fast*. It takes about 0.2
seconds to debayer a frame. Except that there is a 5 second overhead for
manipulating the NumPy array to right alignment, transferring the data
to GPU and back. It might be possible to manipulate the data on GPU and
take some overhead off, but this is the situation at version 0.6.
Nevertheless it’s faster than same with Cython.

Support for OpenCL doesn’t work out of the box with Ubuntu. With Gentoo
it works reasonably well with programs from official distribution, but
with Ubuntu 14.04 requires 3rd party packages.

Multithreading does not work at all with PyOpenCL. Not even in GUI.
Seems like it’s just not possible. It might be possible to multithread
all the overhead stuff and just queue math itself, but there’s no plans
for that yet.

### register {#registering}

Batch of frames will be registered. This means aligning them for
stacking. All of the current registering methods work the same:

-   find stars

-   match stars

-   calculate affine transformation

-   do the affine transformation

Further information about registering process is explained in Section
[registeringmath].

Command is run with

     mosstack register <fphase>

where `<fphase>` is identifier for the batch.

Example: Run register for calibrated and debayered light frames saved
with identifier *rgb*

     mosstack register rgb

Register will save the batch with identifier *reg*.

Currently there’s no choice on the algorithms.

### crop {#cropping}

Batch of registered images will be cropped by given XY-range.
Coordinates are given as pixels from upper left corner. I recommend
doing all the croppings with the graphical user interface.

Command is run with:

     mosstack crop <fphase> x0, x1, y0, y1

where x0, x1, y0 and y1 are coordinates limiting a rectangular area and
`<fphase>` identifier for frames to crop. Mostly this is *reg* since
only aligned images are good for cropping.

Example: Crop a rectangle limited by corners (300, 200) and (1800, 1300)

     mosstack crop reg 300 1800 200 1300

Images are saved with identifier *crop*

### stack {#stacking}

Batch of frames will be stacked with the selected stacking algorithm.
Note that the batch should be aligned before this.

Command is run with

     mosstack stack <ftype> <fphase>

where `<ftype>` is frame type for the batch and `<fphase>` the phase of
process, for example `calib` or `reg`.

Example: Run stack for registered frames saved with identifier *reg*

     mosstack stack light reg

The result image will be saved with identifier *master*. Full name of
the resulting files are printed after successful stacking.

Note that stacking algorithm can be changed during project. If you want
to stack calibration frames with average value and light frames with eg.
sigma median, just use `set` to change stacker before running stack. See
tutorial [tutorial] for examples.

### subtract

Subrtact frame from all the frames in batch. This is used with bias and
dark frame calibration.

Command is run with:

     mosstack subtract <batch> <calib>

where `<batch>` is identifier for batch to subtract from and `<calib>`
identifier for master calibration frame. Note that the requested master
must exist, or the command will fail.

Example: Subtract master bias from dark frames.

     mosstack subtract dark bias

Resulting light images will be saved with identifier *calib*. Calibrated
dark and flat will be overwritten with the same name.

Example: Stack bias frames, calibrate and stack dark frames and
calibrate light frames.

     mosstack stack bias orig
     mosstack subtract dark bias
     mosstack stack dark calib
     mosstack subtract light bias
     mosstack subtract calib dark

Note that first time you subtract from light frames the identifier is
*light* but after that it’s *calib*. Operating on *light* always takes
the original files. Use this if you want to undo subtractions.

### divide

Divide frame from all the frames in batch. This is used with flat frame
calibration.

Command is run with:

     mosstack divide <batch> <calib>

where `<batch>` is identifier for batch to subtract from and `<calib>`
identifier for master calibration frame. There really is no reason to do
anything but dividing light (identifier *light* or *calib*) with master
flat frame.

Example: Divide calibrated light frames with master flat frame.

     mosstack divide calib flat

Result will be saved with identifier *calib*.

### biaslevel

Set *bias level* for batch. This works like bias frame calibration, but
subtracts a constant value from all the pixels.

Command is run with:

     mosstack bias <batch> <value>

where `<batch>` is identifier for the batch and `<value>` is the value
to subtract from pixels.

Example: Subtract bias level 21 from light frames.

     mosstack bias light 21

The resulting batch will be saved with identifier *calib*, just like if
they were calibrated with bias frame.

### master

Add a pre-existing master frame to the project. With this you don’t need
to remake the calibration frames for all projects from same photo
session.

Command is run with:

     mosstack master <path> <type>

where `<path>` is a Unix path to file and `<type>` is type of the
calibration frame (*dark*, *flat* or *bias*).

Example: Add master flat frame to the project.

     mosstack master /path/to/saved/flat_2014-10-20.fits flat

Formats Fits and Tiff are supported.

### size

Tell the size of all the files in project. Mosstack creates a lot of
temporary files required only for the next step in processing. Depending
on the number and size of source files, a project can easily take
several gigabytes of space.

Command is run with:

     mosstack size

That’s it. It prints out the size in the most convinient unit. Most
likely that will be GiB, but for small projects maybe MiB.

### clean

Remove all the temporary files. This is a useful command to run after
the project is done. `Clean` removes all the temprary files leaving only
ones labeled *master* and the project file. Everything can be easily run
again without adding all the files.

Command is run with:

     mosstack clean

### fixsex

If you manage to delete SExtractor configuration files from mosstack's
temporary directory, you can fix it by:

    mosstack fixsex


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

        elif argv[0] == "files":

            itype = argv[-1]
            if len(argv[1:-1]) == 0:
                print ("No files given?")
                exit()
            for p in argv[1:-1]:
                try:
                    path = UserInterface.absolutepath(p)
                    self.addfile(path, itype)
                except IOError:
                    print("File " + p + " not found. Check your input")
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
            # AstroStack stack <frame type> <frame phase>
            typelist = ("light", "dark", "bias", "flat")
            phaselist = ("orig", "rgb", "calib", "reg", "crop")
            if (argv[1] in typelist) and (argv[2] in phaselist):
                self.stack(argv[1], argv[2])
            else:
                print("Invalid argument")
                print("<frame type> has to be one of: " + str(typelist))
                print("<frame phase> has to be one of: " + str(phaselist))

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

        elif argv[0] == "fixsex":

            print("Rewriting SExtractor configuration files.")
            Config.Setup.createSExConf()

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

    def stack(self, ftype, fphase):
        """
        Stack project files under specified section.
        """

        batch = Batch(self.project, ftype=ftype, fphase=fphase)

        if self.project.get("Default", "Stack") == "SigmaMedian" or self.project.get("Default", "Stack") == "SigmaClip":
            batch.stack(self.stackerwrap(kappa=int(self.project.get("Default", "Kappa"))))
        else:
            batch.stack(self.stackerwrap())

        if fphase == "reg":
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
            batch.frames[i].biaslevel = level
            batch.frames[i].calibrate(self.stackerwrap())

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