# Mosstack
## Mikko's Open Source Stacker for astronomical images

Mosstack is an open source registering and stacking software for
astronomical images. Original (and current) design is made for photos taken
with DSLR camera.

Version 0.6 brings support for everything DCRaw opens, makes project control
easier and gives a choice to crop the image before stacking.

Full list of working features:

- CFA to RGB conversion (see below for supported cameras)
    - Bilinear (OpenCL, Cython)
    - Variable Number of Gradients (OpenCL, Cython)

- Registering
    - SExtractor and http://adsabs.harvard.edu/abs/1986AJ.....91.1244G

- Aligning
    - Scikit-image

- Cropping image

- Stacking
    - Maximum value
    - Minimum value
    - Mean value
    - Median value
    - Sigma Median
    - Sigma Clipping

- A somewhat working GUI
    - Written on PyQt4
    - Multithreading for some parts of the process

- A command line interface

Plan is to have functionality comparable to DeepSkyStacker, IRIS or Regim, but
for now this is far from that.