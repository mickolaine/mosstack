from __future__ import division
from subprocess import call
from re import sub
from shutil import copyfile


class ImTransform(object):

    @staticmethod
    def affine_transform(image, ref):
        """
        Transforms image according to image.pairs.

        Transformation is done with ImageMagick's "convert -distort Affine" from command line.
        New image will have genname "reg".

        Arguments:
        image - Frame type object to transform
        ref - Number for reference image
        """

        if sub("\D", "", image.number) == ref:  # For RGB-images i.number holds more than number. Strip that
            print("Not transforming the reference frame.")
            oldpath = image.path
            image.genname = "reg"
            newpath = image.path
            copyfile(oldpath, newpath)
            return

        # Preparations. Create string of coordinate pairs the way ImageMagick wants it
        if image.points is None or True:
            points = "'"
            n = 0
            for i in image.pairs:
                if n > 12:          # max number of control points is 12
                    break
                points = points + "{},{},{},{} ".format(int(i[0][0]), image.y - int(i[0][1]),
                                                        int(i[1][0]), image.y - int(i[1][1]))
                n += 1
            points += "'"
            image.points = points
        else:
            points = image.points

        print("Starting affine transform for frame number " + image.number)
        # Actual transforming
        image.write_tiff()
        oldpath = image.rgbpath(fileformat="tiff")
        image.genname = "reg"
        newpath = image.rgbpath()
        if len(oldpath) == 3:
            for i in [0, 1, 2]:
                command = "convert " + oldpath[i] + " -distort Affine " + points + " " + newpath[i]
                call([command], shell=True)
                call(["rm " + oldpath[i]], shell=True)

        else:
            command = "convert " + oldpath + " -distort Affine " + points + " " + newpath
            call([command], shell=True)
            call(["rm " + oldpath], shell=True)

        image.combine(newpath)
        print("Done")