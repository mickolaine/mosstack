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
#include <math.h>
#include <time.h>



#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

#include "libraw/libraw.h"
#include "fitsio.h"

// no error reporting, only params check

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

    /*
    for (long i = 1; i < width*height+1; i++){
        unsigned int pixel[1];
        pixel[0] = bitmap[i-1];

        fits_write_pix(fptr, TDOUBLE, &i, 1, pixel, &status);
    }*/

    long longone = 1;
    printf("%d, %d\n", width, height);
    fits_write_pix(fptr, TUSHORT, &longone, width*height, bitmap, &status);
    printf("Three\n");

    fits_close_file(fptr, &status);

}

void write_ppm2(unsigned width, unsigned height, unsigned short *bitmap, const char *fname)
{
    if(!bitmap) return;

    FILE *f = fopen(fname,"wb");
    if(!f) return;
    int bits = 16;
    fprintf (f, "P5\n%d %d\n%d\n", width, height, (1 << bits) - 1);
    unsigned char *data = (unsigned char *)bitmap;
    unsigned data_size = width*height*2;

#define SWAP(a,b) { a ^= b; a ^= (b ^= a); }
    for(unsigned i=0; i< data_size; i+=2)
            SWAP(data[i],data[i+1]);
#undef SWAP

    fwrite(data,data_size,1,f);
    fclose(f);
}


void write_ppm(libraw_processed_image_t *img, const char *basename)
{
    if(!img) return;
    // type SHOULD be LIBRAW_IMAGE_BITMAP, but we'll check
    if(img->type != LIBRAW_IMAGE_BITMAP) return;
    // only 3-color images supported...
    if(img->colors != 3) return;

    char fn[1024];
    snprintf(fn,1024,"%s.ppm",basename);
    FILE *f = fopen(fn,"wb");
    if(!f) return;
    fprintf (f, "P6\n%d %d\n%d\n", img->width, img->height, (1 << img->bits)-1);
/*
  NOTE:
  data in img->data is not converted to network byte order.
  So, we should swap values on some architectures for dcraw compatibility
  (unfortunately, xv cannot display 16-bit PPMs with network byte order data
*/
#define SWAP(a,b) { a ^= b; a ^= (b ^= a); }
    if (img->bits == 16 && htons(0x55aa) != 0x55aa)
        for(unsigned i=0; i< img->data_size; i+=2)
            SWAP(img->data[i],img->data[i+1]);
#undef SWAP

    fwrite(img->data,img->data_size,1,f);
    fclose(f);
}

void write_thumb(libraw_processed_image_t *img, const char *basename)
{
    if(!img) return;

    if(img->type == LIBRAW_IMAGE_BITMAP)
        {
            char fnt[1024];
            snprintf(fnt,1024,"%s.thumb",basename);
            write_ppm(img,fnt);
        }
    else if (img->type == LIBRAW_IMAGE_JPEG)
        {
            char fn[1024];
            snprintf(fn,1024,"%s.thumb.jpg",basename);
            FILE *f = fopen(fn,"wb");
            if(!f) return;
            fwrite(img->data,img->data_size,1,f);
            fclose(f);
        }
}

void gamma_curve (unsigned short curve[]);

int main(int ac, char *av[]) {
    int  i, ret, output_thumbs=0;

    // don't use fixed size buffers in real apps!

    LibRaw RawProcessor;

    if(ac<2) {
        printf(
            "mem_image - LibRaw sample, to illustrate work for memory buffers. Emulates dcraw [-4] [-1] [-e] [-h]\n"
            "Usage: %s [-D] [-T] [-v] [-e] raw-files....\n"
            "\t-6 - output 16-bit PPM\n"
            "\t-4 - linear 16-bit data\n"
            "\t-e - extract thumbnails (same as dcraw -e in separate run)\n",
            "\t-h - use half_size\n"
        );
        return 0;
    }

    putenv ((char*)"TZ=UTC"); // dcraw compatibility, affects TIFF datestamp field

    int verbose=1,autoscale=0,use_gamma=0,out_tiff=0;
    char outfn[1024];

#define P1 RawProcessor.imgdata.idata
#define S RawProcessor.imgdata.sizes
#define C RawProcessor.imgdata.color
#define T RawProcessor.imgdata.thumbnail
#define P2 RawProcessor.imgdata.other
#define OUT RawProcessor.imgdata.params


    for (i=1;i<ac;i++) {
        if(av[i][0]=='-') {
            if(av[i][1]=='q' && av[i][2]==0){}

            else if(av[i][1]=='A' && av[i][2]==0)
                autoscale=1;
            else if(av[i][1]=='g' && av[i][2]==0)
                use_gamma = 0;
            else if(av[i][1]=='s' && av[i][2]==0) {
                    i++;
                    OUT.shot_select=av[i]?atoi(av[i]):0;
            }
            continue;
        }

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


            if(autoscale) {
                unsigned max=0,scale;
                for(int j=0; j<S.raw_height*S.raw_width; j++)
                    if(max < RawProcessor.imgdata.rawdata.raw_image[j])
                       max = RawProcessor.imgdata.rawdata.raw_image[j];
                if (max >0 && max< 1<<15) {
                    scale = (1<<16)/max;
                    if(verbose)
                        printf("Scaling with multiplier=%d (max=%d)\n",scale,max);

                    for(int j=0; j<S.raw_height*S.raw_width; j++)
                        RawProcessor.imgdata.rawdata.raw_image[j] *= scale;
                }
            }
            if(use_gamma) {
                unsigned short curve[0x10000];
                gamma_curve(curve);
                for(int j=0; j<S.raw_height*S.raw_width; j++)
                    RawProcessor.imgdata.rawdata.raw_image[j] = curve[RawProcessor.imgdata.rawdata.raw_image[j]];
                if(verbose)
                    printf("Gamma-corrected....\n");
            }

            if(OUT.shot_select)
                snprintf(outfn,sizeof(outfn),"%s-%d.%s",av[i],OUT.shot_select,out_tiff?"tiff":"fits");
            else
                snprintf(outfn,sizeof(outfn),"%s.%s",av[i],out_tiff?"tiff":"fits");

            if(out_tiff){}

            else
                write_fits(S.raw_width, S.raw_height, RawProcessor.imgdata.rawdata.raw_image, outfn);

            if(verbose) printf("Stored to file %s\n",outfn);
    }

    RawProcessor.recycle(); // just for show this call

    return 0;
}

#define SQR(x) ((x)*(x))

void  gamma_curve (unsigned short *curve)
{

    double pwr = 1.0/2.2;
    double ts = 0.0;
    int imax = 0xffff;
    int mode = 2;
  int i;
  double g[6], bnd[2]={0,0}, r;

  g[0] = pwr;
  g[1] = ts;
  g[2] = g[3] = g[4] = 0;
  bnd[g[1] >= 1] = 1;
  if (g[1] && (g[1]-1)*(g[0]-1) <= 0) {
    for (i=0; i < 48; i++) {
      g[2] = (bnd[0] + bnd[1])/2;
      if (g[0]) bnd[(pow(g[2]/g[1],-g[0]) - 1)/g[0] - 1/g[2] > -1] = g[2];
      else	bnd[g[2]/exp(1-1/g[2]) < g[1]] = g[2];
    }
    g[3] = g[2] / g[1];
    if (g[0]) g[4] = g[2] * (1/g[0] - 1);
  }
  if (g[0]) g[5] = 1 / (g[1]*SQR(g[3])/2 - g[4]*(1 - g[3]) +
		(1 - pow(g[3],1+g[0]))*(1 + g[4])/(1 + g[0])) - 1;
  else      g[5] = 1 / (g[1]*SQR(g[3])/2 + 1
		- g[2] - g[3] -	g[2]*g[3]*(log(g[3]) - 1)) - 1;
  for (i=0; i < 0x10000; i++) {
    curve[i] = 0xffff;
    if ((r = (double) i / imax) < 1)
      curve[i] = 0x10000 * ( mode
	? (r < g[3] ? r*g[1] : (g[0] ? pow( r,g[0])*(1+g[4])-g[4]    : log(r)*g[2]+1))
	: (r < g[2] ? r/g[1] : (g[0] ? pow((r+g[4])/(1+g[4]),1/g[0]) : exp((r-1)/g[2]))));
  }
}

