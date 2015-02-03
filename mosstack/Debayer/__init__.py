__author__ = 'Mikko Laine'
__all__ = ["BilinearOpenCl", "VNGOpenCl", "BilinearCython", "VNGCython"]

try:
    from . import *
    BilinearOpenCl = BilinearOpenCl.BilinearOpenCl
    VNGOpenCl = VNGOpenCl.VNGOpenCl
#    VNGOpenCl_test = VNGOpenCl_test.VNGOpenCl_test
except ImportError:
    from . import BilinearCython
    from . import VNGCython


BilinearCython = BilinearCython.BilinearCython
VNGCython = VNGCython.VNGCython
