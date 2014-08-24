"""
PyQt4 specific class. Program will run just fine on command line without PyQt but GUI requires it.
"""

from . Frame import Frame


class QFrame(Frame):
    """
    QFrame is a variation of Frame class intended for PyQt4 gui. It inherits Frame, which represents one photo frame.
    This class holds everything specific to GUI and it's use requires PyQt4.
    """

    def __init__(self, project=None, rawpath=None, infopath=None, ftype="light", number=None, fphase="orig"):
        """

        """
        super(QFrame, self).__init__(project=project,
                                     rawpath=rawpath,
                                     infopath=infopath,
                                     ftype=ftype,
                                     number=number,
                                     fphase=fphase)

    def update_ui(self):
        """
        Tell the user interface that something has changed and state of this object needs to be read again
        """
        pass


