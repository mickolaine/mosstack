"""
Graphical user interface for pyAstroStack. This file holds all the functionality for GUI drafted in Qt Designer.
"""

#from PyQt4.QtCore import QAbstractTableModel, Qt, QThread, pyqtSignal, SIGNAL
from PyQt4.QtCore import *
from PyQt4.QtGui import QFileDialog, qApp, QInputDialog, QProgressDialog, QMessageBox, QAction, QApplication
from ast import literal_eval
from . UiDesign import Ui_MainWindow
from . Config import Project, Setup
from . QBatch import QBatch
from . QFrame import QFrame
from . import Registering
from . import Debayer
from . import Stacker
import sys
try:
    from PyQt4.QtCore import Qstring
    _fromUtf8 = QString.fromUtf8
except ImportError:
    def _fromUtf8(s):
        return s

try:
    import pyopencl
    use_pyopencl = True
except ImportError:
    use_pyopencl = False


class Ui(Ui_MainWindow):

    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        #self.app = QApplication(sys.argv)
        #self.setupUi(self)
        #self.app.exec_()

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

        if not use_pyopencl:
            self.radioButtonBilinearCL.setEnabled(False)
            self.radioButtonVNGCL.setEnabled(False)

        self.setValues()
        self.thread = None
        self.fileDialog = QFileDialog()
        self.inputDialog = QInputDialog()
        self.messageBox = QMessageBox()

        self.threadpool = QThreadPool(self)
        self.threadpool.setMaxThreadCount(1)   # TODO: This should be an option

        self.framearray = []
        self.batch = {}
        self.pname = None

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
                      "BilinearOpenCl": 0,
                      "VNGOPENCL": 0,
                      "GrothIM": 0,
                      "GrothSK": 2,
                      #"Legacy": 0,
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
        self.radioButtonBilinearCL.setChecked(values["BilinearOpenCl"])
        self.radioButtonVNGCL.setChecked(values["VNGOPENCL"])

        self.radioButtonGrothIM.setChecked(values["GrothIM"])
        self.radioButtonGrothSK.setChecked(values["GrothSK"])
        #self.radioButtonLegacy.setChecked(values["Legacy"])

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
                  "BilinearOpenCl": self.radioButtonBilinearCL.isChecked(),
                  "VNGOPENCL": self.radioButtonVNGCL.isChecked(),
                  "GrothIM": self.radioButtonGrothIM.isChecked(),
                  "GrothSK": self.radioButtonGrothSK.isChecked(),
                  #"Legacy": self.radioButtonLegacy.isChecked(),
                  "Mean": self.radioButtonMean.isChecked(),
                  "Median": self.radioButtonMedian.isChecked(),
                  "SigmaMedian": self.radioButtonSMedian.isChecked(),
                  "SigmaClip": self.radioButtonSClip.isChecked()
                  }
        return values

    def loadProject(self):
        """
        Load a project. Settings and file lists
        """

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
                self.addFrame(files, i)
            except:
                pass

    def saveProject(self):
        """
        Save project settings. All the files are automatically written in project file, but this writes the settings
        as well.
        """
        self.project.set("GUI", "Values", str(self.getValues()))

    def newProject(self):
        """
        Initiate a new project. Project name is required for almost everything so this needs to be done first.
        """

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
        self.pname = pname

    def addFrameDialog(self, ftype):
        """
        Wrapper to add light files. TODO: better solution
        """
        if self.pname is None:
            self.messageBox.information(self.messageBox, 'Error', 'You need to start a new project first!')
            return
        files = QFileDialog.getOpenFileNames(caption="Select light files",
                                             filter="Raw photos (*.CR2 *.cr2)")
        self.addFrame(files, ftype)

        #self.lightfiles = files
        #self.addFrame(files, "light")

    def addLight(self):
        """
        Wrapper to add light files TODO: better solution
        """
        self.addFrameDialog("light")

    def addDark(self):
        """
        Wrapper to add dark files. TODO: better solution
        """

        self.addFrameDialog("dark")

    def addFlat(self):
        """
        Wrapper to add flat files. TODO: better solution
        """

        self.addFrameDialog("flat")

    def addBias(self):
        """
        Wrapper to add bias files. TODO: better solution
        """
        self.addFrameDialog("bias")

    def addFrame(self, files, ftype):
        """
        Add files to frame list and batches. Create batches if they don't already exist.
        """

        # Add files to batch
        number = 0
        #threadpool = QThreadPool(self)
        #threadpool.setMaxThreadCount(1)

        for path in files:
            # If batch does not exist, create one
            if ftype not in self.batch:
                self.batch[ftype] = QBatch(self.project, ftype)
                self.batch[ftype].refresh.connect(self.updateTableView)

            self.threadpool.start(GenericThread(self.batch[ftype].addfile, path, ftype, str(number)))

            number += 1

        self.threadpool.waitForDone()
        #n = 0

        for i in self.batch[ftype].frames:
            self.threadpool.start(GenericThread(self.batch[ftype].decode, i))

        #while n < number:
        #    self.threadpool.start(GenericThread(self.batch[ftype].decode, n), priority=-1)
        #    n += 1

    def updateTableView(self):
        tablemodel = []
        for i in self.batch:
            tablemodel += self.batch[i].framearray
        tablemodel = FrameTableModel(tablemodel)
        self.tableView.setModel(tablemodel)
        self.tableView.resizeColumnsToContents()
        self.tableView.resizeRowsToContents()

    def runProgram(self):
        """
        Check what needs to be done and call everything necessary
        """
        #self.light = Batch(self.project, "light")
        #self.light.addfiles(self.lightfiles, "light")

        self.messageBox.information(self.messageBox, 'Starting the process...',
                                    'Press Ok and the process will start. Program will be unresponsive and all the ' +
                                    'output goes to terminal.')

        if self.checkBoxCalib.isChecked():
            self.runCalib()
        if self.checkBoxDebayer.isChecked():
            self.runDebayer()
        if self.checkBoxReg.isChecked():
            self.runRegister()
        if self.checkBoxStack.isChecked():
            self.runStack()

    def runCalib(self):
        """
        Run everything related to calibrating
        """

        self.threadpool.setMaxThreadCount(1)

        # If Bias frames are required
        if self.checkBoxDarkBias.isChecked() or self.checkBoxFlatBias.isChecked() or self.checkBoxLightBias.isChecked():
            self.threadpool.start(GenericThread(self.batch["bias"].stack, Stacker.Mean()))
            #self.threadpool.waitForDone()
            #self.batch["bias"].stack(Stacker.Mean())

        # If Dark frames are required
        if self.checkBoxDarkBias.isChecked() or self.checkBoxLightDark.isChecked() or self.checkBoxFlatDark.isChecked():
            if self.checkBoxDarkBias.isChecked():
                self.threadpool.start(GenericThread(self.batch["dark"].subtract, "bias", Stacker.Mean()))
                #self.threadpool.waitForDone()
                #self.batch["dark"].subtract("bias", Stacker.Mean())

            self.threadpool.start(GenericThread(self.batch["dark"].stack, Stacker.Mean()))
            #self.threadpool.waitForDone()
            #self.batch["dark"].stack(Stacker.Mean())

        # If Flat frames are required
        if self.checkBoxFlatBias.isChecked() or self.checkBoxFlatDark.isChecked() or self.checkBoxLightFlat.isChecked():
            if self.checkBoxFlatBias.isChecked():
                self.threadpool.start(GenericThread(self.batch["flat"].subtract, "bias", Stacker.Mean()))
                #self.threadpool.waitForDone()
                #self.batch["flat"].subtract("bias", Stacker.Mean())
            if self.checkBoxFlatDark.isChecked():
                self.threadpool.start(GenericThread(self.batch["flat"].subtract, "dark", Stacker.Mean()))
                #self.threadpool.waitForDone()
                #self.batch["flat"].subtract("dark", Stacker.Mean())

            self.threadpool.start(GenericThread(self.batch["flat"].stack, Stacker.Mean()))
            #self.threadpool.waitForDone()
            #self.batch["flat"].stack(Stacker.Mean())

        # Process Light frames. Everything is ready for it
        if self.checkBoxLightBias.isChecked():
            self.threadpool.start(GenericThread(self.batch["light"].subtract, "bias", Stacker.Mean()))
            #self.threadpool.waitForDone()
            #self.batch["light"].subtract("bias", Stacker.Mean())
        if self.checkBoxLightDark.isChecked():
            self.threadpool.start(GenericThread(self.batch["light"].subtract, "dark", Stacker.Mean()))
            #self.threadpool.waitForDone()
            #self.batch["light"].subtract("dark", Stacker.Mean())
        if self.checkBoxLightFlat.isChecked():
            self.threadpool.start(GenericThread(self.batch["light"].divide, "flat", Stacker.Mean()))
            #self.threadpool.waitForDone()
            #self.batch["light"].divide("flat", Stacker.Mean())

        self.threadpool.setMaxThreadCount(1)

    def runDebayer(self):
        """
        Run everything related to debayering
        """

        if self.buttonDebayer.checkedButton().text() == "VNG Cython":
            self.debayerwrap = Debayer.VNGCython()
        elif self.buttonDebayer.checkedButton().text() == "Bilinear Cython":
            self.debayerwrap = Debayer.BilinearCython()
        elif self.buttonDebayer.checkedButton().text() == "VNG OpenCL":
            self.debayerwrap = Debayer.VNGOpenCl()
        elif self.buttonDebayer.checkedButton().text() == "Bilinear OpenCL":
            self.debayerwrap = Debayer.BilinearOpenCl()

        #self.batch["light"].debayer(self.debayerwrap)

        for i in self.batch["light"].frames:
            self.threadpool.start(GenericThread(self.batch["light"].debayer, i, self.debayerwrap))

        self.threadpool.waitForDone()

    def runRegister(self):
        """
        Run everything related to registering
        """
        if self.buttonRegister.checkedButton().text() == self.radioButtonGrothIM.text():
            self.registerwrap = Registering.Groth_ImageMagick()
        elif self.buttonRegister.checkedButton().text() == self.radioButtonGrothSK.text():
            self.registerwrap = Registering.Groth_Skimage()
        #elif self.buttonRegister.checkedButton().text() == self.radioButtonLegacy.text():
        #    self.registerwrap = Registering.Sextractor2()

        # First register the reference frame. This has to be done before anything else
        self.threadpool.start(GenericThread(self.batch["light"].register,
                                            self.batch["light"].refnum,
                                            self.registerwrap))
        self.threadpool.waitForDone()

        for i in self.batch["light"].frames:
            if i == self.batch["light"].refnum:
                continue
            self.threadpool.start(GenericThread(self.batch["light"].register, i, self.registerwrap))

        self.threadpool.waitForDone()
        #self.batch["light"].register(self.registerwrap)

    def runStack(self):
        """
        Run everything related to stacking
        """

        if self.radioButtonMean.isChecked():
            self.stackingwrap = Stacker.Mean()
        elif self.radioButtonMedian.isChecked():
            self.stackingwrap = Stacker.Median()
        elif self.radioButtonSMedian.isChecked():
            self.stackingwrap = Stacker.SigmaMedian()
        elif self.radioButtonSClip.isChecked():
            self.stackingwrap = Stacker.SigmaClip()

        self.threadpool.start(GenericThread(self.batch["light"].stack, self.stackingwrap))
        #self.batch["light"].stack(self.stackingwrap)


class FrameTableModel(QAbstractTableModel):
    """
    Model for file list table.
    """

    header_labels = ['File path', 'Type', 'Decoded', 'Calibrated', 'Debayered', 'Registered']

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


class GenericThread(QRunnable):
    """
    Generic thread borrowed from http://joplaete.wordpress.com/2010/07/21/threading-with-pyqt4/

    Will rewrite this, when I understand what's happening here
    """
    __pyqtSignals__ = ("update")
    refresh = pyqtSignal()

    def __init__(self, function, *args, **kwargs):
        super(QRunnable, self).__init__()
        #QThread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs
        #self.signal = SIGNAL("signal")

    #def __del__(self):
    #    self.wait()

    def run(self):
        self.function(*self.args, **self.kwargs)
        #self.emit(SIGNAL("update"), "CALLED FROM GenericThread.run()")
        #self.refresh.emit()
        return


class BatchThread(QThread):
    """

    """

    update = pyqtSignal()

    def __init__(self, batch, function, *args, **kwargs):
        super(QThread, self).__init__()
        self.batch = batch
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __del__(self):
        self.wait()

    def run(self):
        if self.function == "decode":
            self.run_decode()

        if self.function == "calibrate":
            self.run_calibrate()

        if self.function == "debayering":
            self.run_debayering()

        if self.function == "registering":
            self.run_registering()

        if self.function == "stacking":
            self.run_stacking()

        return

    def run_decode(self):

        pass

    def run_calibrate(self):
        pass

    def run_debayering(self):
        pass

    def run_registering(self):
        pass

    def run_stacking(self):
        pass