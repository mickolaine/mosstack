/* -*- C++ -*-

 * File: raw2fitsmodule.cpp
 * Copyright 2015 Mikko Laine (mikko.laine@gmail.com)
 *
 * Raw2fits is a simple program to use decode DSLR raw photos to FITS format using LibRaw and
 * Cfitsio. Decoding should be identical to dcraw -v -4 -t 0 -D. This is Python interface to it

   Raw2fits is is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

   This software is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.



   Sample programs from LibRaw distribution has been used to write
   this software.
 */


#include <Python.h>
#include <string.h>
#include <stdio.h>
#include <math.h>
//#include <string>
#include <fitsio.h>
#include <libraw/libraw.h>

using namespace std;


void write_fits(unsigned width, unsigned height, unsigned short *bitmap, const char *fname) {

  if(!bitmap) return;

  fitsfile *fptr;

  int status = 0;
  int hdutype, naxis;

  long naxes[2], totpix, fpixel[2];

  naxis = 2;
  naxes[0] = width;
  naxes[1] = height;

  totpix = naxes[0] * naxes[1];
  fpixel[0] = 1;  //* read starting with first pixel in each row

  fits_create_file(&fptr, fname, &status);
  fits_create_img(fptr, -32, 2, naxes, &status);

  printf("%d, %d\n", width, height);

  for (fpixel[1] = 1; fpixel[1] <= naxes[1]; fpixel[1]++) {
    fits_write_pix(fptr, TUSHORT, fpixel, width, bitmap + fpixel[1]*width, &status);
  }

  fits_close_file(fptr, &status);

}


int raw2fits_real(char *infile, char *outfile) {

  int  i, ret;
  LibRaw RawProcessor;

  //printf("%s\n", av[1]);
  //printf("%s\n", av[2]);

  putenv ((char*)"TZ=UTC"); // dcraw compatibility, affects TIFF datestamp field

  int verbose=1, autoscale=0, use_gamma=0, out_tiff=0;

  #define P1 RawProcessor.imgdata.idata
  #define P2 RawProcessor.imgdata.other

  #define S RawProcessor.imgdata.sizes
  #define C RawProcessor.imgdata.color
  #define T RawProcessor.imgdata.thumbnail

  #define OUT RawProcessor.imgdata.params
  #define exifLens RawProcessor.imgdata.lens


  if(verbose) printf("Processing file %s\n", infile);

  if( (ret = RawProcessor.open_file(infile) ) != LIBRAW_SUCCESS) {
    fprintf(stderr,"Cannot open %s: %s\n", infile, libraw_strerror(ret));

  }
  if(verbose) {
    printf("Image size: %dx%d\nRaw size: %dx%d\n", S.width, S.height, S.raw_width, S.raw_height);
    printf("Margins: top=%d, left=%d\n", S.top_margin, S.left_margin);
  }

  if( (ret = RawProcessor.unpack() ) != LIBRAW_SUCCESS) {
    fprintf(stderr,"Cannot unpack %s: %s\n", infile, libraw_strerror(ret));

  }
  if(verbose)
    printf("Unpacked....\n");

  if(!(RawProcessor.imgdata.idata.filters || RawProcessor.imgdata.idata.colors == 1)) {
    printf("Only Bayer-pattern RAW files supported, sorry....\n");

  }

  printf ("Timestamp: %s", ctime(&(P2.timestamp)));
  printf ("Camera: %s %s\n", P1.make, P1.model);
  printf ("ISO speed: %d\n", (int) P2.iso_speed);
  printf ("%0.1f sec\n", P2.shutter);
  printf ("Aperture: f/%0.1f\n", P2.aperture);
  printf ("Focal length: %0.1f mm\n", P2.focal_len);
  if (P1.filters) {
    printf ("\nFilter pattern: ");
    if (!P1.cdesc[3]) P1.cdesc[3] = 'G';
    for (int i=0; i < 16; i++)
      putchar (P1.cdesc[RawProcessor.fcol(i >> 1,i & 1)]);
  }
  printf ("\nDaylight multipliers:");
  for(int c=0;c<P1.colors;c++) printf (" %f", C.pre_mul[c]);
  if (C.cam_mul[0] > 0) {
    printf ("\nCamera multipliers:");
    for(int c=0;c<4;c++) printf (" %f", C.cam_mul[c]);
  }


  write_fits(S.raw_width, S.raw_height, RawProcessor.imgdata.rawdata.raw_image, outfile);

  if(verbose) printf("Stored to file %s\n", outfile);

  RawProcessor.recycle(); // just for show this call

  return 0;
}



static PyObject *Raw2fitsError;

/**
  Pass arguments to raw2fits_real which does all the work.
*/
static PyObject* raw2fits(PyObject* self, PyObject* args) {
    char *infile, *outfile;
    PyArg_ParseTuple(args, "ss", &infile, &outfile);
    raw2fits_real(infile, outfile);
    return Py_None;
}


static PyMethodDef raw2fits_methods[] = {
  {"raw2fits", raw2fits, METH_VARARGS, NULL},
  {NULL, NULL, 0, NULL}
};


static struct PyModuleDef raw2fitsmodule = {
   PyModuleDef_HEAD_INIT,
   "raw2fits",  /* name of module */
   NULL,        /* module documentation, may be NULL */
   -1,          /* size of per-interpreter state of the module,
                   or -1 if the module keeps state in global variables. */
   raw2fits_methods
};


PyMODINIT_FUNC PyInit_raw2fits(void)
{
    PyObject *m;

    m = PyModule_Create(&raw2fitsmodule);
    if (m == NULL)
        return NULL;

    Raw2fitsError = PyErr_NewException("raw2fits.error", NULL, NULL);
    Py_INCREF(Raw2fitsError);
    PyModule_AddObject(m, "error", Raw2fitsError);
    return m;
}

int main(int argc, char *argv[]) {
  char* infile = argv[1];
  char* outfile = argv[2];

  //return raw2fits_real(infile, outfile);
}