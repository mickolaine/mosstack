# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mosstack/AstroStack.ui'
#
# Created: Mon Oct  6 19:42:03 2014
#      by: PyQt4 UI code generator 4.11.1
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
        MainWindow.resize(1072, 857)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/data/astrostack_icon128.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
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
        self.gridLayout_2.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
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
        self.pageFrames.setGeometry(QtCore.QRect(0, 0, 200, 486))
        self.pageFrames.setObjectName(_fromUtf8("pageFrames"))
        self.label_6 = QtGui.QLabel(self.pageFrames)
        self.label_6.setGeometry(QtCore.QRect(10, 0, 61, 20))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_master = QtGui.QLabel(self.pageFrames)
        self.label_master.setGeometry(QtCore.QRect(10, 160, 81, 20))
        self.label_master.setObjectName(_fromUtf8("label_master"))
        self.widget = QtGui.QWidget(self.pageFrames)
        self.widget.setGeometry(QtCore.QRect(10, 180, 71, 81))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.pushButtonMasterDark = QtGui.QPushButton(self.widget)
        self.pushButtonMasterDark.setObjectName(_fromUtf8("pushButtonMasterDark"))
        self.verticalLayout_2.addWidget(self.pushButtonMasterDark)
        self.pushButtonMasterBias = QtGui.QPushButton(self.widget)
        self.pushButtonMasterBias.setObjectName(_fromUtf8("pushButtonMasterBias"))
        self.verticalLayout_2.addWidget(self.pushButtonMasterBias)
        self.pushButtonMasterFlat = QtGui.QPushButton(self.widget)
        self.pushButtonMasterFlat.setObjectName(_fromUtf8("pushButtonMasterFlat"))
        self.verticalLayout_2.addWidget(self.pushButtonMasterFlat)
        self.verticalLayout_2.setStretch(0, 1)
        self.verticalLayout_2.setStretch(1, 1)
        self.verticalLayout_2.setStretch(2, 1)
        self.widget1 = QtGui.QWidget(self.pageFrames)
        self.widget1.setGeometry(QtCore.QRect(10, 20, 73, 106))
        self.widget1.setObjectName(_fromUtf8("widget1"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widget1)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.pushLight = QtGui.QPushButton(self.widget1)
        self.pushLight.setObjectName(_fromUtf8("pushLight"))
        self.verticalLayout.addWidget(self.pushLight)
        self.pushDark = QtGui.QPushButton(self.widget1)
        self.pushDark.setObjectName(_fromUtf8("pushDark"))
        self.verticalLayout.addWidget(self.pushDark)
        self.pushBias = QtGui.QPushButton(self.widget1)
        self.pushBias.setObjectName(_fromUtf8("pushBias"))
        self.verticalLayout.addWidget(self.pushBias)
        self.pushFlat = QtGui.QPushButton(self.widget1)
        self.pushFlat.setObjectName(_fromUtf8("pushFlat"))
        self.verticalLayout.addWidget(self.pushFlat)
        self.toolBox.addItem(self.pageFrames, _fromUtf8(""))
        self.pageCalib = QtGui.QWidget()
        self.pageCalib.setGeometry(QtCore.QRect(0, 0, 200, 486))
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
        self.pageDebayer.setGeometry(QtCore.QRect(0, 0, 200, 486))
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
        self.pageReg.setGeometry(QtCore.QRect(0, 0, 200, 486))
        self.pageReg.setObjectName(_fromUtf8("pageReg"))
        self.layoutWidget2 = QtGui.QWidget(self.pageReg)
        self.layoutWidget2.setGeometry(QtCore.QRect(10, 40, 81, 31))
        self.layoutWidget2.setObjectName(_fromUtf8("layoutWidget2"))
        self.verticalLayoutRegister = QtGui.QVBoxLayout(self.layoutWidget2)
        self.verticalLayoutRegister.setMargin(0)
        self.verticalLayoutRegister.setObjectName(_fromUtf8("verticalLayoutRegister"))
        self.radioButtonGroth = QtGui.QRadioButton(self.layoutWidget2)
        self.radioButtonGroth.setObjectName(_fromUtf8("radioButtonGroth"))
        self.buttonMatcher = QtGui.QButtonGroup(MainWindow)
        self.buttonMatcher.setObjectName(_fromUtf8("buttonMatcher"))
        self.buttonMatcher.addButton(self.radioButtonGroth)
        self.verticalLayoutRegister.addWidget(self.radioButtonGroth)
        self.label_9 = QtGui.QLabel(self.pageReg)
        self.label_9.setGeometry(QtCore.QRect(10, 20, 101, 16))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.label_10 = QtGui.QLabel(self.pageReg)
        self.label_10.setGeometry(QtCore.QRect(10, 90, 161, 16))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.layoutWidget_2 = QtGui.QWidget(self.pageReg)
        self.layoutWidget_2.setGeometry(QtCore.QRect(10, 110, 121, 48))
        self.layoutWidget_2.setObjectName(_fromUtf8("layoutWidget_2"))
        self.verticalLayoutRegister_2 = QtGui.QVBoxLayout(self.layoutWidget_2)
        self.verticalLayoutRegister_2.setMargin(0)
        self.verticalLayoutRegister_2.setObjectName(_fromUtf8("verticalLayoutRegister_2"))
        self.radioButtonScikit = QtGui.QRadioButton(self.layoutWidget_2)
        self.radioButtonScikit.setObjectName(_fromUtf8("radioButtonScikit"))
        self.buttonTransformer = QtGui.QButtonGroup(MainWindow)
        self.buttonTransformer.setObjectName(_fromUtf8("buttonTransformer"))
        self.buttonTransformer.addButton(self.radioButtonScikit)
        self.verticalLayoutRegister_2.addWidget(self.radioButtonScikit)
        self.radioButtonImagick = QtGui.QRadioButton(self.layoutWidget_2)
        self.radioButtonImagick.setObjectName(_fromUtf8("radioButtonImagick"))
        self.buttonTransformer.addButton(self.radioButtonImagick)
        self.verticalLayoutRegister_2.addWidget(self.radioButtonImagick)
        self.toolBox.addItem(self.pageReg, _fromUtf8(""))
        self.pageStack = QtGui.QWidget()
        self.pageStack.setGeometry(QtCore.QRect(0, 0, 200, 486))
        self.pageStack.setObjectName(_fromUtf8("pageStack"))
        self.layoutWidget3 = QtGui.QWidget(self.pageStack)
        self.layoutWidget3.setGeometry(QtCore.QRect(10, 10, 117, 148))
        self.layoutWidget3.setObjectName(_fromUtf8("layoutWidget3"))
        self.verticalLayoutStack = QtGui.QVBoxLayout(self.layoutWidget3)
        self.verticalLayoutStack.setMargin(0)
        self.verticalLayoutStack.setObjectName(_fromUtf8("verticalLayoutStack"))
        self.radioButtonMaximum = QtGui.QRadioButton(self.layoutWidget3)
        self.radioButtonMaximum.setObjectName(_fromUtf8("radioButtonMaximum"))
        self.buttonStack = QtGui.QButtonGroup(MainWindow)
        self.buttonStack.setObjectName(_fromUtf8("buttonStack"))
        self.buttonStack.addButton(self.radioButtonMaximum)
        self.verticalLayoutStack.addWidget(self.radioButtonMaximum)
        self.radioButtonMinimum = QtGui.QRadioButton(self.layoutWidget3)
        self.radioButtonMinimum.setObjectName(_fromUtf8("radioButtonMinimum"))
        self.buttonStack.addButton(self.radioButtonMinimum)
        self.verticalLayoutStack.addWidget(self.radioButtonMinimum)
        self.radioButtonMean = QtGui.QRadioButton(self.layoutWidget3)
        self.radioButtonMean.setObjectName(_fromUtf8("radioButtonMean"))
        self.buttonStack.addButton(self.radioButtonMean)
        self.verticalLayoutStack.addWidget(self.radioButtonMean)
        self.radioButtonMedian = QtGui.QRadioButton(self.layoutWidget3)
        self.radioButtonMedian.setObjectName(_fromUtf8("radioButtonMedian"))
        self.buttonStack.addButton(self.radioButtonMedian)
        self.verticalLayoutStack.addWidget(self.radioButtonMedian)
        self.radioButtonSClip = QtGui.QRadioButton(self.layoutWidget3)
        self.radioButtonSClip.setObjectName(_fromUtf8("radioButtonSClip"))
        self.buttonStack.addButton(self.radioButtonSClip)
        self.verticalLayoutStack.addWidget(self.radioButtonSClip)
        self.radioButtonSMedian = QtGui.QRadioButton(self.layoutWidget3)
        self.radioButtonSMedian.setObjectName(_fromUtf8("radioButtonSMedian"))
        self.buttonStack.addButton(self.radioButtonSMedian)
        self.verticalLayoutStack.addWidget(self.radioButtonSMedian)
        self.layoutWidget4 = QtGui.QWidget(self.pageStack)
        self.layoutWidget4.setGeometry(QtCore.QRect(10, 170, 141, 24))
        self.layoutWidget4.setObjectName(_fromUtf8("layoutWidget4"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.layoutWidget4)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_kappa = QtGui.QLabel(self.layoutWidget4)
        self.label_kappa.setObjectName(_fromUtf8("label_kappa"))
        self.horizontalLayout_2.addWidget(self.label_kappa)
        self.lineEditKappa = QtGui.QLineEdit(self.layoutWidget4)
        self.lineEditKappa.setObjectName(_fromUtf8("lineEditKappa"))
        self.horizontalLayout_2.addWidget(self.lineEditKappa)
        self.toolBox.addItem(self.pageStack, _fromUtf8(""))
        self.pageRun = QtGui.QWidget()
        self.pageRun.setGeometry(QtCore.QRect(0, 0, 200, 486))
        self.pageRun.setObjectName(_fromUtf8("pageRun"))
        self.label_2 = QtGui.QLabel(self.pageRun)
        self.label_2.setGeometry(QtCore.QRect(0, 0, 91, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.layoutWidget5 = QtGui.QWidget(self.pageRun)
        self.layoutWidget5.setGeometry(QtCore.QRect(0, 20, 161, 123))
        self.layoutWidget5.setObjectName(_fromUtf8("layoutWidget5"))
        self.verticalLayoutRun = QtGui.QVBoxLayout(self.layoutWidget5)
        self.verticalLayoutRun.setMargin(0)
        self.verticalLayoutRun.setObjectName(_fromUtf8("verticalLayoutRun"))
        self.checkBoxCalib = QtGui.QCheckBox(self.layoutWidget5)
        self.checkBoxCalib.setObjectName(_fromUtf8("checkBoxCalib"))
        self.verticalLayoutRun.addWidget(self.checkBoxCalib)
        self.checkBoxDebayer = QtGui.QCheckBox(self.layoutWidget5)
        self.checkBoxDebayer.setObjectName(_fromUtf8("checkBoxDebayer"))
        self.verticalLayoutRun.addWidget(self.checkBoxDebayer)
        self.checkBoxReg = QtGui.QCheckBox(self.layoutWidget5)
        self.checkBoxReg.setObjectName(_fromUtf8("checkBoxReg"))
        self.verticalLayoutRun.addWidget(self.checkBoxReg)
        self.checkBoxStack = QtGui.QCheckBox(self.layoutWidget5)
        self.checkBoxStack.setObjectName(_fromUtf8("checkBoxStack"))
        self.verticalLayoutRun.addWidget(self.checkBoxStack)
        self.toolBox.addItem(self.pageRun, _fromUtf8(""))
        self.gridLayout_2.addWidget(self.toolBox, 1, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tableView = QtGui.QTableView(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.setObjectName(_fromUtf8("tableView"))
        self.gridLayout.addWidget(self.tableView, 1, 0, 1, 1)
        self.widget2 = QtGui.QWidget(self.centralwidget)
        self.widget2.setObjectName(_fromUtf8("widget2"))
        self.formLayout = QtGui.QFormLayout(self.widget2)
        self.formLayout.setMargin(0)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label_7 = QtGui.QLabel(self.widget2)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_7)
        self.projectName = QtGui.QLabel(self.widget2)
        self.projectName.setObjectName(_fromUtf8("projectName"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.projectName)
        self.gridLayout.addWidget(self.widget2, 0, 0, 1, 1)
        self.widget_2 = QtGui.QWidget(self.centralwidget)
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.layoutWidget6 = QtGui.QWidget(self.widget_2)
        self.layoutWidget6.setGeometry(QtCore.QRect(0, 0, 801, 25))
        self.layoutWidget6.setObjectName(_fromUtf8("layoutWidget6"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.layoutWidget6)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pushButtonRemoveFrame = QtGui.QPushButton(self.layoutWidget6)
        self.pushButtonRemoveFrame.setObjectName(_fromUtf8("pushButtonRemoveFrame"))
        self.horizontalLayout.addWidget(self.pushButtonRemoveFrame)
        self.pushButtonMakeRef = QtGui.QPushButton(self.layoutWidget6)
        self.pushButtonMakeRef.setObjectName(_fromUtf8("pushButtonMakeRef"))
        self.horizontalLayout.addWidget(self.pushButtonMakeRef)
        self.pushButtonCrop = QtGui.QPushButton(self.layoutWidget6)
        self.pushButtonCrop.setObjectName(_fromUtf8("pushButtonCrop"))
        self.horizontalLayout.addWidget(self.pushButtonCrop)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButtonRun = QtGui.QPushButton(self.layoutWidget6)
        self.pushButtonRun.setMinimumSize(QtCore.QSize(100, 0))
        self.pushButtonRun.setObjectName(_fromUtf8("pushButtonRun"))
        self.horizontalLayout.addWidget(self.pushButtonRun)
        self.gridLayout.addWidget(self.widget_2, 2, 0, 1, 1)
        self.gridLayout.setRowMinimumHeight(2, 30)
        self.gridLayout_3.addLayout(self.gridLayout, 0, 1, 1, 1)
        self.widget_5 = QtGui.QWidget(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(50)
        sizePolicy.setHeightForWidth(self.widget_5.sizePolicy().hasHeightForWidth())
        self.widget_5.setSizePolicy(sizePolicy)
        self.widget_5.setObjectName(_fromUtf8("widget_5"))
        self.tableView_2 = QtGui.QTableView(self.widget_5)
        self.tableView_2.setGeometry(QtCore.QRect(220, 0, 841, 131))
        self.tableView_2.setObjectName(_fromUtf8("tableView_2"))
        self.label_8 = QtGui.QLabel(self.widget_5)
        self.label_8.setGeometry(QtCore.QRect(10, 10, 111, 16))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.layoutWidget7 = QtGui.QWidget(self.widget_5)
        self.layoutWidget7.setGeometry(QtCore.QRect(10, 40, 121, 73))
        self.layoutWidget7.setObjectName(_fromUtf8("layoutWidget7"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.layoutWidget7)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.checkBoxBias = QtGui.QCheckBox(self.layoutWidget7)
        self.checkBoxBias.setCheckable(False)
        self.checkBoxBias.setObjectName(_fromUtf8("checkBoxBias"))
        self.verticalLayout_3.addWidget(self.checkBoxBias)
        self.checkBoxDark = QtGui.QCheckBox(self.layoutWidget7)
        self.checkBoxDark.setCheckable(False)
        self.checkBoxDark.setObjectName(_fromUtf8("checkBoxDark"))
        self.verticalLayout_3.addWidget(self.checkBoxDark)
        self.checkBoxFlat = QtGui.QCheckBox(self.layoutWidget7)
        self.checkBoxFlat.setEnabled(True)
        self.checkBoxFlat.setCheckable(False)
        self.checkBoxFlat.setObjectName(_fromUtf8("checkBoxFlat"))
        self.verticalLayout_3.addWidget(self.checkBoxFlat)
        self.gridLayout_3.addWidget(self.widget_5, 1, 0, 1, 2)
        self.gridLayout_3.setColumnMinimumWidth(0, 200)
        self.gridLayout_3.setColumnStretch(0, 1)
        self.gridLayout_3.setColumnStretch(1, 4)
        self.gridLayout_3.setRowStretch(0, 10)
        self.gridLayout_3.setRowStretch(1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1072, 20))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuAbout = QtGui.QMenu(self.menubar)
        self.menuAbout.setObjectName(_fromUtf8("menuAbout"))
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
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionSettings = QtGui.QAction(MainWindow)
        self.actionSettings.setObjectName(_fromUtf8("actionSettings"))
        self.menuFile.addAction(self.actionNew_project)
        self.menuFile.addAction(self.actionOpen_project)
        self.menuFile.addAction(self.actionSave_project)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSettings)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuAbout.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())

        self.retranslateUi(MainWindow)
        self.toolBox.setCurrentIndex(3)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Mikko\'s Open Source Stacker", None))
        self.label.setText(_translate("MainWindow", "Project settings", None))
        self.label_6.setText(_translate("MainWindow", "Add", None))
        self.label_master.setText(_translate("MainWindow", "Add master", None))
        self.pushButtonMasterDark.setText(_translate("MainWindow", "Dark", None))
        self.pushButtonMasterBias.setText(_translate("MainWindow", "Bias", None))
        self.pushButtonMasterFlat.setText(_translate("MainWindow", "Flat", None))
        self.pushLight.setText(_translate("MainWindow", "Light", None))
        self.pushDark.setText(_translate("MainWindow", "Dark", None))
        self.pushBias.setText(_translate("MainWindow", "Bias", None))
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
        self.radioButtonGroth.setText(_translate("MainWindow", "Groth", None))
        self.label_9.setText(_translate("MainWindow", "Star matching", None))
        self.label_10.setText(_translate("MainWindow", "Image transformations", None))
        self.radioButtonScikit.setText(_translate("MainWindow", "Scikit-image", None))
        self.radioButtonImagick.setText(_translate("MainWindow", "ImageMagick", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.pageReg), _translate("MainWindow", "Registering", None))
        self.radioButtonMaximum.setText(_translate("MainWindow", "Maximum", None))
        self.radioButtonMinimum.setText(_translate("MainWindow", "Minimum", None))
        self.radioButtonMean.setText(_translate("MainWindow", "Mean", None))
        self.radioButtonMedian.setText(_translate("MainWindow", "Median", None))
        self.radioButtonSClip.setText(_translate("MainWindow", "Sigma Clipping", None))
        self.radioButtonSMedian.setText(_translate("MainWindow", "Sigma Median", None))
        self.label_kappa.setText(_translate("MainWindow", "κ coefficient", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.pageStack), _translate("MainWindow", "Stacking", None))
        self.label_2.setText(_translate("MainWindow", "Set workflow", None))
        self.checkBoxCalib.setText(_translate("MainWindow", "Calibrate", None))
        self.checkBoxDebayer.setText(_translate("MainWindow", "Debayer", None))
        self.checkBoxReg.setText(_translate("MainWindow", "Register", None))
        self.checkBoxStack.setText(_translate("MainWindow", "Stack", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.pageRun), _translate("MainWindow", "Workflow", None))
        self.label_7.setText(_translate("MainWindow", "Project name:", None))
        self.projectName.setText(_translate("MainWindow", "Not Set! Choose File -> New project", None))
        self.pushButtonRemoveFrame.setToolTip(_translate("MainWindow", "Remove the selected frame", None))
        self.pushButtonRemoveFrame.setText(_translate("MainWindow", "-", None))
        self.pushButtonMakeRef.setToolTip(_translate("MainWindow", "Selected frame will be made the reference frame", None))
        self.pushButtonMakeRef.setText(_translate("MainWindow", "Reference", None))
        self.pushButtonCrop.setText(_translate("MainWindow", "Crop", None))
        self.pushButtonRun.setText(_translate("MainWindow", "Run", None))
        self.label_8.setText(_translate("MainWindow", "Master frames", None))
        self.checkBoxBias.setText(_translate("MainWindow", "Bias", None))
        self.checkBoxDark.setText(_translate("MainWindow", "Dark", None))
        self.checkBoxFlat.setText(_translate("MainWindow", "Flat", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuAbout.setTitle(_translate("MainWindow", "Help", None))
        self.actionOpen_project.setText(_translate("MainWindow", "Open project", None))
        self.actionSave_project.setText(_translate("MainWindow", "Save project", None))
        self.actionNew_project.setText(_translate("MainWindow", "New project", None))
        self.actionExit.setText(_translate("MainWindow", "Exit", None))
        self.actionAbout.setText(_translate("MainWindow", "About", None))
        self.actionSettings.setText(_translate("MainWindow", "Settings", None))

from . import icons_rc
