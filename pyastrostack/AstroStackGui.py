from PyQt4.QtCore import QAbstractTableModel, Qt
from PyQt4.QtGui import QFileDialog, qApp, QInputDialog
from UiDesign import Ui_MainWindow
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

        #Menu
        self.actionNew_project.triggered.connect(self.newProject)
        self.actionOpen_project.triggered.connect(self.loadProject)
        self.actionSave_project.triggered.connect(self.saveProject)
        self.actionExit.triggered.connect(qApp.quit)

        self.pushLight.clicked.connect(self.addLight)
        self.pushDark.clicked.connect(self.addDark)
        self.pushFlat.clicked.connect(self.addFlat)
        self.pushBias.clicked.connect(self.addBias)

        self.buttonDebayer.setExclusive(True)
        self.buttonRegister.setExclusive(True)
        self.buttonStack.setExclusive(True)

        self.setDefaultValues()
        self.fileDialog = QFileDialog()
        self.inputDialog = QInputDialog()

        self.framearray = []

    def setDefaultValues(self):

        self.checkBoxDarkBias.setCheckState(Qt.Unchecked)
        self.checkBoxFlatBias.setCheckState(Qt.Checked)
        self.checkBoxFlatDark.setCheckState(Qt.Unchecked)
        self.checkBoxLightBias.setCheckState(Qt.Checked)
        self.checkBoxLightDark.setCheckState(Qt.Unchecked)
        self.checkBoxLightFlat.setCheckState(Qt.Checked)

        self.checkBoxCalib.setCheckState(Qt.Checked)
        self.checkBoxDebayer.setCheckState(Qt.Checked)
        self.checkBoxReg.setCheckState(Qt.Checked)
        self.checkBoxStack.setCheckState(Qt.Checked)

        self.radioButtonVNGCyt.setChecked(True)
        self.radioButtonGrothSK.setChecked(True)
        self.radioButtonSMedian.setChecked(True)

    def loadProject(self):
        pass

    def saveProject(self):
        pass

    def newProject(self):
        self.pname, ok = self.inputDialog.getText(self.inputDialog, "New project", "Type name for the new project:")

        if not ok:
            return
        if self.pname == "":
            return

        self.setProjectName(str(self.pname))
        self.setDefaultValues()
        self.framearray = []
        tablemodel = FrameTableModel(self.framearray)
        self.tableView.setModel(tablemodel)

    def projectName(self):
        self.pname, ok = self.inputDialog.getText(self.inputDialog, "New project", "Type name for the new project:")
        if ok:
            self.setProjectName(str(self.pname))

    def setProjectName(self, pname):
        self.projectName.setText(_fromUtf8(pname))

    def setValues(self, values):

        if values["darkbias"]:
            self.checkBoxDarkBias.setCheckState(Qt.Checked)
        else:
            self.checkBoxDarkBias.setCheckState(Qt.Unchecked)
        if values["flatbias"]:
            self.checkBoxFlatBias.setCheckState(Qt.Checked)
        else:
            self.checkBoxFlatBias.setCheckState(Qt.Unchecked)
        if values["flatdark"]:
            self.checkBoxFlatDark.setCheckState(Qt.Checked)
        else:
            self.checkBoxFlatDark.setCheckState(Qt.Unchecked)
        if values["lightbias"]:
            self.checkBoxLightBias.setCheckState(Qt.Checked)
        else:
            self.checkBoxLightBias.setCheckState(Qt.Unchecked)
        if values["lightdark"]:
            self.checkBoxLightDark.setCheckState(Qt.Checked)
        else:
            self.checkBoxLightDark.setCheckState(Qt.Unchecked)
        if values["lightflat"]:
            self.checkBoxLightFlat.setCheckState(Qt.Checked)
        else:
            self.checkBoxLightFlat.setCheckState(Qt.Unchecked)

    def addLight(self):
        files = QFileDialog.getOpenFileNames()
        self.addFrame(files, "light")

    def addDark(self):
        files = QFileDialog.getOpenFileNames()
        self.addFrame(files, "dark")

    def addFlat(self):
        files = QFileDialog.getOpenFileNames()
        self.addFrame(files, "flat")

    def addBias(self):
        files = QFileDialog.getOpenFileNames()
        self.addFrame(files, "bias")

    def addFrame(self, files, itype):

        for i in files:
            self.framearray.append([i, itype])
        tablemodel = FrameTableModel(self.framearray)
        self.tableView.setModel(tablemodel)


class FrameTableModel(QAbstractTableModel):
    def __init__(self, datain, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        return len(self.arraydata[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.arraydata[index.row()][index.column()]