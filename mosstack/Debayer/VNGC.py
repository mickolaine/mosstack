from __future__ import division
from .. Debayer.Debayer import Debayer
from .. Debayer import debayer


class VNGC(Debayer):
    """
    Debayering class.

    """

    def __init__(self):
        """Prepare everything for running the debayer-algorithms."""

    def debayer(self, image):
        """

        """

        debayer.debayer(image.getpath(), image.getpath(fphase="rgb"))
