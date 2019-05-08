#!/usr/bin/python3

from subprocess import call
from os import remove
from astropy.io import fits
import numpy as np

try:
    remove("/home/micko/PycharmProjects/mosstack/test/red.fits")
    remove("/home/micko/PycharmProjects/mosstack/test/green.fits")
    remove("/home/micko/PycharmProjects/mosstack/test/blue.fits")
except:
    pass

call(["../tools/debayer", "/media/data/astrostack/Testi1_light_0_orig.fits"], cwd="/home/micko/src/mosstack/test/")

orig = fits.open("/media/data/astrostack/Testi1_light_0_rgb.fits")[0].data

newfiles = []

newfiles.append(fits.open("/home/micko/src/mosstack/test/red.fits"))
newfiles.append(fits.open("/home/micko/sec/mosstack/test/green.fits"))
newfiles.append(fits.open("/home/micko/sec/mosstack/test/blue.fits"))

new = []

for i in 0, 1, 2:
    new.append(newfiles[i][0].data)

new = np.array(new)

diff = orig - new

print(np.amax(orig))
print(np.amin(orig))
print(np.amax(new))
print(np.amin(new))
print("Difference")
print(np.amax(diff))
print(np.amin(diff))
print(diff)