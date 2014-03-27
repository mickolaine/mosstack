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

        r = np.zeros_like(image)
        g = np.zeros_like(image)
        b = np.zeros_like(image)
        cfa = np.flipud(image)

        # Green pixels are interpolated first
        for i in range(len(image)):
            for j in range(len(image[i])):
                if i == 0 or i == len(image) - 1 or j == 0 or j == len(image[i]) - 1:
                    g[i][j] = cfa[i][j]
                elif ((i % 2 == 0) & (j % 2 == 1)) or ((i % 2 == 1) & (j % 2 == 0)):     # Test, when non-green pixel
                    g[i][j] = (cfa[i - 1][j] + cfa[i][j - 1] + cfa[i][j + 1] + cfa[i + 1][j]) / 4
                else:                                                                           # For the green pixels
                    g[i][j] = cfa[i][j]

        for i in range(len(image)):
            for j in range(len(image[i])):
                if i == 0 or i == len(image) - 1 or j == 0 or j == len(image[i]) - 1:
                    r[i][j] = cfa[i][j]
                    b[i][j] = cfa[i][j]
                elif (i % 2 == 0) & (j % 2 == 0):                                 # At green on red row
                    r[i][j] = (cfa[i][j - 1] + cfa[i][j + 1]) / 2
                    b[i][j] = (cfa[i - 1][j] + cfa[i + 1][j]) / 2
                elif (i % 2 == 1) & (j % 2 == 1):                                 # At green on blue row
                    r[i][j] = (cfa[i - 1][j] + cfa[i + 1][j]) / 2
                    b[i][j] = (cfa[i][j - 1] + cfa[i][j + 1]) / 2
                elif (i % 2 == 0) & (j % 2 == 1):                                 # At red position
                    r[i][j] = cfa[i][j]
                    b[i][j] = (cfa[i - 1][j - 1] + cfa[i - 1][j + 1] + cfa[i + 1][j - 1] + cfa[i + 1][j + 1]) / 4
                elif (i % 2 == 1) & (j % 2 == 0):                                 # At blue position
                    r[i][j] = (cfa[i - 1][j - 1] + cfa[i - 1][j + 1] + cfa[i + 1][j - 1] + cfa[i + 1][j + 1]) / 4
                    b[i][j] = cfa[i][j]

        return np.array([r, g, b])


