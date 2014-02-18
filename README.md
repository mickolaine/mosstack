# PyAstroStack
## an open source stacking software for astronomical images

PyAstroStack is an open source registering and stacking software for
astronomical images. Original (and current) design is made for photos taken
with DSLR camera.

With version 0.1 the program is still quite incomplete; only the core modules
regarding image registration and stacking are working. Full list of working
features:

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

Plan is to have functionality comparable to DeepSkyStacker, IRIS or Regim, but
for now this is far from that.