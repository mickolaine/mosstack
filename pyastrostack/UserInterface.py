"""
Classes related to user interface. Main program "AstroStack.py" parses the input (at least for now), but
this file controls all the actions after that.
"""

import Conf
from Photo import Photo, Batch
import Registering
import Demosaic
import Stacker

__author__ = 'Mikko Laine'


class UserInterface:
    """

    """

    setup = Conf.Setup()

    shorthelp = """
    pyAstroStack is run with:
    AstroStack.py <operation> <projectfile> <arguments>

    <operation>   - init, adddir, addfile, ... Try AstroStack help for full list
    <projectname> - File in configured working directory. Type the name without extension
    <arguments>   - Depends on <operation>
    """
    """
    String to print when program run with no parameters or false parameters.
    """


    longhelp = shorthelp
    """
    String to print when program run with 'help' parameter. Will include short explanations on every
    command line argument available.

    For now is just a copy of shorthelp.
    """

    def __init__(self, project=None):
        """

        """
        self.project = project

    def setproject(self, project):
        """

        """
        self.project = project

    def register(self, section):
        """
        Register project files under specified section.
        """

        batch = Batch(section=section, project=self.project)
        batch.register(Registering.Sextractor())

    def demosaic(self, section):
        """
        Demosaic project files under specified section. Use demosaicing algorithm TODO:
        """

        batch = Batch(section=section, project=self.project)
        batch.demosaic(Demosaic.LRPCl())

    def stack(self, section):
        """
        Stack project files under specified section. Stacker read from TODO: do this
        """

        batch = Batch(section=section, project=self.project)
        batch.stack(Stacker.Median())

    def subtract(self, section, calib):
        """
        Subtract calibration frame from main frame or frames.

        Arguments:
        section - section code or name for master frame (light, dark, flat, bias)
        calib - name for master frame (dark, bias)
        """

        batch = Batch(section=section, project=self.project)
        batch.subtract(calib, Stacker.Mean())

    def divide(self, section, calib):
        """
        Divide main frame with calibration frame.

        Arguments:
        section - section code or name for master frame
        calib - name for master frame (most likely flat)
        """

        batch = Batch(section=section, project=self.project)
        batch.divide(calib, Stacker.Mean())