# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AstroStack.ui'
#
# Created: Fri May 16 14:54:00 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(819, 626)
        self.centralwidget = QtGui.QWidget(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_3 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_3.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.gridLayout_3.setSpacing(-1)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.toolBox = QtGui.QToolBox(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolBox.sizePolicy().hasHeightForWidth())
        self.toolBox.setSizePolicy(sizePolicy)
        self.toolBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.toolBox.setObjectName(_fromUtf8("toolBox"))
        self.pageFrames = QtGui.QWidget()
        self.pageFrames.setGeometry(QtCore.QRect(0, 0, 174, 389))
        self.pageFrames.setObjectName(_fromUtf8("pageFrames"))
        self.label_6 = QtGui.QLabel(self.pageFrames)
        self.label_6.setGeometry(QtCore.QRect(7, 0, 61, 20))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.pushLight = QtGui.QPushButton(self.pageFrames)
        self.pushLight.setGeometry(QtCore.QRect(7, 28, 56, 23))
        self.pushLight.setObjectName(_fromUtf8("pushLight"))
        self.pushBias = QtGui.QPushButton(self.pageFrames)
        self.pushBias.setGeometry(QtCore.QRect(7, 96, 52, 23))
        self.pushBias.setObjectName(_fromUtf8("pushBias"))
        self.pushDark = QtGui.QPushButton(self.pageFrames)
        self.pushDark.setGeometry(QtCore.QRect(7, 62, 56, 23))
        self.pushDark.setObjectName(_fromUtf8("pushDark"))
        self.pushFlat = QtGui.QPushButton(self.pageFrames)
        self.pushFlat.setGeometry(QtCore.QRect(7, 130, 50, 23))
        self.pushFlat.setObjectName(_fromUtf8("pushFlat"))
        self.toolBox.addItem(self.pageFrames, _fromUtf8(""))
        self.pageCalib = QtGui.QWidget()
        self.pageCalib.setGeometry(QtCore.QRect(0, 0, 174, 389))
        self.pageCalib.setObjectName(_fromUtf8("pageCalib"))
        self.layoutWidget = QtGui.QWidget(self.pageCalib)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 0, 141, 241))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayoutCalibrate = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayoutCalibrate.setMargin(0)
        self.verticalLayoutCalibrate.setObjectName(_fromUtf8("verticalLayoutCalibrate"))
        self.label_3 = QtGui.QLabel(self.layoutWidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayoutCalibrate.addWidget(self.label_3)
        self.checkBoxDarkBias = QtGui.QCheckBox(self.layoutWidget)
        self.checkBoxDarkBias.setObjectName(_fromUtf8("checkBoxDarkBias"))
        self.verticalLayoutCalibrate.addWidget(self.checkBoxDarkBias)
        self.label_4 = QtGui.QLabel(self.layoutWidget)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayoutCalibrate.addWidget(self.label_4)
        self.checkBoxFlatBias = QtGui.QCheckBox(self.layoutWidget)
        self.checkBoxFlatBias.setObjectName(_fromUtf8("checkBoxFlatBias"))
        self.verticalLayoutCalibrate.addWidget(self.checkBoxFlatBias)
        self.checkBoxFlatDark = QtGui.QCheckBox(self.layoutWidget)
        self.checkBoxFlatDark.setObjectName(_fromUtf8("checkBoxFlatDark"))
        self.verticalLayoutCalibrate.addWidget(self.checkBoxFlatDark)
        self.label_5 = QtGui.QLabel(self.layoutWidget)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayoutCalibrate.addWidget(self.label_5)
        self.checkBoxLightBias = QtGui.QCheckBox(self.layoutWidget)
        self.checkBoxLightBias.setObjectName(_fromUtf8("checkBoxLightBias"))
        self.verticalLayoutCalibrate.addWidget(self.checkBoxLightBias)
        self.checkBoxLightDark = QtGui.QCheckBox(self.layoutWidget)
        self.checkBoxLightDark.setObjectName(_fromUtf8("checkBoxLightDark"))
        self.verticalLayoutCalibrate.addWidget(self.checkBoxLightDark)
        self.checkBoxLightFlat = QtGui.QCheckBox(self.layoutWidget)
        self.checkBoxLightFlat.setObjectName(_fromUtf8("checkBoxLightFlat"))
        self.verticalLayoutCalibrate.addWidget(self.checkBoxLightFlat)
        self.toolBox.addItem(self.pageCalib, _fromUtf8(""))
        self.pageDebayer = QtGui.QWidget()
        self.pageDebayer.setGeometry(QtCore.QRect(0, 0, 174, 389))
        self.pageDebayer.setObjectName(_fromUtf8("pageDebayer"))
        self.layoutWidget1 = QtGui.QWidget(self.pageDebayer)
        self.layoutWidget1.setGeometry(QtCore.QRect(0, 0, 161, 111))
        self.layoutWidget1.setObjectName(_fromUtf8("layoutWidget1"))
        self.verticalLayoutDebayer = QtGui.QVBoxLayout(self.layoutWidget1)
        self.verticalLayoutDebayer.setMargin(0)
        self.verticalLayoutDebayer.setObjectName(_fromUtf8("verticalLayoutDebayer"))
        self.radioButtonBilinearCyt = QtGui.QRadioButton(self.layoutWidget1)
        self.radioButtonBilinearCyt.setObjectName(_fromUtf8("radioButtonBilinearCyt"))
        self.buttonDebayer = QtGui.QButtonGroup(MainWindow)
        self.buttonDebayer.setObjectName(_fromUtf8("buttonDebayer"))
        self.buttonDebayer.addButton(self.radioButtonBilinearCyt)
        self.verticalLayoutDebayer.addWidget(self.radioButtonBilinearCyt)
        self.radioButtonVNGCyt = QtGui.QRadioButton(self.layoutWidget1)
        self.radioButtonVNGCyt.setObjectName(_fromUtf8("radioButtonVNGCyt"))
        self.buttonDebayer.addButton(self.radioButtonVNGCyt)
        self.verticalLayoutDebayer.addWidget(self.radioButtonVNGCyt)
        self.radioButtonBilinearCL = QtGui.QRadioButton(self.layoutWidget1)
        self.radioButtonBilinearCL.setObjectName(_fromUtf8("radioButtonBilinearCL"))
        self.buttonDebayer.addButton(self.radioButtonBilinearCL)
        self.verticalLayoutDebayer.addWidget(self.radioButtonBilinearCL)
        self.radioButtonVNGCL = QtGui.QRadioButton(self.layoutWidget1)
        self.radioButtonVNGCL.setObjectName(_fromUtf8("radioButtonVNGCL"))
        self.buttonDebayer.addButton(self.radioButtonVNGCL)
        self.verticalLayoutDebayer.addWidget(self.radioButtonVNGCL)
        self.toolBox.addItem(self.pageDebayer, _fromUtf8(""))
        self.pageReg = QtGui.QWidget()
        self.pageReg.setGeometry(QtCore.QRect(0, 0, 174, 389))
        self.pageReg.setObjectName(_fromUtf8("pageReg"))
        self.layoutWidget2 = QtGui.QWidget(self.pageReg)
        self.layoutWidget2.setGeometry(QtCore.QRect(0, 10, 161, 73))
        self.layoutWidget2.setObjectName(_fromUtf8("layoutWidget2"))
        self.verticalLayoutRegister = QtGui.QVBoxLayout(self.layoutWidget2)
        self.verticalLayoutRegister.setMargin(0)
        self.verticalLayoutRegister.setObjectName(_fromUtf8("verticalLayoutRegister"))
        self.radioButtonGrothIM = QtGui.QRadioButton(self.layoutWidget2)
        self.radioButtonGrothIM.setObjectName(_fromUtf8("radioButtonGrothIM"))
        self.buttonRegister = QtGui.QButtonGroup(MainWindow)
        self.buttonRegister.setObjectName(_fromUtf8("buttonRegister"))
        self.buttonRegister.addButton(self.radioButtonGrothIM)
        self.verticalLayoutRegister.addWidget(self.radioButtonGrothIM)
        self.radioButtonGrothSK = QtGui.QRadioButton(self.layoutWidget2)
        self.radioButtonGrothSK.setObjectName(_fromUtf8("radioButtonGrothSK"))
        self.buttonRegister.addButton(self.radioButtonGrothSK)
        self.verticalLayoutRegister.addWidget(self.radioButtonGrothSK)
        self.toolBox.addItem(self.pageReg, _fromUtf8(""))
        self.pageStack = QtGui.QWidget()
        self.pageStack.setGeometry(QtCore.QRect(0, 0, 174, 389))
        self.pageStack.setObjectName(_fromUtf8("pageStack"))
        self.layoutWidget3 = QtGui.QWidget(self.pageStack)
        self.layoutWidget3.setGeometry(QtCore.QRect(10, 10, 117, 111))
        self.layoutWidget3.setObjectName(_fromUtf8("layoutWidget3"))
        self.verticalLayoutStack = QtGui.QVBoxLayout(self.layoutWidget3)
        self.verticalLayoutStack.setMargin(0)
        self.verticalLayoutStack.setObjectName(_fromUtf8("verticalLayoutStack"))
        self.radioButtonMean = QtGui.QRadioButton(self.layoutWidget3)
        self.radioButtonMean.setObjectName(_fromUtf8("radioButtonMean"))
        self.buttonStack = QtGui.QButtonGroup(MainWindow)
        self.buttonStack.setObjectName(_fromUtf8("buttonStack"))
        self.buttonStack.addButton(self.radioButtonMean)
        self.verticalLayoutStack.addWidget(self.radioButtonMean)
        self.radioButtonMedian = QtGui.QRadioButton(self.layoutWidget3)
        self.radioButtonMedian.setObjectName(_fromUtf8("radioButtonMedian"))
        self.buttonStack.addButton(self.radioButtonMedian)
        self.verticalLayoutStack.addWidget(self.radioButtonMedian)
        self.radioButtonSClip = QtGui.QRadioButton(self.layoutWidget3)
        self.radioButtonSClip.setObjectName(_fromUtf8("radioButtonSClip"))
        self.verticalLayoutStack.addWidget(self.radioButtonSClip)
        self.radioButtonSMedian = QtGui.QRadioButton(self.layoutWidget3)
        self.radioButtonSMedian.setObjectName(_fromUtf8("radioButtonSMedian"))
        self.verticalLayoutStack.addWidget(self.radioButtonSMedian)
        self.toolBox.addItem(self.pageStack, _fromUtf8(""))
        self.pageRun = QtGui.QWidget()
        self.pageRun.setGeometry(QtCore.QRect(0, 0, 174, 389))
        self.pageRun.setObjectName(_fromUtf8("pageRun"))
        self.label_2 = QtGui.QLabel(self.pageRun)
        self.label_2.setGeometry(QtCore.QRect(0, 0, 91, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.pushButtonRun = QtGui.QPushButton(self.pageRun)
        self.pushButtonRun.setGeometry(QtCore.QRect(10, 160, 151, 23))
        self.pushButtonRun.setObjectName(_fromUtf8("pushButtonRun"))
        self.layoutWidget4 = QtGui.QWidget(self.pageRun)
        self.layoutWidget4.setGeometry(QtCore.QRect(0, 20, 161, 123))
        self.layoutWidget4.setObjectName(_fromUtf8("layoutWidget4"))
        self.verticalLayoutRun = QtGui.QVBoxLayout(self.layoutWidget4)
        self.verticalLayoutRun.setMargin(0)
        self.verticalLayoutRun.setObjectName(_fromUtf8("verticalLayoutRun"))
        self.checkBoxCalib = QtGui.QCheckBox(self.layoutWidget4)
        self.checkBoxCalib.setObjectName(_fromUtf8("checkBoxCalib"))
        self.verticalLayoutRun.addWidget(self.checkBoxCalib)
        self.checkBoxDebayer = QtGui.QCheckBox(self.layoutWidget4)
        self.checkBoxDebayer.setObjectName(_fromUtf8("checkBoxDebayer"))
        self.verticalLayoutRun.addWidget(self.checkBoxDebayer)
        self.checkBoxReg = QtGui.QCheckBox(self.layoutWidget4)
        self.checkBoxReg.setObjectName(_fromUtf8("checkBoxReg"))
        self.verticalLayoutRun.addWidget(self.checkBoxReg)
        self.checkBoxStack = QtGui.QCheckBox(self.layoutWidget4)
        self.checkBoxStack.setObjectName(_fromUtf8("checkBoxStack"))
        self.verticalLayoutRun.addWidget(self.checkBoxStack)
        self.toolBox.addItem(self.pageRun, _fromUtf8(""))
        self.gridLayout_2.addWidget(self.toolBox, 1, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.widget = QtGui.QWidget(self.centralwidget)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.formLayout = QtGui.QFormLayout(self.widget)
        self.formLayout.setMargin(0)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label_7 = QtGui.QLabel(self.widget)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_7)
        self.projectName = QtGui.QLabel(self.widget)
        self.projectName.setObjectName(_fromUtf8("projectName"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.projectName)
        self.gridLayout.addWidget(self.widget, 0, 0, 1, 1)
        self.tableView = QtGui.QTableView(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.setObjectName(_fromUtf8("tableView"))
        self.gridLayout.addWidget(self.tableView, 1, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout, 0, 1, 1, 1)
        self.widget_2 = QtGui.QWidget(self.centralwidget)
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.gridLayout_3.addWidget(self.widget_2, 1, 0, 1, 1)
        self.gridLayout_3.setColumnStretch(0, 3)
        self.gridLayout_3.setColumnStretch(1, 10)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 819, 20))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen_project = QtGui.QAction(MainWindow)
        self.actionOpen_project.setObjectName(_fromUtf8("actionOpen_project"))
        self.actionSave_project = QtGui.QAction(MainWindow)
        self.actionSave_project.setObjectName(_fromUtf8("actionSave_project"))
        self.actionNew_project = QtGui.QAction(MainWindow)
        self.actionNew_project.setObjectName(_fromUtf8("actionNew_project"))
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.menuFile.addAction(self.actionNew_project)
        self.menuFile.addAction(self.actionOpen_project)
        self.menuFile.addAction(self.actionSave_project)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.toolBox.setCurrentIndex(3)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "PyAstroStack", None))
        self.label.setText(_translate("MainWindow", "Project settings", None))
        self.label_6.setText(_translate("MainWindow", "Add", None))
        self.pushLight.setText(_translate("MainWindow", "Light", None))
        self.pushBias.setText(_translate("MainWindow", "Bias", None))
        self.pushDark.setText(_translate("MainWindow", "Dark", None))
        self.pushFlat.setText(_translate("MainWindow", "Flat", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.pageFrames), _translate("MainWindow", "Frames", None))
        self.label_3.setText(_translate("MainWindow", "Dark frames", None))
        self.checkBoxDarkBias.setText(_translate("MainWindow", "Subtract bias", None))
        self.label_4.setText(_translate("MainWindow", "Flat frames", None))
        self.checkBoxFlatBias.setText(_translate("MainWindow", "Subtract bias", None))
        self.checkBoxFlatDark.setText(_translate("MainWindow", "Subtract dark", None))
        self.label_5.setText(_translate("MainWindow", "Light frames", None))
        self.checkBoxLightBias.setText(_translate("MainWindow", "Subtract bias", None))
        self.checkBoxLightDark.setText(_translate("MainWindow", "Subtract dark", None))
        self.checkBoxLightFlat.setText(_translate("MainWindow", "Divide by flat", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.pageCalib), _translate("MainWindow", "Calibrating", None))
        self.radioButtonBilinearCyt.setText(_translate("MainWindow", "Bilinear Cython", None))
        self.radioButtonVNGCyt.setText(_translate("MainWindow", "VNG Cython", None))
        self.radioButtonBilinearCL.setText(_translate("MainWindow", "Bilinear OpenCL", None))
        self.radioButtonVNGCL.setText(_translate("MainWindow", "VNG OpenCL", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.pageDebayer), _translate("MainWindow", "Debayering", None))
        self.radioButtonGrothIM.setText(_translate("MainWindow", "Groth + ImageMagick", None))
        self.radioButtonGrothSK.setText(_translate("MainWindow", "Groth + Scikit", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.pageReg), _translate("MainWindow", "Registering", None))
        self.radioButtonMean.setText(_translate("MainWindow", "Mean", None))
        self.radioButtonMedian.setText(_translate("MainWindow", "Median", None))
        self.radioButtonSClip.setText(_translate("MainWindow", "Sigma Clipping", None))
        self.radioButtonSMedian.setText(_translate("MainWindow", "Sigma Median", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.pageStack), _translate("MainWindow", "Stacking", None))
        self.label_2.setText(_translate("MainWindow", "Set workflow", None))
        self.pushButtonRun.setText(_translate("MainWindow", "Run", None))
        self.checkBoxCalib.setText(_translate("MainWindow", "Calibrate", None))
        self.checkBoxDebayer.setText(_translate("MainWindow", "Debayer", None))
        self.checkBoxReg.setText(_translate("MainWindow", "Register", None))
        self.checkBoxStack.setText(_translate("MainWindow", "Stack", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.pageRun), _translate("MainWindow", "Run", None))
        self.label_7.setText(_translate("MainWindow", "Project name:", None))
        self.projectName.setText(_translate("MainWindow", "Not Set! Choose File -> New project", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.actionOpen_project.setText(_translate("MainWindow", "Open project", None))
        self.actionSave_project.setText(_translate("MainWindow", "Save project", None))
        self.actionNew_project.setText(_translate("MainWindow", "New project", None))
        self.actionExit.setText(_translate("MainWindow", "Exit", None))

