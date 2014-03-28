__author__ = 'Mikko Laine'
__all__ = ["BilinearCl", "LRPCl", "Bilinear", "VNG"]

try:
    from . import *
    BilinearCl = BilinearCl.BilinearCl
    LRPCl = LRPCl.LRPCl
    VNG = VNG.VNG
except ImportError:
    from . import Bilinear

Bilinear = Bilinear.Bilinear
