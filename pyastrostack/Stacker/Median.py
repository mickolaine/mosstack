"""

"""

__author__ = 'Mikko Laine'


from .. Stacker.Stacking import Stacking
import numpy as np
import gc


class Median(Stacking):
    """
    Each pixel will be a median value of the entire stack.
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def stack(imagelist, project):
        """
        Stack the list of images using median value for every subpixel of every colour
        """
        print("Beginning median stack...")
        rlist = []
        glist = []
        blist = []

        print("Loading images in memory...")
        for i in imagelist:
            if imagelist[i].rgb:
                rgb = True
                for i in imagelist:
                    imagelist[i].load_data()
                    rlist.append(imagelist[i].data[0])
                    glist.append(imagelist[i].data[1])
                    blist.append(imagelist[i].data[2])
                    imagelist[i].release()
                    gc.collect()
            else:
                rgb = False
                for i in imagelist:
                    imagelist[i].load_data()
                    rlist.append(imagelist[i].data)
                    imagelist[i].release()
                    gc.collect()
            break

        print("Done!")
        print("Calculating the median. This might take a while...")
        r = np.median(rlist, axis=0)
        del rlist
        gc.collect()
        if rgb:
            g = np.median(glist, axis=0)
            del glist
            gc.collect()
            b = np.median(blist, axis=0)
            del blist
            gc.collect()
        print("Calculating done!")
        if rgb:
            return np.array([r, g, b])
        else:
            return r
