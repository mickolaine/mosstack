/* -*- C++ -*-

 * File: raw2fits.cpp
 * Copyright 2015 Mikko Laine (mikko.laine@gmail.com)
 *
 * Raw2fits is a simple program to use decode DSLR raw photos to FITS format using LibRaw and
 * Cfitsio. Decoding should be identical to dcraw -v -4 -t 0 -D

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

#include <stdio.h>
#include <string.h>

#include "libraw/libraw.h"
#include "fitsio.h"


void write_fits(unsigned width, unsigned height, unsigned short *bitmap, const char *fname) {

    if(!bitmap) return;

    fitsfile *fptr;

    int status = 0;
    int hdutype, naxis;

    long naxes[2], totpix, fpixel[2];

    /*
    unsigned long **data;

    data = (unsigned long **) malloc(height * sizeof(unsigned long*));
    if (data){
        for (int i = 0; i < height; i++) {
            data[i] = (unsigned long *) malloc(width * sizeof(unsigned long));
        }
    }

    //unsigned short data[width][height];
    */
    naxis = 2;
    naxes[0] = width;
    naxes[1] = height;

    totpix = naxes[0] * naxes[1];
    fpixel[0] = 1;  /* read starting with first pixel in each row */

    fits_create_file(&fptr, fname, &status);
    fits_create_img(fptr, -32, 2, naxes, &status);

    printf("%d, %d\n", width, height);

    /*
    for (int i = 0; i < height; i++) {
        //printf("Line: %d\n ", i);
        for (int j = 0; j < width; j++) {
            //printf("Line: %d of %d, Element: %d of %d \n", i, width, j, height);
            //printf("Bitmap index %d of %ld\n", (height*i + j), totpix);

            data[i][j] = bitmap[width*i + j];
            //printf("Bitmap value %d\n", bitmap[height*i + j]);
            fflush(stdout);
        }
    }
    */
    for (fpixel[1] = 1; fpixel[1] <= naxes[1]; fpixel[1]++) {
        //printf("%ld\n ", fpixel[1]);
        //fits_write_pix(fptr, TULONG, fpixel, width, data[fpixel[1]-1], &status);
        fits_write_pix(fptr, TUSHORT, fpixel, width, bitmap + fpixel[1]*width, &status);
    }

    fits_close_file(fptr, &status);

}


int main(int ac, char *av[]) {
    int  i, ret;

    LibRaw RawProcessor;



    if(ac<3) {
        printf(
            "raw2fits - Simple program to convert DSLR raw files to fits format.\n"
            "The output data is supposed to be same than dcraw -4 -D -t 0\n\n"
            "Usage: raw2fits [raw-file]\n"
        );
        return 0;
    }

    char *infn;
    char *outfn;

    infn = av[1];
    outfn = av[2];

    printf("%s\n", av[1]);
    printf("%s\n", av[2]);

    putenv ((char*)"TZ=UTC"); // dcraw compatibility, affects TIFF datestamp field

    int verbose=1, autoscale=0, use_gamma=0, out_tiff=0;

#define P1 RawProcessor.imgdata.idata
#define S RawProcessor.imgdata.sizes
#define C RawProcessor.imgdata.color
#define T RawProcessor.imgdata.thumbnail
#define P2 RawProcessor.imgdata.other
#define OUT RawProcessor.imgdata.params


    if(verbose) printf("Processing file %s\n", infn);

    if( (ret = RawProcessor.open_file(infn) ) != LIBRAW_SUCCESS) {
        fprintf(stderr,"Cannot open %s: %s\n", infn, libraw_strerror(ret));

    }
    if(verbose) {
        printf("Image size: %dx%d\nRaw size: %dx%d\n", S.width, S.height, S.raw_width, S.raw_height);
        printf("Margins: top=%d, left=%d\n", S.top_margin, S.left_margin);
    }

    if( (ret = RawProcessor.unpack() ) != LIBRAW_SUCCESS) {
        fprintf(stderr,"Cannot unpack %s: %s\n", infn, libraw_strerror(ret));

    }
    if(verbose)
        printf("Unpacked....\n");

    if(!(RawProcessor.imgdata.idata.filters || RawProcessor.imgdata.idata.colors == 1)) {
        printf("Only Bayer-pattern RAW files supported, sorry....\n");

    }

    write_fits(S.raw_width, S.raw_height, RawProcessor.imgdata.rawdata.raw_image, outfn);

    if(verbose) printf("Stored to file %s\n", outfn);


    RawProcessor.recycle(); // just for show this call

    return 0;
}