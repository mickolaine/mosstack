from __future__ import division
from .. Debayer.Debayer import Debayer
from .. Debayer import debayer
from os.path import exists
from os import remove


class VNGC(Debayer):
    """
    Debayering class.

    """

    def __init__(self):
        """Prepare everything for running the debayer-algorithms."""

    def debayer(self, image):
        """
        Debayer using C-subroutine

        None should be returned
        """

        outname = image.getpath(fphase="rgb")

        # CFITSIO fails writing the file if it exists. Remove if necessary
        if exists(outname):
            remove(outname)

        return debayer.debayer(image.getpath(), outname)
