"""
Some tests for debayering algorithms and classes
"""

from mosstack.Debayer import *
from mosstack import Frame
from datetime import datetime
import numpy as np
from PIL import Image as Im

directory = "/media/data/astrostack/Testdata/"
file1 = "Andromeda_Test.cr2"

frames = []

for i in [0, 1, 2, 3]:
    frames.append(Frame.Frame(rawpath=directory+file1, ftype="light"))

bilinearcython = BilinearCython()
bilinearopencl = BilinearOpenCl()
vngcython = VNGCython()
vngopencl = VNGOpenCl()


for frame in frames:
    frame.wdir = directory
    frame.name = "DebayerTest"

frames[0].name += "_BilinearCython"
frames[1].name += "_BilinearOpenCl"
frames[2].name += "_VNGCython"
frames[3].name += "_VNGOpenCl"

for frame in frames:
    frame.decode()

data = []

t1 = datetime.now()
data.append(bilinearcython.debayer(frames[0].data[0]))
t2 = datetime.now()
data.append(bilinearopencl.debayer(frames[1].data[0]))
t3 = datetime.now()
data.append(vngcython.debayer(frames[2].data[0]))
t4 = datetime.now()
data.append(vngopencl.debayer(frames[3].data[0]))
t5 = datetime.now()


print("Results:")
print("Bilinear Cython: " + str(t2 - t1))
print("Bilinear OpenCl: " + str(t3 - t2))
print("VNG Cython:      " + str(t4 - t3))
print("VNG OpenCl:      " + str(t5 - t4))

print("Data analysis:")
bilineardiff = data[0] - data[1]
vngdiff = data[2] - data[3]

#vngdiff = (vngdiff + np.amin(vngdiff)) / np.amax(vngdiff) * 254
#vngdiff = np.uint8(vngdiff)

print("Bilinear difference:    " + str(np.amax(bilineardiff)) + " and " + str(np.amin(bilineardiff)))
print("VNG difference - red:   " + str(np.amax(vngdiff[0])) + " and " + str(np.amin(vngdiff[0])))
print("VNG difference - green: " + str(np.amax(vngdiff[1])) + " and " + str(np.amin(vngdiff[1])))
print("VNG difference - blue:  " + str(np.amax(vngdiff[2])) + " and " + str(np.amin(vngdiff[2])))
print("VNGOpenCl values:    " + str(np.amax(data[3])) + " and " + str(np.amin(data[3])))

print(vngdiff)

Im.fromarray(vngdiff[0]).save(directory + "vngdiff_r.tiff")
Im.fromarray(vngdiff[1]).save(directory + "vngdiff_g.tiff")
Im.fromarray(vngdiff[2]).save(directory + "vngdiff_b.tiff")