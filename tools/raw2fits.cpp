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
    long naxes[2], totpix;

    naxis = 2;
    naxes[0] = width;
    naxes[1] = height;

    totpix = naxes[0] * naxes[1];
    printf("One\n");

    fits_create_file(&fptr, fname, &status);

    printf("Two\n");
    fits_create_img(fptr, -32, 2, naxes, &status);

    long longone = 1;
    printf("%d, %d\n", width, height);
    fits_write_pix(fptr, TUSHORT, &longone, width*height, bitmap, &status);
    printf("Three\n");

    fits_close_file(fptr, &status);

}


int main(int ac, char *av[]) {
    int  i, ret;

    LibRaw RawProcessor;

    if(ac<2) {
        printf(
            "raw2fits - Simple program to convert DSLR raw files to fits format.\n"
            "The output data is supposed to be same than dcraw -4 -D -t 0\n\n"
            "Usage: raw2fits [raw-file]\n"
        );
        return 0;
    }

    putenv ((char*)"TZ=UTC"); // dcraw compatibility, affects TIFF datestamp field

    int verbose=1, autoscale=0, use_gamma=0, out_tiff=0;
    char outfn[1024];

#define P1 RawProcessor.imgdata.idata
#define S RawProcessor.imgdata.sizes
#define C RawProcessor.imgdata.color
#define T RawProcessor.imgdata.thumbnail
#define P2 RawProcessor.imgdata.other
#define OUT RawProcessor.imgdata.params


    for (i=1;i<ac;i++) {

        if(verbose) printf("Processing file %s\n",av[i]);
        if( (ret = RawProcessor.open_file(av[i])) != LIBRAW_SUCCESS) {
            fprintf(stderr,"Cannot open %s: %s\n",av[i],libraw_strerror(ret));
            continue; // no recycle b/c open file will recycle itself
        }
        if(verbose) {
            printf("Image size: %dx%d\nRaw size: %dx%d\n",S.width,S.height,S.raw_width,S.raw_height);
            printf("Margins: top=%d, left=%d\n",S.top_margin,S.left_margin);
        }

        if( (ret = RawProcessor.unpack() ) != LIBRAW_SUCCESS) {
            fprintf(stderr,"Cannot unpack %s: %s\n",av[i],libraw_strerror(ret));
            continue;
        }

        if(verbose)
            printf("Unpacked....\n");

        if(!(RawProcessor.imgdata.idata.filters || RawProcessor.imgdata.idata.colors == 1)) {
            printf("Only Bayer-pattern RAW files supported, sorry....\n");
            continue;
        }

        snprintf(outfn,sizeof(outfn),"%s.%s",av[i],out_tiff?"tiff":"fits");

        write_fits(S.raw_width, S.raw_height, RawProcessor.imgdata.rawdata.raw_image, outfn);

        if(verbose) printf("Stored to file %s\n",outfn);
    }

    RawProcessor.recycle(); // just for show this call

    return 0;
}