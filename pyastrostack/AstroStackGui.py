"""
Graphical user interface for pyAstroStack. This file holds all the functionality for GUI drafted in Qt Designer.
"""

from PyQt4.QtCore import QAbstractTableModel, Qt
from PyQt4.QtGui import QFileDialog, qApp, QInputDialog
from . UiDesign import Ui_MainWindow
from . Config import Project, Setup
from . Photo import Batch
from . import Registering
from . import Demosaic
from . import Stacker
try:
    from PyQt4.QtCore import Qstring
    _fromUtf8 = QString.fromUtf8
except ImportError:
    def _fromUtf8(s):
        return s


class Ui(Ui_MainWindow):

    def __init__(self):
        super(Ui, self).__init__()

    def setupMoar(self, MainWindow):
        """
        Add things I don't know how to add with Qt Designer
        """

        self.setup = Setup()

        #Menu
        self.actionNew_project.triggered.connect(self.newProject)
        self.actionOpen_project.triggered.connect(self.loadProject)
        self.actionSave_project.triggered.connect(self.saveProject)
        self.actionExit.triggered.connect(qApp.quit)

        self.pushLight.clicked.connect(self.addLight)
        self.pushDark.clicked.connect(self.addDark)
        self.pushFlat.clicked.connect(self.addFlat)
        self.pushBias.clicked.connect(self.addBias)
        self.pushButtonRun.clicked.connect(self.runProgram)

        self.buttonDebayer.setExclusive(True)
        self.buttonRegister.setExclusive(True)
        self.buttonStack.setExclusive(True)

        self.setValues()
        self.fileDialog = QFileDialog()
        self.inputDialog = QInputDialog()

        self.framearray = []

    def setValues(self, values=None):
        """
        Set the values for checkboxes.

        Arguments
        values - dict of values to check, use defaults if not given

        Note to self: 0 is unchecked, 2 is checked. 1 is partially checked which is not needed
        """
        if values is None:
            values = {"DB": 0,
                      "FB": 2,
                      "FD": 0,
                      "LB": 2,
                      "LD": 0,
                      "LF": 2,
                      "calib": 2,
                      "debayer": 2,
                      "reg": 2,
                      "stack": 2,
                      "VC": 2,
                      "GSK": 2,
                      "SM": 2
            }

        self.checkBoxDarkBias.setCheckState(values["DB"])
        self.checkBoxFlatBias.setCheckState(values["FB"])
        self.checkBoxFlatDark.setCheckState(values["FD"])
        self.checkBoxLightBias.setCheckState(values["LB"])
        self.checkBoxLightDark.setCheckState(values["LD"])
        self.checkBoxLightFlat.setCheckState(values["LF"])

        self.checkBoxCalib.setCheckState(values["calib"])
        self.checkBoxDebayer.setCheckState(values["debayer"])
        self.checkBoxReg.setCheckState(values["reg"])
        self.checkBoxStack.setCheckState(values["stack"])

        self.radioButtonVNGCyt.setChecked(values["VC"])
        self.radioButtonGrothSK.setChecked(values["GSK"])
        self.radioButtonSMedian.setChecked(values["SM"])

    def loadProject(self):
        self.pfile = self.fileDialog.getOpenFileName(caption="Open project",
                                                     directory=self.setup.get("Default", "Path"),
                                                     filter="Project files (*.project)")
        self.project = Project(self.pfile)
        self.setProjectName(self.project.get("Default", "Project name"))

        try:
            self.setValues(self.project.get("GUI", "Values"))
        except KeyError:
            self.setValues()

    def saveProject(self):
        pass

    def newProject(self):
        self.pname, ok = self.inputDialog.getText(self.inputDialog, "New project", "Type name for the new project:")

        if not ok:
            return
        if self.pname == "":
            return

        self.setProjectName(str(self.pname))
        self.project = Project(self.pname)
        self.setValues()
        self.framearray = []
        tablemodel = FrameTableModel(self.framearray)
        self.tableView.setModel(tablemodel)

    def setProjectName(self, pname):
        self.projectName.setText(_fromUtf8(pname))

    def addLight(self):
        files = QFileDialog.getOpenFileNames(caption="Select files",
                                             filter="Raw photos (*.CR2 *.cr2)")
        self.lightfiles = files
        self.addFrame(files, "light")

    def addDark(self):
        files = QFileDialog.getOpenFileNames(caption="Select files",
                                             filter="Raw photos (*.CR2 *.cr2)")
        self.darkfiles = files
        self.addFrame(files, "dark")

    def addFlat(self):
        files = QFileDialog.getOpenFileNames(caption="Select files",
                                             filter="Raw photos (*.CR2 *.cr2)")
        self.flatfiles = files
        self.addFrame(files, "flat")

    def addBias(self):
        files = QFileDialog.getOpenFileNames(caption="Select files",
                                             filter="Raw photos (*.CR2 *.cr2)")
        self.biasfiles = files
        self.addFrame(files, "bias")

    def addFrame(self, files, itype):

        for i in files:
            self.framearray.append([i, itype])
        tablemodel = FrameTableModel(self.framearray)
        self.tableView.setModel(tablemodel)

    def runProgram(self):
        """

        """
        self.light = Batch(self.project, "light")
        self.light.addfiles(self.lightfiles, "light")

        if self.checkBoxCalib.isChecked():
            self.runCalib()
        if self.checkBoxDebayer.isChecked():
            self.runDebayer()
        if self.checkBoxReg.isChecked():
            self.runRegister()
        if self.checkBoxStack.isChecked():
            self.runStack()

    def runCalib(self):

        if self.checkBoxDarkBias.isChecked() or self.checkBoxFlatBias.isChecked():
            self.bias = Batch(self.project, "bias")
            self.bias.addfiles(self.biasfiles, "bias")
            self.bias.stack(self.stackingwrap)

        if self.checkBoxDarkBias.isChecked():
            self.dark = Batch(self.project, "dark")
            self.dark.addfiles(self.biasfiles, "dark")
            self.dark.subtract("bias", self.stackingwrap)
            self.dark.stack(self.stackingwrap)

        if self.checkBoxFlatBias.isChecked() or self.checkBoxFlatDark.isChecked():
            self.flat = Batch(self.project, "flat")
            self.flat.addfiles(self.biasfiles, "flat")
            if self.checkBoxFlatBias.isChecked():
                self.flat.subtract("bias", self.stackingwrap)
            if self.checkBoxFlatDark.isChecked():
                self.flat.subtract("dark", self.stackingwrap)

        if self.checkBoxLightBias.isChecked():
            self.light.subtract("bias", self.stackingwrap)
        if self.checkBoxLightDark.isChecked():
            self.light.subtract("dark", self.stackingwrap)
        if self.checkBoxLightFlat.isChecked():
            self.light.divide("flat", self.stackingwrap)

    def runDebayer(self):

        if self.buttonDebayer.checkedButton().text() == "VNG Cython":
            self.demosaicwrap = Demosaic.VNGCython
        elif self.buttonDebayer.checkedButton().text() == "Bilinear Cython":
            self.demosaicwrap = Demosaic.BilinearCython
        elif self.buttonDebayer.checkedButton().text() == "VNG OpenCL":
            self.demosaicwrap = Demosaic.VNG
        elif self.buttonDebayer.checkedButton().text() == "Bilinear OpenCL":
            self.demosaicwrap = Demosaic.BilinearCl

        self.light.demosaic(self.demosaicwrap)

    def runRegister(self):
        if self.buttonRegister.checkedButton().text() == self.radioButtonGrothIM.text():
            self.registerwrap = Registering.Groth_ImageMagick
        elif self.buttonRegister.checkedButton().text() == self.radioButtonGrothSK.text():
            self.registerwrap = Registering.Groth_Skimage
        elif self.buttonRegister.checkedButton().text() == self.radioButtonLegacy.text():
            self.registerwrap = Registering.Sextractor2

        self.light.register(self.registerwrap)

    def runStack(self):
        if self.buttonStack.checkedButton().text() == self.radioButtonMean.text():
            self.stackingwrap = Stacker.Mean
        elif self.buttonStack.checkedButton().text() == self.radioButtonMedian.text():
            self.stackingwrap = Stacker.Median
        elif self.buttonStack.checkedButton().text() == self.radioButtonSMedian.text():
            self.stackingwrap = Stacker.SigmaMedian
        elif self.buttonStack.checkedButton().text() == self.radioButtonSClip.text():
            self.stackingwrap = Stacker.SigmaClip

        self.light.stack(self.stackingwrap)


class FrameTableModel(QAbstractTableModel):
    def __init__(self, datain, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        if len(self.arraydata) == 0:
            return 0
        return len(self.arraydata[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.arraydata[index.row()][index.column()]


class Configurator():
    """
    This class handles saved projects and relaying configurations and parameters from Gui to core.
    """

    def __init__(self, pfile=None):
        self.project = Project(pfile)
        pass

    @staticmethod
    def loadConfig(pfile):
        return Configurator(pfile=pfile)

    def get(self, section, key):
        return self.project.get(section, key)

    def runProgram(self):
        """
        Parse settings and run the program
        """
