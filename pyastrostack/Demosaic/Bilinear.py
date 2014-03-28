from .. Demosaic.Demosaic import Demosaic
import numpy as np


class Bilinear(Demosaic):
    """
    Demosaicing class. I'll start with regular bilinear interpolation but more will come if necessary

    """

    def __init__(self):
        """Prepare everything for running the demosaic-algorithms."""

    def demosaic(self, image):
        """
        Bilinear interpolation for demosaicing CFA
        Now assumes order of GR
                             BG

        Give cfa-image, receive rgb-image. Return numpy.array
        """

        cfa = np.float32(image)
        r = np.zeros_like(image)
        g = np.zeros_like(image)
        b = np.zeros_like(image)

        for i in range(len(image)):
            for j in range(len(image[i])):
                if i == 0 or i == len(image) - 1 or j == 0 or j == len(image[i]) - 1:      # Border
                    r[i][j] = cfa[i][j]
                    b[i][j] = cfa[i][j]
                    g[i][j] = cfa[i][j]

                elif (i % 2 == 1) & (j % 2 == 1):                                 # At green on red row
                    r[i][j] = (cfa[i][j - 1] + cfa[i][j + 1]) / 2
                    b[i][j] = (cfa[i - 1][j] + cfa[i + 1][j]) / 2
                    g[i][j] = cfa[i][j]

                elif (i % 2 == 0) & (j % 2 == 0):                                 # At green on blue row
                    r[i][j] = (cfa[i - 1][j] + cfa[i + 1][j]) / 2
                    b[i][j] = (cfa[i][j - 1] + cfa[i][j + 1]) / 2
                    g[i][j] = cfa[i][j]
                elif (i % 2 == 1) & (j % 2 == 0):                                 # At red position
                    r[i][j] = cfa[i][j]
                    b[i][j] = (cfa[i - 1][j - 1] + cfa[i - 1][j + 1] + cfa[i + 1][j - 1] + cfa[i + 1][j + 1]) / 4
                    g[i][j] = (cfa[i - 1][j] + cfa[i][j - 1] + cfa[i][j + 1] + cfa[i + 1][j]) / 4

                elif (i % 2 == 0) & (j % 2 == 1):                                 # At blue position
                    r[i][j] = (cfa[i - 1][j - 1] + cfa[i - 1][j + 1] + cfa[i + 1][j - 1] + cfa[i + 1][j + 1]) / 4
                    b[i][j] = cfa[i][j]
                    g[i][j] = (cfa[i - 1][j] + cfa[i][j - 1] + cfa[i][j + 1] + cfa[i + 1][j]) / 4

        return np.array([r, g, b])


