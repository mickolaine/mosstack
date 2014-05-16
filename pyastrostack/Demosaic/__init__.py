__author__ = 'Mikko Laine'
__all__ = ["BilinearCl", "LRPCl", "Bilinear", "VNGCl", "BilinearCython", "VNGCython"]

try:
    from . import *
    BilinearCl = BilinearCl.BilinearCl
#    LRPCl = LRPCl.LRPCl
    VNGCl = VNGCl.VNGCl
except ImportError:
#    from . import Bilinear
    from . import BilinearCython
    from . import VNGCython

#Bilinear = Bilinear.Bilinear
BilinearCython = BilinearCython.BilinearCython
VNGCython = VNGCython.VNGCython
