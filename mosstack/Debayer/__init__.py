__author__ = 'Mikko Laine'
__all__ = ["BilinearOpenCl", "VNGOpenCl", "BilinearCython", "VNGCython"]

try:
    from . import *
    BilinearOpenCl = BilinearOpenCl.BilinearOpenCl
#    LRPCl = LRPCl.LRPCl
    VNGOpenCl = VNGOpenCl.VNGOpenCl
#    VNGOpenCl_test = VNGOpenCl_test.VNGOpenCl_test
except ImportError:
#    from . import Bilinear
    from . import BilinearCython
    from . import VNGCython

#Bilinear = Bilinear.Bilinear
BilinearCython = BilinearCython.BilinearCython
VNGCython = VNGCython.VNGCython
