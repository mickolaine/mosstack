"""
Graphical user interface for pyAstroStack. This file holds all the functionality for GUI drafted in Qt Designer.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import QFileDialog, qApp, QInputDialog, QDialog, QMessageBox, QAbstractItemView, QItemSelectionModel,QSortFilterProxyModel
from ast import literal_eval
from subprocess import CalledProcessError
from . UiDesign import Ui_MainWindow
from . settings import Ui_Dialog
from . Config import Project, Global, Setup
from . QBatch import QBatch
from . import Registering
from . import Debayer
from . import Stacker

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


class Ui(Ui_MainWindow, QObject):

    def __init__(self):
        super(Ui_MainWindow, self).__init__()

        self.thread = None
        self.fileDialog = QFileDialog()
        self.inputDialog = QInputDialog()
        self.messageBox = QMessageBox()
        self.swindow = Settings()

        self.threadpool = QThreadPool(self)
        self.threads = 4

        self.framearray = []
        self.batch = {}
        self.pname = None
        self.project = None

        self.selectedId = None
        self.selectedFtype = None
        self.infotablemodel = None

        self.values = {"tempdir": "", "sexpath": "/usr/bin/sex", "processes": 1}

    def setupManual(self, MainWindow):
        """
        Add things I don't know how to add with Qt Designer
        """

        # Menu
        self.actionNew_project.triggered.connect(self.newProject)
        self.actionOpen_project.triggered.connect(self.loadProject)
        self.actionSave_project.triggered.connect(self.saveProject)
        self.actionSettings.triggered.connect(self.settings)
        self.actionAbout.triggered.connect(self.about)
        self.actionExit.triggered.connect(qApp.quit)

        # Buttons
        self.pushLight.clicked.connect(self.addLight)
        self.pushDark.clicked.connect(self.addDark)
        self.pushFlat.clicked.connect(self.addFlat)
        self.pushBias.clicked.connect(self.addBias)
        self.pushButtonRun.clicked.connect(self.runProgram)
        self.pushButtonMakeRef.clicked.connect(self.makeRef)

        self.buttonDebayer.setExclusive(True)
        self.buttonRegister.setExclusive(True)
        self.buttonStack.setExclusive(True)

        # TableView

        # Check setup
        try:
            Global.get("Default", "Path")
        except KeyError:
            self.settings()

        if not use_pyopencl:
            self.radioButtonBilinearCL.setEnabled(False)
            self.radioButtonVNGCL.setEnabled(False)

        self.setValues()
        self.threadpool.setMaxThreadCount(self.threads)

    def settings(self):
        """
        Open settings window and read values from there.
        """

        #self.swindow = Settings()
        dialog = QDialog()
        self.swindow.setupUi(dialog)

        try:
            self.values = {"tempdir": Global.get("Default", "path"),
                           "sexpath": Global.get("Programs", "sextractor"),
                           "processes": self.threads}
        except KeyError:
            try:
                sexpath = Setup.findsex()
            except CalledProcessError:
                sexpath = ""
            self.values = {"tempdir": "", "sexpath": sexpath, "processes": 1}

        self.swindow.setupContent(values=self.values)
        if dialog.exec():
            new_values = self.swindow.getValues()

            self.threads = new_values["processes"]
            Global.set("Programs", "sextractor", self.values["sexpath"])
            Global.set("Default", "path", self.values["tempdir"])

    def about(self):
        """
        Open about dialog
        """

        self.messageBox.information(self.messageBox, 'About',
                                    'Mikko\'s Open Source Stacker for astronomical photos\nmosstack\n\n' +
                                    'Licensed under GPLv3\n\n' +
                                    'Nothing here yet.')

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
                                                     directory=Global.get("Default", "Path"),
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
        tablemodel = GenericTableModel(self.framearray)
        self.tableView.setModel(tablemodel)

    def setProjectName(self, pname):
        self.projectName.setText(_fromUtf8(pname))
        #self.projectName.setText(pname)
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
        for path in files:
            # If batch does not exist, create one
            if ftype not in self.batch:
                self.batch[ftype] = QBatch(self.project, ftype)
                self.batch[ftype].refresh.connect(self.updateTableView)

            self.threadpool.start(GenericThread(self.batch[ftype].addfile, path, ftype, str(number)))

            number += 1

        self.threadpool.waitForDone()

        for i in self.batch[ftype].frames:
            self.threadpool.start(GenericThread(self.batch[ftype].decode, i))

    def updateTableView(self):
        """
        Update frame list view.
        """
        self.tablemodel = []
        for i in self.batch:
            self.tablemodel += self.batch[i].framearray
        self.tablemodel = GenericTableModel(self.tablemodel)
        self.tablemodel.header_labels = ['Id', 'File path', 'Type', 'Decoded', 'Calibrated', 'Debayered', 'Registered']
        self.tableView.setModel(self.tablemodel)
        self.tableView.resizeColumnsToContents()
        self.tableView.resizeRowsToContents()
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.selectionModel().currentChanged.connect(self.updateInfoView)

    def updateInfoView(self, selected, deselected):
        """
        Update frame information view to the selected frame Qt.DisplayRole
        """

        self.selectedId = str(self.tablemodel.data(selected.sibling(selected.row(), 0), Qt.DisplayRole))
        self.selectedFtype = self.tablemodel.data(selected.sibling(selected.row(), 2), Qt.DisplayRole)
        self.infotablemodel = GenericTableModel(self.batch[self.selectedFtype].frames[self.selectedId].infotable())
        self.infotablemodel.header_labels = ["Attribute", "Value"]
        self.tableView_2.setModel(self.infotablemodel)
        self.tableView_2.resizeColumnsToContents()
        self.tableView_2.resizeRowsToContents()

    def makeRef(self):
        """
        Make selected image the reference frame
        """
        self.batch[self.selectedFtype].setRef(self.selectedId)

    def runProgram(self):
        """
        Check what needs to be done and call everything necessary
        """

        self.messageBox.information(self.messageBox, 'Starting the process...',
                                    'Press Ok and the process will start. Program will be unresponsive and all the ' +
                                    'output goes to terminal.')
        self.threadpool.waitForDone()
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
        Run everything needed for calibrating
        """

        # First gather some instructions on what is required. Makes reading the if's ahead easier
        need_bias = self.checkBoxDarkBias.isChecked() + \
                    self.checkBoxFlatBias.isChecked() + \
                    self.checkBoxLightBias.isChecked()
        need_dark = self.checkBoxDarkBias.isChecked() + \
                    self.checkBoxLightDark.isChecked() + \
                    self.checkBoxFlatDark.isChecked()
        need_flat = self.checkBoxFlatBias.isChecked() + \
                    self.checkBoxFlatDark.isChecked() + \
                    self.checkBoxLightFlat.isChecked()

        darkbias = self.checkBoxDarkBias.isChecked()
        flatbias = self.checkBoxFlatBias.isChecked()
        flatdark = self.checkBoxFlatDark.isChecked()
        lightbias = self.checkBoxLightBias.isChecked()
        lightdark = self.checkBoxLightDark.isChecked()
        lightflat = self.checkBoxLightFlat.isChecked()

        # Bias frames
        if need_bias > 0:
            # Threads set to 1 because this has to be done before anything else

            self.threadpool.setMaxThreadCount(1)
            self.threadpool.start(GenericThread(self.batch["bias"].stack, Stacker.Mean()))
            self.threadpool.waitForDone()
            self.threadpool.setMaxThreadCount(self.threads)

        # Dark frames
        if need_dark > 0:
            for i in self.batch["dark"].frames:
                self.threadpool.start(GenericThread(self.batch["dark"].calibrate, i, Stacker.Mean(), bias=darkbias))
            self.threadpool.setMaxThreadCount(1)
            self.threadpool.start(GenericThread(self.batch["dark"].stack, Stacker.Mean()))
            self.threadpool.waitForDone()
            self.threadpool.setMaxThreadCount(self.threads)

        # Flat frames
        if need_flat > 0:
            for i in self.batch["flat"].frames:
                self.threadpool.start(GenericThread(self.batch["flat"].calibrate, i, Stacker.Mean(), bias=flatbias,
                                                                                                     dark=flatdark))
            self.threadpool.setMaxThreadCount(1)
            self.threadpool.start(GenericThread(self.batch["flat"].stack, Stacker.Mean()))
            self.threadpool.waitForDone()
            self.threadpool.setMaxThreadCount(self.threads)

        # Light frames
        for i in self.batch["light"].frames:
            self.threadpool.start(GenericThread(self.batch["light"].calibrate, i, Stacker.Mean(), bias=lightbias,
                                                                                                  dark=lightdark,
                                                                                                  flat=lightflat))
        self.threadpool.setMaxThreadCount(1)
        self.threadpool.start(GenericThread(self.batch["light"].stack, Stacker.Mean()))
        self.threadpool.waitForDone()
        self.threadpool.setMaxThreadCount(self.threads)

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

        # First register the reference frame. This has to be done before anything else
        self.threadpool.start(GenericThread(self.batch["light"].register,
                                            self.batch["light"].refId,
                                            self.registerwrap,
                                            ref=True))
        self.threadpool.waitForDone()

        for i in self.batch["light"].frames:
            if i == self.batch["light"].refId:
                continue
            self.threadpool.start(GenericThread(self.batch["light"].register, i, self.registerwrap))

        self.threadpool.waitForDone()

    def runStack(self):
        """
        Run everything related to stacking
        """
        if self.radioButtonMaximum.isChecked():
            self.stackingwrap = Stacker.Maximum()
        elif self.radioButtonMinimum.isChecked():
            self.stackingwrap = Stacker.Minimum()
        elif self.radioButtonMean.isChecked():
            self.stackingwrap = Stacker.Mean()
        elif self.radioButtonMedian.isChecked():
            self.stackingwrap = Stacker.Median()
        elif self.radioButtonSMedian.isChecked():
            self.stackingwrap = Stacker.SigmaMedian()
        elif self.radioButtonSClip.isChecked():
            self.stackingwrap = Stacker.SigmaClip()

        self.threadpool.start(GenericThread(self.batch["light"].stack, self.stackingwrap))

        self.threadpool.waitForDone()

        self.messageBox.information(self.messageBox, 'Stacking done!',
                                    'Result image saved in ' + self.batch["light"].master.path() + "\n" +
                                    'and ' + self.batch["light"].master.path(fformat="tiff"))


class Settings(Ui_Dialog):
    """
    Defining actions for the Settings window.
    """

    def __init__(self):
        super(Ui_Dialog, self).__init__()
        self.fileDialog = QFileDialog()

    def setupContent(self, values=None):
        """
        Set up everything
        """

        self.pushButtonBrowseTemp.clicked.connect(self.browseTempDialog)
        self.pushButtonBrowseSex.clicked.connect(self.browseSexPath)
        self.comboBox.activated[int].connect(self.comboChange)
        self.lineEditSex.editingFinished.connect(self.lineSexChanged)
        self.lineEditTemp.editingFinished.connect(self.lineTempChanged)

        if values is None:
            self.values = dict()
        else:
            self.values = values

        self.lineEditTemp.setText(self.values["tempdir"])
        self.lineEditSex.setText(self.values["sexpath"])
        self.comboBox.setCurrentIndex(self.values["processes"] - 1)

    def browseTempDialog(self):
        self.values["tempdir"] = self.fileDialog.getExistingDirectory(caption="Select directory for temporary files")
        self.lineEditTemp.setText(self.values["tempdir"])

    def browseSexPath(self):
        self.values["sexpath"] = self.fileDialog.getOpenFileName(caption="Select SExtractor binary",
                                                                 directory="/usr/bin/")
        self.lineEditSex.setText(self.values["sexpath"])

    def lineSexChanged(self):
        self.values["sexpath"] = self.lineEditSex.text()

    def lineTempChanged(self):
        self.values["tempdir"] = self.lineEditTemp.text()

    def comboChange(self):
        try:
            self.values["processes"] = int(self.comboBox.currentText())
        except ValueError:
            pass

    def getValues(self):
        return self.values


class GenericTableModel(QAbstractTableModel):
    """
    Implementation of QAbstractTableModel required for the TableViews
    """

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

    def run(self):
        self.function(*self.args, **self.kwargs)
        return