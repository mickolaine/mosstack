/*#include <Python.h>*/
#include <string.h>
#include <stdio.h>
#include <math.h>
#include "fitsio.h"

int main(int argc, char *argv[]) {
  const char* infile = argv[1];
  const char* outfile = argv[2];

  debayer_real(infile, outfile);

}

int debayer_real(char* infile, char* outfile) {

  fitsfile *fptr, *rfptr, *gfptr, *bfptr, *rgbfptr;
  char card[FLEN_CARD];

  int status = 0;
  int hdutype, naxis, ii;
  long naxes[2], totpix, fpixel[2], fpixelread[2], naxes3d[3], fpixel3d[3];
  double *r, *g, *b, *pix1, *pix2, *pix3, *pix4, *pix5;

  
  if ( !fits_open_image(&fptr, infile, READONLY, &status) ) {

    if (fits_get_hdu_type(fptr, &hdutype, &status) || hdutype != IMAGE_HDU) {
      printf("Error: this program only works on images, not tables\n");
      return(1);
    }

    fits_get_img_dim(fptr, &naxis, &status);
    fits_get_img_size(fptr, 2, naxes, &status);
    
    int naxes0 = naxes[0];
    int naxes1 = naxes[1];

    naxes3d[0] = naxes[0];
    naxes3d[1] = naxes[1];
    naxes3d[2] = 3;

    printf("Original image: %ld, %ld\n", naxes[0], naxes[1]);
    printf("New image: %ld, %ld, %ld\n", naxes3d[0], naxes3d[1], naxes3d[2]);

    if (status || naxis != 2) {
      printf("Error: NAXIS = %d.  Only 2-D image", naxis);
    }

    /* Five lines of data in memory */
    pix1 = (double *) malloc(naxes[0] * sizeof(double)); /* memory for 1 row */
    pix2 = (double *) malloc(naxes[0] * sizeof(double)); /* memory for 1 row */
    pix3 = (double *) malloc(naxes[0] * sizeof(double)); /* memory for 1 row */
    pix4 = (double *) malloc(naxes[0] * sizeof(double)); /* memory for 1 row */
    pix5 = (double *) malloc(naxes[0] * sizeof(double)); /* memory for 1 row */
    
    if (pix4 == NULL) {
      printf("Memory allocation error\n");
      return(1);
    }
    
    totpix = naxes[0] * naxes[1];
    fpixel[0] = 1;  /* read starting with first pixel in each row */

    /* Create new file */
    fits_create_file(&rgbfptr, outfile, &status);
    fits_create_img(rgbfptr, -32, 3, naxes3d, &status);

    
    /* start by loading 3 first lines in memory */
    fpixel[1] = 1;
    fits_read_pix(fptr, TDOUBLE, fpixel, naxes[0],0, pix3,0, &status);
    fpixel[1]++;
    fits_read_pix(fptr, TDOUBLE, fpixel, naxes[0],0, pix4,0, &status);
    fpixel[1]++;
    fits_read_pix(fptr, TDOUBLE, fpixel, naxes[0],0, pix5,0, &status);
    
    /* process image one row at a time; increment row # in each loop */
    for (fpixel[1] = 1; fpixel[1] <= naxes[1]; fpixel[1]++) {

	  //printf("begin to calculate line %ld\n", fpixel[1]);
	  //printf("Reserve red %ld\n", naxes[0]);
      r = (double *) malloc(naxes[0] * sizeof(double));
	  //printf("Reserve green\n");
      g = (double *) malloc(naxes[0] * sizeof(double));
	  //printf("Reserve blue\n");
      b = (double *) malloc(naxes[0] * sizeof(double));

      //printf("Calculations...\n");
      vng(pix1, pix2, pix3, pix4, pix5, r, g, b, fpixel[0], fpixel[1], naxes0, naxes1);
      //printf("calculated line %ld\n", fpixel[1]);

      fpixel3d[0] = fpixel[0];
      fpixel3d[1] = fpixel[1];
      fpixel3d[2] = 1;

      //printf("Writing red\n");
      fits_write_pix(rgbfptr, TDOUBLE, fpixel3d, naxes3d[0], r, &status);
      //printf("Writing green\n");
      fpixel3d[2] = 2;
      fits_write_pix(rgbfptr, TDOUBLE, fpixel3d, naxes3d[0], g, &status);
      //printf("Writing blue\n");
      fpixel3d[2] = 3;
      fits_write_pix(rgbfptr, TDOUBLE, fpixel3d, naxes3d[0], b, &status);

      //printf("Freeing memory\n");
      free(pix1);
      pix1 = pix2;
      pix2 = pix3;
      pix3 = pix4;
      pix4 = pix5;
      pix5 = (double *) malloc(naxes[0] * sizeof(double));

      //printf("%ld, %ld\n", fpixel[1], naxes[1]);

      if(fpixel[1] >= naxes[1] - 2) {

        //printf("skip\n");
      }
      else {
        long fpixelread[2] = {fpixel[0], fpixel[1]+3};
        fits_read_pix(fptr, TDOUBLE, fpixelread, naxes[0],0, pix5,0, &status);
        //printf("read line %ld\n", fpixel[1]+3);
      }

    }

    free(pix1);
    free(pix2);
    free(pix3);
    free(pix4);
    free(pix5);
      
    free(r);
    free(g);
    free(b);

    fits_close_file(fptr, &status);
    fits_close_file(rgbfptr, &status);
      
  }

  if (status)  {
    fits_report_error(stderr, status); /* print any error message */
    //printf("  minimum value = %g\n", minval);
  }

  return(status);
}


int bilinear(double *pix1, double *pix2, double *pix3, double *pix4, double *pix5,
	     double *r, double *g, double *b,
	     long fpixel0, long fpixel1, int naxes0, int naxes1) {

  
  int i = 0;
  
  for (i = 0; i < naxes0; i++) {
    // fpixel1: line
    // i:       row

    // green pixels
    int green_on_blue = (fpixel1%2 == 0) & (i%2 == 0); // green pixel on red  line
    int green_on_red  = (fpixel1%2 == 1) & (i%2 == 1); // green pixel on blue line
    // red pixels
    int blue  = (fpixel1%2 == 0) & (i%2 == 1);
    // blue pixels
    int red = (fpixel1%2 == 1) & (i%2 == 0);
    
    // 2-line border is copied as is
    if ((fpixel1 < 3 | fpixel1 > naxes1 - 3) | (i < 3 | i > naxes0 - 3)) {
    
      r[i] = pix3[i];
    
    }

    // green pixels
    else if (green_on_red | green_on_blue) {

      g[i] = pix3[i];

      if (green_on_blue) {
	r[i] = 0.5*(pix2[i] + pix4[i]);
	b[i] = 0.5*(pix3[i-1] + pix3[i+1]); 
      }
      if (green_on_red)  {
	b[i] = 0.5*(pix2[i] + pix4[i]);
	r[i] = 0.5*(pix3[i-1] + pix3[i+1]);
      }

    }

    // red pixels
    else if (red) {
      b[i] = pix3[i];

      g[i] = 0.25*(pix2[i] + pix3[i-1] + pix3[i+1] + pix4[i]);
      b[i] = 0.25*(pix2[i-1] + pix2[i+1] + pix4[i-1] + pix4[i+1]);
      
    }
    
    // blue pixels
    
    else if (blue){
      
      b[i] = pix3[i];

      g[i] = 0.25*(pix2[i] + pix3[i-1] + pix3[i+1] + pix4[i]);
      r[i] = 0.25*(pix2[i-1] + pix2[i+1] + pix4[i-1] + pix4[i+1]);
      
    }
    // you shouldn't end up in here. Also there shouldn't be any zeros in array
    else {
      r[i] = 0.0;
      g[i] = 0.0;
      b[i] = 0.0;
    }
  }
}

int vng(double *pix1, double *pix2, double *pix3, double *pix4, double *pix5,
	double *r, double *g, double *b,
	long fpixel0, long fpixel1, int naxes0, int naxes1) {
  
  int i = 0;
  
  for (i = 0; i < naxes0; i++) {
    // fpixel1: line
    // i:       row

    // green pixels
    int green_on_blue = (fpixel1%2 == 0) & (i%2 == 0); // green pixel on red  line
    int green_on_red  = (fpixel1%2 == 1) & (i%2 == 1); // green pixel on blue line
    // red pixels
    int blue  = (fpixel1%2 == 0) & (i%2 == 1);
    // blue pixels
    int red = (fpixel1%2 == 1) & (i%2 == 0);

    double rsum = 0, gsum = 0, bsum = 0;
    
    // 2-line border is copied as is
    if ((fpixel1 < 3 | fpixel1 > naxes1 - 3) | (i < 3 | i > naxes0 - 3)) {
      
      r[i] = pix3[i];
      g[i] = pix3[i];
      b[i] = pix3[i];
    }

    // green pixels
    else if (green_on_red | green_on_blue) {

      double g1,  r2,  g3,  r4,  g5,
	         b6,  g7,  b8,  g9,  b10,
	         g11, r12, g13, r14, g15,
	         b16, g17, b18, g19, b20,
	         g21, r22, g23, r24, g25;

      g1  = pix1[i-2];
      r2  = pix1[i-1];
      g3  = pix1[i];
      r4  = pix1[i+1];
      g5  = pix1[i+2];
      b6  = pix2[i-2];
      g7  = pix2[i-1];
      b8  = pix2[i];
      g9  = pix2[i+1];
      b10 = pix2[i+2];
      g11 = pix3[i-2];
      r12 = pix3[i-1];
      g13 = pix3[i];
      r14 = pix3[i+1];
      g15 = pix3[i+2];
      b16 = pix4[i-2];
      g17 = pix4[i-1];
      b18 = pix4[i];
      g19 = pix4[i+1];
      b20 = pix4[i+2];
      g21 = pix5[i-2];
      r22 = pix5[i-1];
      g23 = pix5[i];
      r24 = pix5[i+1];
      g25 = pix5[i+2];

      double grn, gre, grs, grw, grne, grse, grnw, grsw;

      grn  = fabs(g3  - g13) + fabs(b8  - b18) + fabs(g7  - g17)/2.0 +
	         fabs(g9  - g19)/2.0 + fabs(r2  - r12)/2.0 + fabs(r4  - r14)/2.0;
      gre  = fabs(r14 - r12) + fabs(g15 - g13) + fabs(g9  - g7 )/2.0 +
	         fabs(g19 - g17)/2.0 + fabs(b10 - b8 )/2.0 + fabs(b20 - b18)/2.0;
      grs  = fabs(b18 - b8 ) + fabs(g23 - g13) + fabs(g19 - g9 )/2.0 +
	         fabs(g17 - g7 )/2.0 + fabs(r24 - r14)/2.0 + fabs(r22 - r12)/2.0;
      grw  = fabs(r12 - r14) + fabs(g11 - g13) + fabs(g17 - g19)/2.0 +
	         fabs(g7  - g9 )/2.0 + fabs(b16 - b18)/2.0 + fabs(b6  - b8 )/2.0;
      grne = fabs(g9  - g17) + fabs(g5  - g13) + fabs(r4  - r12) + fabs(b10 - b18);
      grse = fabs(g19 - g7 ) + fabs(g25 - g13) + fabs(b20 - b8 ) + fabs(r24 - r12);
      grnw = fabs(g7  - g19) + fabs(g1  - g13) + fabs(b6  - b18) + fabs(r2  - r14);
      grsw = fabs(g17 - g9 ) + fabs(g21 - g13) + fabs(r22 - r14) + fabs(b16 - b8 );

      double min, max, t1, t2, t3, t4;

      t1 = fmin(grn, gre);
      t2 = fmin(grs, grw);
      t3 = fmin(grne, grse);
      t4 = fmin(grnw, grsw);
      t1 = fmin(t1, t2);
      t3 = fmin(t3, t4);
      min = fmin(t1, t3);

      t1 = fmax(grn, gre);
      t2 = fmax(grs, grw);
      t3 = fmax(grne, grse);
      t4 = fmax(grnw, grsw);
      t1 = fmax(t1, t2);
      t3 = fmax(t3, t4);
      max = fmax(t1, t3);

      double T = 1.5*min + 0.5*(max-min);

      int n = 0;
      double rsum = 0,
	         gsum = 0,
	         bsum = 0;

      if (grn  <= T) {
	    rsum = rsum + (r2 + r4 + r12 + r14)/4.0;
	    gsum = gsum + (g3 + g13)/2.0;
	    bsum = bsum + b8;
	    n = n+1;
      }
      if (gre  <= T) {
	    rsum = rsum + r14;
	    gsum = gsum + (g13 + g15)/2.0;
	    bsum = bsum + (b8 + b10 + b18 + b20)/4.0;
	    n = n+1;
      }
      if (grs  <= T) {
	    rsum = rsum + (r12 + r14 + r22 + r24)/4.0;
	    gsum = gsum + (g13 + g23)/2.0;
	    bsum = bsum + b18;
	    n = n+1;
      }
      if (grw  <= T)  {
	    rsum = rsum + r12;
	    gsum = gsum + (g11 + g13)/2.0;
	    bsum = bsum + (b6 + b8 + b16 + b18)/4.0;
	    n = n+1;
      }
      if (grne <= T)  {
	    rsum = rsum + (r4 + r14)/2.0;
	    gsum = gsum + g9;
	    bsum = bsum + (b8 + b10)/2.0;
	    n = n+1;
      }
      if (grse <= T)  {
	    rsum = rsum + (r14 + r24)/2.0;
	    gsum = gsum + g19;
	    bsum = bsum + (b18 + b20)/2.0;
	    n = n+1;
      }
      if (grnw <= T) {
        rsum = rsum + (r2 + r12)/2.0;
        gsum = gsum + g7;
        bsum = bsum + (b6 + b8)/2.0;
        n = n+1;
      }
      if (grsw <= T) {
        rsum = rsum + (r12 + r22)/2.0;
        gsum = gsum + g17;
        bsum = bsum + (b16 + b18)/2.0;
        n = n+1;
      }
      if(n==0){
	    n = 1;
      }

      if (green_on_red) {
        r[i] = g13 + (rsum - gsum)/n;
        g[i] = g13;
        b[i] = g13 + (bsum - gsum)/n;
      }
      if (green_on_blue) {
        b[i] = g13 + (rsum - gsum)/n;
        g[i] = g13;
        r[i] = g13 + (bsum - gsum)/n;

      }
      
    }

    // red pixels
    else if (red | blue) {

      double r1,  g2,  r3,  g4,  r5,
             g6,  b7,  g8,  b9,  g10,
             r11, g12, r13, g14, r15,
             g16, b17, g18, b19, g20,
             r21, g22, r23, g24, r25;
      
      r1  = pix1[i-2];
      g2  = pix1[i-1];
      r3  = pix1[i];
      g4  = pix1[i+1];
      r5  = pix1[i+2];
      g6  = pix2[i-2];
      b7  = pix2[i-1];
      g8  = pix2[i];
      b9  = pix2[i+1];
      g10 = pix2[i+2];
      r11 = pix3[i-2];
      g12 = pix3[i-1];
      r13 = pix3[i];
      g14 = pix3[i+1];
      r15 = pix3[i+2];
      g16 = pix4[i-2];
      b17 = pix4[i-1];
      g18 = pix4[i];
      b19 = pix4[i+1];
      g20 = pix4[i+2];
      r21 = pix5[i-2];
      g22 = pix5[i-1];
      r23 = pix5[i];
      g24 = pix5[i+1];
      r25 = pix5[i+2];


      double grn, gre, grs, grw, grne, grse, grnw, grsw;

      grn  = fabs(g8  - g18) + fabs(r3  - r13) + fabs(b7  - b17)/2.0 +
	         fabs(b9  - b19)/2.0 + fabs(g2  - g12)/2.0 + fabs(g4  - g14)/2.0;
      gre  = fabs(g14 - g12) + fabs(r15 - r13) + fabs(b9  - b7 )/2.0 +
	         fabs(b19 - b17)/2.0 + fabs(g10 - g8 )/2.0 + fabs(g20 - g18)/2.0;
      grs  = fabs(g18 - g8 ) + fabs(r23 - r13) + fabs(b19 - b9 )/2.0 +
	         fabs(b17 - b7 )/2.0 + fabs(g24 - g14)/2.0 + fabs(g22 - g12)/2.0;
      grw  = fabs(g12 - g14) + fabs(r11 - r13) + fabs(b17 - b19)/2.0 +
	         fabs(b7  - b9 )/2.0 + fabs(g16 - g18)/2.0 + fabs(g6  - g8 )/2.0;
      grne = fabs(b9  - b17) + fabs(r5  - r13) + fabs(g8  - g12)/2.0 +
	         fabs(g14 - g18)/2.0 + fabs(g4  - g8 )/2.0 + fabs(g10 - g14)/2.0;
      grse = fabs(b19 - b7 ) + fabs(r25 - r13) + fabs(g14 - g8 )/2.0 +
             fabs(g18 - g12)/2.0 + fabs(g20 - g14)/2.0 + fabs(g24 - g18)/2.0;
      grnw = fabs(b7  - b19) + fabs(r1  - r13) + fabs(g12 - g18)/2.0 +
	         fabs(g8  - g14)/2.0 + fabs(g6  - g12)/2.0 + fabs(g2  - g8 )/2.0;
      grsw = fabs(b17 - b9 ) + fabs(r21 - r13) + fabs(g18 - g14)/2.0 +
	         fabs(g12 - g8 )/2.0 + fabs(g22 - g18)/2.0 + fabs(g16 - g12)/2.0;

      double min, max, t1, t2, t3, t4;

      t1 = fmin(grn, gre);
      t2 = fmin(grs, grw);
      t3 = fmin(grne, grse);
      t4 = fmin(grnw, grsw);
      t1 = fmin(t1, t2);
      t3 = fmin(t3, t4);
      min = fmin(t1, t3);

      t1 = fmax(grn, gre);
      t2 = fmax(grs, grw);
      t3 = fmax(grne, grse);
      t4 = fmax(grnw, grsw);
      t1 = fmax(t1, t2);
      t3 = fmax(t3, t4);
      max = fmax(t1, t3);

      double T = 1.5*min + 0.5*(max-min);

      int n = 0;
      double rsum = 0,
             gsum = 0,
             bsum = 0;

      if (grn  <= T) {
        rsum = rsum + (r3 + r13)/2.0;
        gsum = gsum + g8;
        bsum = bsum + (b7 + b9)/2.0;
        n = n+1;
      }
      if (gre  <= T) {
        rsum = rsum + (r15 + r13)/2.0;
        gsum = gsum + g14;
        bsum = bsum + (b19 + b9)/2.0;
        n = n+1;
      }
      if (grs  <= T) {
        rsum = rsum + (r23 + r13)/2.0;
        gsum = gsum + g18;
        bsum = bsum + (b17 + b19)/2.0;
        n = n+1;
      }
      if (grw  <= T)  {
        rsum = rsum + (r11 + r13)/2.0;
        gsum = gsum + g12;
        bsum = bsum + (b7 + b17)/2.0;
        n = n+1;
      }
      if (grne <= T)  {
        rsum = rsum + (r5 + r13)/2.0;
        gsum = gsum + (g4 + g8 + g10 + g14)/4.0;
        bsum = bsum + b9;
        n = n+1;
      }
      if (grse <= T)  {
        rsum = rsum + (r25 + r13)/2.0;
        gsum = gsum + (g14 + g18 + g20 + g24)/4.0;
        bsum = bsum + b19;
        n = n+1;
      }
      if (grnw <= T) {
        rsum = rsum + (r1 + r13)/2.0;
        gsum = gsum + (g2 + g6 + g8 + g12)/4.0;
        bsum = bsum + b7;
        n = n+1;
      }
      if (grsw <= T) {
        rsum = rsum + (r21 + r13)/2.0;
        gsum = gsum + (g12 + g16 + g18 + g22)/4.0;
        bsum = bsum + b17;
        n = n+1;
      }

      if(n == 0){
	    n = 1.0;
      }

      if (red) { 
        r[i] = r13;
        g[i] = r13 + (gsum - rsum)/n;
        b[i] = r13 + (bsum - rsum)/n;
      }
      else if (blue) {
        b[i] = r13;
        g[i] = r13 + (gsum - rsum)/n;
        r[i] = r13 + (bsum - rsum)/n;
      }

    }

    // you shouldn't end up in here. Also there shouldn't be any zeros in array  
    else {

      r[i] = 0.0;
      g[i] = 0.0;
      b[i] = 0.0;
    }


  }
}