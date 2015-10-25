__author__ = 'Mikko Laine'
__all__ = ["BilinearOpenCl", "VNGOpenCl", "BilinearCython", "VNGCython", "VNGC"]

try:
    from . import *
    BilinearOpenCl = BilinearOpenCl.BilinearOpenCl
    VNGOpenCl = VNGOpenCl.VNGOpenCl
except ImportError:
    from . import BilinearOpenCl
    from . import VNGOpenCl
    from . import BilinearCython
    from . import VNGCython
    from . import VNGC


BilinearCython = BilinearCython.BilinearCython
VNGCython = VNGCython.VNGCython
VNGC = VNGC.VNGC
VNGOpenCl = VNGOpenCl
BilinearOpenCl = BilinearOpenCl