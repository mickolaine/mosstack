#__all__ = ["Groth_ImageMagick", "Groth_Skimage", "Groth", "SkTransform"]
__all__ = ["Groth", "SkTransform", "ImTransform"]
matcher = ["Groth"]
transformer = ["SkTransform"]

from . import *

#Groth_ImageMagick = Groth_ImageMagick.Groth_ImageMagick
#Groth_Skimage = Groth_Skimage.Groth_Skimage
Groth = Groth.Groth
SkTransform = SkTransform.SkTransform
#ImTransform = ImTransform.ImTransform
