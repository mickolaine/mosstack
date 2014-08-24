# Mosstack
## Mikko's Open Source Stacker for astronomical images

Mosstack is an open source registering and stacking software for
astronomical images. Original (and current) design is made for photos taken
with DSLR camera.

Version 0.5 finally brings multithreading to GUI. Other than that, the features
are still quite limited

Full list of working features:

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

Plan is to have functionality comparable to DeepSkyStacker, IRIS or Regim, but
for now this is far from that.