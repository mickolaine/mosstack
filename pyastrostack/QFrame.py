"""
PyQt4 specific class. Program will run just fine on command line without PyQt but GUI requires it.
"""

from . Frame import Frame


class QFrame(Frame):
    """
    QFrame is a variation of Frame class intended for PyQt4 gui. It inherits Frame, which represents one photo frame.
    This class holds everything specific to GUI and it's use requires PyQt4.
    """

    def __init__(self, rawpath=None, infopath=None):
        """

        """
        super(QFrame, self).__init__(rawpath=rawpath, infopath=infopath)

        self.status = {         # Status of the process
            "prepare": 0,       # 0 = not started
            "calibrate": 0,     # 1 = under process
            "debayer": 0,       # 2 = done
            "register": 0       # -1 = failed
        }

    def prepare(self):
        """
        Prepare the frame.

        Returns signal or something where Gui knows to update itself

        1. Check if there already is an .info file
            1.1. Check if everything .info file says is really done and found
            1.2. Update all variables to match .info's state
            1.3. Inform Gui to update itself
        2. Decode raw to FITS
        3. Read raw's properties (dimensions, bayer filter...)
        4. Write everything to .info
        5. Inform Gui that status has changed
        """
        self.status["prepare"] = 1

        if not Frame.checkraw(self.rawpath):
            self.status["prepare"] = -1
            return

        self.status["prepare"] = 2

        return

    def calibrate(self):
        """
        Calibrate the frame. Project tells how.

        All stages are optional except the last one
        1. Subtract master bias
        2. Subtract master dark
        3. Divide with master flat
        4. Inform Gui that status has changed
        """

        self.status["calibrate"] = 1
        pass  # Here's da magick

        self.status["calibrate"] = 2

        return

    def debayer(self):
        """
        Debayer the frame. Project tells how.

        1. Check what Debayer function to use
        2. Do the thing
        3. Inform Gui that status has changed
        """

        self.status["debayer"] = 1
        pass
        self.status["debayer"] = 2

        return

    def register(self):
        """
        Register the frame. Project tells how.

        1. Step 1
        2. Check if reference frame.
            2.(If)   Copy file
            2.(Else) Step 2
        3. Inform Gui that status has changed
        """

        self.status["register"] = 1

        pass

        self.status["register"] = 2

        return