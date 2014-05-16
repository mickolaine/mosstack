"""
Graphical user interface for pyAstroStack. This file holds all the functionality for GUI drafted in Qt Designer.
"""

from PyQt4.QtCore import QAbstractTableModel, Qt
from PyQt4.QtGui import QFileDialog, qApp, QInputDialog, QProgressDialog
from ast import literal_eval
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
        self.batch = {}

    def setValues(self, values=None):
        """
        Set the values for checkboxes.

        Arguments
        values - dict of values to check, use defaults if not given

        Note to self: 0 is unchecked, 2 is checked. 1 is partially checked which is not needed
        """
        if values is None:
            values = {"CalibDarkBias": 0,
                      "CalibFlatBias": 2,
                      "CalibFlatDark": 0,
                      "CalibLightBias": 2,
                      "CalibLightDark": 0,
                      "CalibLightFlat": 2,
                      "Calibrate": 2,
                      "Debayer": 2,
                      "Register": 2,
                      "Stack": 2,
                      "BilinearCython": 0,
                      "VNGCython": 2,
                      "BilinearCL": 0,
                      "VNGCL": 0,
                      "GrothIM": 0,
                      "GrothSK": 2,
                      "Legacy": 0,
                      "Mean": 0,
                      "Median": 0,
                      "SigmaMedian": 2,
                      "SigmaClip": 0
            }

        self.checkBoxDarkBias.setCheckState(values["CalibDarkBias"])
        self.checkBoxFlatBias.setCheckState(values["CalibFlatBias"])
        self.checkBoxFlatDark.setCheckState(values["CalibFlatDark"])
        self.checkBoxLightBias.setCheckState(values["CalibLightBias"])
        self.checkBoxLightDark.setCheckState(values["CalibLightDark"])
        self.checkBoxLightFlat.setCheckState(values["CalibLightFlat"])

        self.checkBoxCalib.setCheckState(values["Calibrate"])
        self.checkBoxDebayer.setCheckState(values["Debayer"])
        self.checkBoxReg.setCheckState(values["Register"])
        self.checkBoxStack.setCheckState(values["Stack"])

        self.radioButtonBilinearCyt.setChecked(values["BilinearCython"])
        self.radioButtonVNGCyt.setChecked(values["VNGCython"])
        self.radioButtonBilinearCL.setChecked(values["BilinearCL"])
        self.radioButtonVNGCL.setChecked(values["VNGCL"])

        self.radioButtonGrothIM.setChecked(values["GrothIM"])
        self.radioButtonGrothSK.setChecked(values["GrothSK"])
        self.radioButtonLegacy.setChecked(values["Legacy"])

        self.radioButtonMean.setChecked(values["Mean"])
        self.radioButtonMedian.setChecked(values["Median"])
        self.radioButtonSMedian.setChecked(values["SigmaMedian"])
        self.radioButtonSClip.setChecked(values["SigmaClip"])

    def getValues(self):
        """
        Return dict of values according to checkboxes and radio buttons
        """
        values = {"CalibDarkBias": self.checkBoxDarkBias.checkState(),
                  "CalibFlatBias": self.checkBoxFlatBias.checkState(),
                  "CalibFlatDark": self.checkBoxFlatDark.checkState(),
                  "CalibLightBias": self.checkBoxLightBias.checkState(),
                  "CalibLightDark": self.checkBoxLightDark.checkState(),
                  "CalibLightFlat": self.checkBoxLightFlat.checkState(),
                  "Calibrate": self.checkBoxCalib.checkState(),
                  "Debayer": self.checkBoxDebayer.checkState(),
                  "Register": self.checkBoxReg.checkState(),
                  "Stack": self.checkBoxStack.checkState(),
                  "BilinearCython": self.radioButtonBilinearCyt.isChecked(),
                  "VNGCython": self.radioButtonVNGCyt.isChecked(),
                  "BilinearCL": self.radioButtonBilinearCL.isChecked(),
                  "VNGCL": self.radioButtonVNGCL.isChecked(),
                  "GrothIM": self.radioButtonGrothIM.isChecked(),
                  "GrothSK": self.radioButtonGrothSK.isChecked(),
                  "Legacy": self.radioButtonLegacy.isChecked(),
                  "Mean": self.radioButtonMean.isChecked(),
                  "Median": self.radioButtonMedian.isChecked(),
                  "SigmaMedian": self.radioButtonSMedian.isChecked(),
                  "SigmaClip": self.radioButtonSClip.isChecked()
                  }
        return values

    def loadProject(self):
        self.pfile = self.fileDialog.getOpenFileName(caption="Open project",
                                                     directory=self.setup.get("Default", "Path"),
                                                     filter="Project files (*.project)")
        self.project = Project.load(self.pfile)
        self.setProjectName(self.project.get("Default", "Project name"))

        try:
            self.setValues(literal_eval(self.project.get("GUI", "Values")))
        except KeyError:
            self.setValues()

        for i in ("light", "dark", "bias", "flat"):
            try:
                files = self.project.get(i)
                files = list(files.values())
                self.batch[i] = Batch(self.project, i)
                self.batch[i].addfiles(files, i)
                self.addFrame(files, i)
            except:
                pass

    def saveProject(self):
        self.project.set("GUI", "Values", str(self.getValues()))

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
        """
        Wrapper to add light files. TODO: better solution
        """
        files = QFileDialog.getOpenFileNames(caption="Select files",
                                             filter="Raw photos (*.CR2 *.cr2)")
        self.lightfiles = files
        self.addFrame(files, "light")

    def addDark(self):
        """
        Wrapper to add dark files. TODO: better solution
        """
        files = QFileDialog.getOpenFileNames(caption="Select files",
                                             filter="Raw photos (*.CR2 *.cr2)")
        self.darkfiles = files
        self.addFrame(files, "dark")

    def addFlat(self):
        """
        Wrapper to add flat files. TODO: better solution
        """
        files = QFileDialog.getOpenFileNames(caption="Select files",
                                             filter="Raw photos (*.CR2 *.cr2)")
        self.flatfiles = files
        self.addFrame(files, "flat")

    def addBias(self):
        """
        Wrapper to add bias files. TODO: better solution
        """
        files = QFileDialog.getOpenFileNames(caption="Select files",
                                             filter="Raw photos (*.CR2 *.cr2)")
        self.biasfiles = files
        self.addFrame(files, "bias")

    def addFrame(self, files, itype):
        """
        Add files to frame list and batches. Create batches if they don't already exist.
        """

        progress = QProgressDialog()
        progress.show()
        progress.setMinimum(0)
        progress.setMaximum(len(files))
        n = 0
        for i in files:
            progress.setValue(n)
            # If batch does not exist, create one
            if itype not in self.batch:
                self.batch[itype] = Batch(self.project, itype)

            # Add files
            self.batch[itype].addfile(i, itype)

            # Add files to framearray
            self.framearray.append([i, itype])
            n += 1
            progress.update()

        tablemodel = FrameTableModel(self.framearray)
        self.tableView.setModel(tablemodel)
        self.tableView.resizeColumnsToContents()
        self.tableView.resizeRowsToContents()
        #progress.hide()

    def runProgram(self):
        """

        """
        #self.light = Batch(self.project, "light")
        #self.light.addfiles(self.lightfiles, "light")

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
            #self.bias = Batch(self.project, "bias")
            #self.bias.addfiles(self.biasfiles, "bias")
            self.batch["bias"].stack(Stacker.Mean())

        if self.checkBoxDarkBias.isChecked():
            #self.dark = Batch(self.project, "dark")
            #self.batch["dark"].addfiles(self.darkfiles, "dark")
            self.batch["dark"].subtract("bias", Stacker.Mean())
            self.batch["dark"].stack(Stacker.Mean())

        if self.checkBoxFlatBias.isChecked() or self.checkBoxFlatDark.isChecked():
            #self.flat = Batch(self.project, "flat")
            #self.flat.addfiles(self.flatfiles, "flat")
            self.batch["flat"].stack(Stacker.Mean())
            if self.checkBoxFlatBias.isChecked():
                self.batch["flat"].subtract("bias", Stacker.Mean())
            if self.checkBoxFlatDark.isChecked():
                self.batch["flat"].subtract("dark", Stacker.Mean())

        if self.checkBoxLightBias.isChecked():
            self.batch["light"].subtract("bias", Stacker.Mean())
        if self.checkBoxLightDark.isChecked():
            self.batch["light"].subtract("dark", Stacker.Mean())
        if self.checkBoxLightFlat.isChecked():
            self.batch["light"].divide("flat", Stacker.Mean())

    def runDebayer(self):

        if self.buttonDebayer.checkedButton().text() == "VNG Cython":
            self.demosaicwrap = Demosaic.VNGCython()
        elif self.buttonDebayer.checkedButton().text() == "Bilinear Cython":
            self.demosaicwrap = Demosaic.BilinearCython()
        elif self.buttonDebayer.checkedButton().text() == "VNG OpenCL":
            self.demosaicwrap = Demosaic.VNG()
        elif self.buttonDebayer.checkedButton().text() == "Bilinear OpenCL":
            self.demosaicwrap = Demosaic.BilinearCl()

        self.batch["light"].demosaic(self.demosaicwrap)

    def runRegister(self):
        if self.buttonRegister.checkedButton().text() == self.radioButtonGrothIM.text():
            self.registerwrap = Registering.Groth_ImageMagick()
        elif self.buttonRegister.checkedButton().text() == self.radioButtonGrothSK.text():
            self.registerwrap = Registering.Groth_Skimage()
        elif self.buttonRegister.checkedButton().text() == self.radioButtonLegacy.text():
            self.registerwrap = Registering.Sextractor2()

        self.batch["light"].register(self.registerwrap)

    def runStack(self):
        print(self.buttonStack.checkedButton())
        if self.radioButtonMean.isChecked():
            self.stackingwrap = Stacker.Mean()
        elif self.radioButtonMedian.isChecked():
            self.stackingwrap = Stacker.Median()
        elif self.radioButtonSMedian.isChecked():
            self.stackingwrap = Stacker.SigmaMedian()
        elif self.radioButtonSClip.isChecked():
            self.stackingwrap = Stacker.SigmaClip()

        self.batch["light"].stack(self.stackingwrap)


class FrameTableModel(QAbstractTableModel):

    header_labels = ['File path', 'Type', 'Column 3', 'Column 4']

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

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)


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
