===========
pyAstroStack
===========

pyAstroStack is an open source registering and stacking software for
astronomical images. Original (and current) design is made for photos taken
with DSLR camera. The program is still quite incomplete; only the core modules
regarding image registration and stacking are working. If you understood none
of that, this program probably isn't for you.

Here's a piece of the model README.txt from
<http://guide.python-distribute.org/creation.html#directory-layout>
to remind me how this works.

Towel Stuff provides such and such and so and so. You might find
it most useful for tasks involving <x> and also <y>. Typical usage
often looks like this::

    #!/usr/bin/env python

    from towelstuff import location
    from towelstuff import utils

    if utils.has_towel():
        print "Your towel is located:", location.where_is_my_towel()

(Note the double-colon and 4-space indent formatting above.)

Paragraphs are separated by blank lines. *Italics*, **bold**,
and ``monospace`` look like this.


Prerequisites
=========

pyAstroStack relies heavily on other open source programs and libraries. Here's
a complete list:

* DCRaw - <http://www.cybercom.net/~dcoffin/dcraw/>

* SExtractor - <http://www.astromatic.net/software/sextractor>
  Installation of this might be tricky if it's not included in your Linux
  distribution. RPM-packages on the link above should work in most cases.
  I even installed this on Gentoo with provided RPM.

* Rawtran - <http://integral.physics.muni.cz/rawtran/>
  I try to get rid of this. It's not included in any Linux distribution I
  checked so installation is done from source.
  
* ImageMagick - <http://www.imagemagick.org>

* ExifTool - <http://www.sno.phy.queensu.ca/~phil/exiftool/>

* AstroPy - <http://www.astropy.org/>
  or
  pyFITS - <http://www.stsci.edu/institute/software_hardware/pyfits>

* NumPy - <http://www.numpy.org/>



Installing required software
=========

Debian and Ubuntu (and perhaps derivatives)
-------------

This oneliner ought install most of the required software

    ``apt-get install dcraw sextractor imagemagick numpy python3-pip``

Rawtran is installed by following instructions in
<http://integral.physics.muni.cz/rawtran/>

AstroPy can be installed now with

    ``pip-3.2 install astropy``

as root or

    ``pip-3.2 install --user astropy``

if you want the installation on users $HOME

Gentoo
------------
Foo
