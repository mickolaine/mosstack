===========
pyAstroStack
===========

pyAstroStack is an open source registering and stacking software for
astronomical images. Original (and current) design is made for photos taken
with DSLR camera. The program is still quite incomplete; only the core modules
regarding image registration and stacking are working. If you understood none
of that, this program probably isn't for you.


Prerequisites
=========

pyAstroStack relies heavily on other open source programs and libraries. Here's
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
  or
  pyFITS - <http://www.stsci.edu/institute/software_hardware/pyfits>

* NumPy - <http://www.numpy.org/>

* Cython - <http://www.cython.org/>

* PyOpenCL - <http://mathema.tician.de/software/pyopencl>


Installing
=========

Download the archive and extract it. That you most likely have already done since you're reading this document.
Installing can be done by

    ``python setup.py install``

or if you want to install under $HOME

    ``python setup.py install --user``

Note that command python should run python3 and python2 won't work. If you have python2 as default python interpreter,
running the script

    ``python3 setup.py install --user``

might work.

Installing required software
=========

Ubuntu
-------------

Most dependencies can be installed straight from package manager. Here's an Apt-get one-liner for that

    ``apt-get install python3-pip cython3 python3-numpy dcraw python3-pyopencl imagemagick sextractor libtiff5-dev``

This assumes you have the newest full Ubuntu desktop installed. If you have customized your installation, other packages
might be required as well.

Python packages AstroPy and Python-imaging (Pillow) are also on package manager, but only for Python2. For Python3
they can be easily installed with

    ``pip3 install astropy``
    ``pip3 install pillow``



Debian and Ubuntu (and perhaps derivatives)
-------------

This oneliner ought install most of the required software

    ``apt-get install dcraw sextractor libtiff5-dev imagemagick numpy python3-pip python3-pyopencl``

AstroPy can be installed now with

    ``pip-3.2 install astropy``

as root or

    ``pip-3.2 install --user astropy``

if you want the installation on users $HOME.

Also Python packages Pillow and Cython have to be installed with pip

    ``pip-3.2 install cython``
    ``pip-3.2 install pillow``

Gentoo
------------
AstroPy and SExtractor are in Science overlay, so that has to be activated. Easiest way is to use Layman

    ``emerge layman``

and activate the overlay by

    ``layman -a science``

After that all the requirements can be installed with

    ``emerge dcraw sextractor imagemagick exiftool astropy numpy cython pyopencl``

Some of these might be ~arch and require unmasking, but as a Gentoo user you might know how to get around it


Features
=========

Ultimate plan is to have functionality similar to DeepSkyStacker or IRIS, but
for now the program is limited to basic functionality.

List of features
 - CFA to RGB conversion (see below for supported cameras)
  - Bilinear (python, only for testing)
  - Bilinear (OpenCL)
  - LaRoche-Prescott (OpenCL)
  - Variable Number of Gradients (OpenCL)

 - Registering
  - SExtractor and http://adsabs.harvard.edu/abs/1986AJ.....91.1244G

 - Aligning
  - Affine transformations by ImageMagick

 - Stacking
  - Mean value
  - Median value

Supported cameras
------------
I have a Canon EOS 1100D and I've used that to do all the testings. Most likely
everything with the same Bayer filter pattern works.

List of tested Camera Model IDs (as printed by exiftool)
 - EOS Rebel T3 / 1100D / Kiss X50

List of tested Bayer filter patterns (as printed by dcraw -i -v)
 - RGGBRGGBRGGBRGGB


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