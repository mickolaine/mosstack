import sys
from PyQt4.QtCore import QAbstractTableModel, Qt
from PyQt4.QtGui import QApplication, QMainWindow, QFileDialog, QAction, qApp
from AstroStackGui import Ui_MainWindow


class Ui(Ui_MainWindow):

    def __init__(self):
        super(Ui, self).__init__()

    def setupMoar(self, MainWindow):
        """
        Add things I don't know how to add with Qt Designer
        """

        #Menu
        self.actionNew_project
        self.actionOpen_project
        self.actionSave_project
        self.actionExit.triggered.connect(qApp.quit)

        self.pushLight.clicked.connect(self.addLight)
        self.pushDark.clicked.connect(self.addDark)
        self.pushFlat.clicked.connect(self.addFlat)
        self.pushBias.clicked.connect(self.addBias)
        self.fileDialog = QFileDialog()

        self.framearray = []
        tablemodel = FrameTableModel([["1","2","3"],["4","5","6"],["7","8","9"]])

        self.tableView.setModel(tablemodel)

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


class Ui_testi():

    def __init__(self):
        app = QApplication(sys.argv)
        window = QMainWindow()
        ui = Ui()
        ui.setupUi(window)
        ui.setupMoar(window)

        window.show()
        sys.exit(app.exec_())


if __name__ == "__main__":

    Ui_testi()
