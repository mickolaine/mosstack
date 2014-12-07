===========
Mikko's Open Source Stacker for astronomical images
===========

Mosstack is an open source registering and stacking software for
astronomical images. Original (and current) design is made for photos taken
with DSLR camera. Program is crude and it lacks functionality familiar with
better known freeware stacking software.


Prerequisites
=========

Mosstack relies heavily on other open source programs and libraries. Here's
a complete list:

* Python 3 - <http://www.python.org>

* DCRaw - <http://www.cybercom.net/~dcoffin/dcraw/>

* SExtractor - <http://www.astromatic.net/software/sextractor>
  Installation of this might be tricky if it's not included in your Linux
  distribution. RPM-packages on the link above should work in most cases.
  I even installed this on Gentoo with provided RPM.
  
* ImageMagick - <http://www.imagemagick.org>

* ExifTool - <http://www.sno.phy.queensu.ca/~phil/exiftool/>

* AstroPy - <http://www.astropy.org/>

* NumPy - <http://www.numpy.org/>

* Scikit-image - <http://scikit-image.org/>

* Cython - <http://www.cython.org/>

* PyOpenCL - <http://mathema.tician.de/software/pyopencl> (Not required but supported)

* PyQt4 - <http://qt-project.org>


Features
=========

Ultimate plan is to have functionality similar to DeepSkyStacker or IRIS, but
for now the program is limited to basic functionality.

- CFA to RGB conversion (see below for supported cameras)
    - Bilinear (OpenCL, Cython)
    - Variable Number of Gradients (OpenCL, Cython)

- Registering
    - SExtractor and http://adsabs.harvard.edu/abs/1986AJ.....91.1244G

- Aligning
    - ImageMagick
    - Scikit-image

- Stacking
    - Mean value
    - Median value
    - Sigma Median
    - Sigma Clipping

- A somewhat working GUI
    - PyQt4
    - Multithreading


Supported cameras
------------
Basically everything DCRaw can open, is supported. Then again maybe not.
DCRaw does not debayer the images, only converts them and checks the bayer
matrix. Most modern consumer DSLR's have bayer filter pattern 'RGGB' and
for now that's the only one supported. As soon as I find out about some other
pattern, I'll program support for that too.

So if DCRaw (dcraw -i -v <file>) says the filter pattern is 'RGGBRGGBRGGBRGGB',
the camera is supported.


Using mosstack
=========

This section of the README will be removed. Please refer to manual.pdf found
in program website https://sites.google.com/site/mosstack/ or packaged in
mosstack's distribution under doc/

The program does nothing automatically. It's designed by the process
calibrate -> debayer -> align -> stack and user has to call each of these
individually. User can also skip any of these steps, if for example no
debayering is required or images are already aligned.

UI is a command line one. User calls mosstack with proper arguments and the
program does that step. Most commands work with pattern

    ``mosstack <operation> <arguments>``

where <operation> and <arguments> are something from following list.

<operation> | <arguments>
-------------------------
help        |
init        | <project name>
set         | <setting> <option>
dir         | <path to dir> <image type>
file        | <path to file> <image type>
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

    ``mosstack init Andromeda``

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