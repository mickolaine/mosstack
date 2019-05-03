from __future__ import division
from subprocess import call
from shutil import copyfile


class ImTransform(object):

    @staticmethod
    def calculate_transform(frame):
        """
        Calculates affine transformation. Actually does nothing since all the work is in affine_transform. Exists for
        compability reasons.
        """

    @staticmethod
    def affine_transform(frame):
        """
        Transforms image according to frame.pairs.

        Transformation is done with ImageMagick's "convert -distort Affine" from command line.
        New image will have genname "reg".

        Arguments:
        frame - Frame type object to transform
        ref - Number for reference image
        """

        if frame.isref:
            print("Not transforming the reference frame.")
            oldpath = frame.path()
            frame.genname = "reg"
            newpath = frame.path()
            copyfile(oldpath, newpath)
            return None

        # Preparations. Create string of coordinate pairs the way ImageMagick wants it
        if frame.points is None or True:
            points = "'"
            n = 0
            for i in frame.pairs:
                if n > 12:          # max number of control points is 12
                    break
                points = points + "{},{},{},{} ".format(int(i[0][0]), frame.y - int(i[0][1]),
                                                        int(i[1][0]), frame.y - int(i[1][1]))
                n += 1
            points += "'"
            frame.points = points
        else:
            points = frame.points

        print("Starting affine transform for frame number " + frame.number)
        # Actual transforming
        frame.write_tiff()
        oldpath = frame.rgbpath(fileformat="tiff")
        frame.genname = "reg"
        newpath = frame.rgbpath()
        if len(oldpath) == 3:
            for i in [0, 1, 2]:
                command = "convert " + oldpath[i] + " -distort Affine " + points + " " + newpath[i]
                call([command], shell=True)
                call(["rm " + oldpath[i]], shell=True)

        else:
            command = "convert " + oldpath + " -distort Affine " + points + " " + newpath
            call([command], shell=True)
            call(["rm " + oldpath], shell=True)

        frame.combine(newpath)
        print("Done")
        return None