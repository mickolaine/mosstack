__author__ = 'Mikko Laine'
__all__ = ["BilinearCl", "LRPCl", "Bilinear", "VNG", "BilinearCython", "VNGCython"]

try:
    from . import *
    BilinearCl = BilinearCl.BilinearCl
    LRPCl = LRPCl.LRPCl
    VNG = VNG.VNG
except ImportError:
    from . import Bilinear
    from . import BilinearCython
    from . import VNGCython

Bilinear = Bilinear.Bilinear
BilinearCython = BilinearCython.BilinearCython
VNGCython = VNGCython.VNGCython
