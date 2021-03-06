from __future__ import division
import numpy as np
from skimage import transform as tf


class SkTransform(object):
    """
    Affine transformation calculations and the transformation itself. Contains static methods and should be used
    as a static class.
    """

    @staticmethod
    def calculate_transform(frame):
        """
        Calculates affine transformation.

        Write result to frame.tform
        """
        if frame.isref:
            print("No need to calculate for reference frame.")
            return

        print("Starting affine transform for frame number " + frame.number)
        primary = []
        secondary = []
        m = 0

        for i in frame.pairs:
            if m > 11 or i[2] < 20:
                break
            #primary.append([i[0][0], i[0][1], 0])
            #secondary.append([i[1][0], i[1][1], 0])
            primary.append([i[0][0], i[0][1]])
            secondary.append([i[1][0], i[1][1]])
            m += 1
        primary = np.squeeze(np.array(primary))
        secondary = np.squeeze(np.array(secondary))

        try:
            frame.tform = tf.estimate_transform(ttype="affine", src=secondary, dst=primary)
        except IndexError:
            pass

    @staticmethod
    def affine_transform(frame):
        """
        Do the affine transformation

        Return transformed data. For the reference image return data itself.
        """

        if frame.isref:
            print("Copying the reference frame.")

            return frame.data

        imagedata = np.float64(frame.data)
        data = []
        for i in range(len(imagedata)):
            amax = np.amax(imagedata[i])
            #data.append(tf.warp(np.int32(imagedata[i] / np.amax(imagedata[i])), inverse_map=frame.tform))
            data.append(tf.warp(imagedata[i] / np.amax(imagedata[i]), inverse_map=frame.tform))
            data[i] /= np.amax(data[i]) / amax

        return np.array(data)


    '''
    @staticmethod
    def affine_transform(image, ref):
        """
        Transforms image according to image.pairs.

        Arguments:
        image - Frame type object to transform
        ref - Number for reference image
        """

        if sub("\D", "", image.number) == ref:  # For RGB-images i.number holds more than number. Strip that
            print("Not transforming the reference frame.")
            oldpath = image.path()
            image.genname = "reg"
            newpath = image.path()
            copyfile(oldpath, newpath)
            return

        print("Starting affine transform for frame number " + image.number)
        primary = []
        secondary = []
        m = 0
        for i in image.pairs:
            if m > 11 or i[2] < 20:
                break
            #print(i)
            primary.append([i[0][0], i[0][1], 0])
            secondary.append([i[1][0], i[1][1], 0])
            m += 1
        primary = np.array(primary)
        secondary = np.array(secondary)

        tform = tf.estimate_transform(ttype="affine", dst=primary, src=secondary)
        imagedata = image.data

        data = []

        for i in range(len(imagedata)):
            amax = np.amax(imagedata[i])
            data.append(tf.warp(np.float32(imagedata[i])/np.amax(imagedata[i]), inverse_map=tform))
            data[i] /= np.amax(data[i])/amax
            #print("Minime " + str(np.amin(imagedata[i])) + " ja " + str(np.amin(data[i])))
            #print("Maxime "+ str(np.amax(imagedata[i])) + " ja " + str(np.amax(data[i])))
        data = np.array(data)

        image.genname = "reg"
        image.data = data
        image.write()
        del data
        print("Done")

    @staticmethod
    def affine_transform3(image, ref):
        """
        Transforms image according to image.pairs.

        Arguments:
        image - Frame type object to transform
        ref - Number for reference image
        """

        if str(image.number) == str(ref.number):  # For RGB-images i.number holds more than number. Strip that
            print("Not transforming the reference frame.")
            oldpath = image.path()
            image.genname = "reg"
            newpath = image.path()
            copyfile(oldpath, newpath)
            return

        print("Starting affine transform for frame number " + image.number)
        primary = []
        secondary = []
        m = 0

        for i in image.pairs:
            if m > 11 or i[2] < 20:
                break
            #print(i)
            primary.append([i[0][0], i[0][1], 0])
            secondary.append([i[1][0], i[1][1], 0])
            m +=1
        primary = np.array(primary)
        secondary = np.array(secondary)

        try:
            tform = tf.estimate_transform(ttype="affine", dst=primary, src=secondary)
        except IndexError:
            pass

        imagedata = image.data
        data = []
        for i in range(len(imagedata)):
            amax = np.amax(imagedata[i])
            data.append(tf.warp(np.float32(imagedata[i])/np.amax(imagedata[i]), inverse_map=tform))
            data[i] /= np.amax(data[i])/amax
            #print("Minime " + str(np.amin(imagedata[i])) + " ja " + str(np.amin(data[i])))
            #print("Maxime "+ str(np.amax(imagedata[i])) + " ja " + str(np.amax(data[i])))

        return np.array(data)

    @staticmethod
    def affine_transform2(image):
        """
        Transforms image according to image.pairs.

        Arguments:
        image - Frame type object to transform
        """

        matrix = SkTransform.solve_matrix(image.pairs)
        t1 = datetime.datetime.now()
        print(matrix[:2,:2])
        print(matrix[3,0:2])
        print(image.x)
        offset_matrix = [-matrix[3,1], -matrix[3,0]]
        print(offset_matrix)
        data = np.array([affine_transform(image.data[0], matrix[:2,:2], offset=offset_matrix),
                         affine_transform(image.data[1], matrix[:2,:2], offset=offset_matrix),
                         affine_transform(image.data[2], matrix[:2,:2], offset=offset_matrix)])
        t2 = datetime.datetime.now()
        print("Affine transforming took " + str(t2 - t1) + " seconds.")

        image.genname = "reg"
        image.data = data
        image.write()

    @staticmethod
    def solve_matrix(pairs):
        """
        http://stackoverflow.com/questions/20546182/how-to-perform-coordinates-affine-transformation-using-python-part-2
        """
        primary = []
        secondary = []
        m = 0
        for i in pairs:
            if m > 11 or i[2] < 20:
                break
            print(i)
            primary.append([i[0][0], i[0][1], 0])
            secondary.append([i[1][0], i[1][1], 0])
            m +=1
        primary = np.array(primary)
        secondary = np.array(secondary)
        for i in range(len(primary)):
            print(primary[i])
            print(secondary[i])

        n = primary.shape[0]
        pad = lambda x: np.hstack([x, np.ones((x.shape[0], 1))])
        unpad = lambda x: x[:,:-1]
        X = pad(primary)
        Y = pad(secondary)

        # Solve the least squares problem X * A = Y
        # to find our transformation matrix A
        A, res, rank, s = np.linalg.lstsq(X, Y)

        #transform = lambda x: unpad(np.dot(pad(x), A))

        print(A)

        #return A[:2,:2]
        return A
    '''