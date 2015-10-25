# Mosstack
## Mikko's Open Source Stacker for astronomical images

Mosstack is an open source registering and stacking software for
astronomical images. Original (and current) design is made for photos taken
with DSLR camera.

Version 0.7 has new command line interface and it drops several dependencies.
It changes default RGB-conversion to one written in C. PyOpenCL will probably
be dropped in the future.

Full list of working features:

- Image decoding
    - C++ and LibRaw (DCRaw still required but not for long)

- CFA to RGB conversion
    - Variable Number of Gradients: C (default), OpenCL, Cython
    - Bilinear: OpenCL, Cython

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