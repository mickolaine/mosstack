# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AstroStack.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1072, 857)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/data/astrostack_icon128.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.toolBox = QtWidgets.QToolBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolBox.sizePolicy().hasHeightForWidth())
        self.toolBox.setSizePolicy(sizePolicy)
        self.toolBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.toolBox.setObjectName("toolBox")
        self.pageFrames = QtWidgets.QWidget()
        self.pageFrames.setGeometry(QtCore.QRect(0, 0, 200, 486))
        self.pageFrames.setObjectName("pageFrames")
        self.label_6 = QtWidgets.QLabel(self.pageFrames)
        self.label_6.setGeometry(QtCore.QRect(10, 0, 61, 20))
        self.label_6.setObjectName("label_6")
        self.label_master = QtWidgets.QLabel(self.pageFrames)
        self.label_master.setGeometry(QtCore.QRect(10, 160, 81, 20))
        self.label_master.setObjectName("label_master")
        self.widget = QtWidgets.QWidget(self.pageFrames)
        self.widget.setGeometry(QtCore.QRect(10, 180, 71, 81))
        self.widget.setObjectName("widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.pushButtonMasterDark = QtWidgets.QPushButton(self.widget)
        self.pushButtonMasterDark.setObjectName("pushButtonMasterDark")
        self.verticalLayout_2.addWidget(self.pushButtonMasterDark)
        self.pushButtonMasterBias = QtWidgets.QPushButton(self.widget)
        self.pushButtonMasterBias.setObjectName("pushButtonMasterBias")
        self.verticalLayout_2.addWidget(self.pushButtonMasterBias)
        self.pushButtonMasterFlat = QtWidgets.QPushButton(self.widget)
        self.pushButtonMasterFlat.setObjectName("pushButtonMasterFlat")
        self.verticalLayout_2.addWidget(self.pushButtonMasterFlat)
        self.verticalLayout_2.setStretch(0, 1)
        self.verticalLayout_2.setStretch(1, 1)
        self.verticalLayout_2.setStretch(2, 1)
        self.widget1 = QtWidgets.QWidget(self.pageFrames)
        self.widget1.setGeometry(QtCore.QRect(10, 20, 73, 106))
        self.widget1.setObjectName("widget1")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget1)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushLight = QtWidgets.QPushButton(self.widget1)
        self.pushLight.setObjectName("pushLight")
        self.verticalLayout.addWidget(self.pushLight)
        self.pushDark = QtWidgets.QPushButton(self.widget1)
        self.pushDark.setObjectName("pushDark")
        self.verticalLayout.addWidget(self.pushDark)
        self.pushBias = QtWidgets.QPushButton(self.widget1)
        self.pushBias.setObjectName("pushBias")
        self.verticalLayout.addWidget(self.pushBias)
        self.pushFlat = QtWidgets.QPushButton(self.widget1)
        self.pushFlat.setObjectName("pushFlat")
        self.verticalLayout.addWidget(self.pushFlat)
        self.toolBox.addItem(self.pageFrames, "")
        self.pageCalib = QtWidgets.QWidget()
        self.pageCalib.setGeometry(QtCore.QRect(0, 0, 200, 486))
        self.pageCalib.setObjectName("pageCalib")
        self.layoutWidget = QtWidgets.QWidget(self.pageCalib)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 0, 141, 241))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayoutCalibrate = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayoutCalibrate.setContentsMargins(0, 0, 0, 0)
        self.verticalLayoutCalibrate.setObjectName("verticalLayoutCalibrate")
        self.label_3 = QtWidgets.QLabel(self.layoutWidget)
        self.label_3.setObjectName("label_3")
        self.verticalLayoutCalibrate.addWidget(self.label_3)
        self.checkBoxDarkBias = QtWidgets.QCheckBox(self.layoutWidget)
        self.checkBoxDarkBias.setObjectName("checkBoxDarkBias")
        self.verticalLayoutCalibrate.addWidget(self.checkBoxDarkBias)
        self.label_4 = QtWidgets.QLabel(self.layoutWidget)
        self.label_4.setObjectName("label_4")
        self.verticalLayoutCalibrate.addWidget(self.label_4)
        self.checkBoxFlatBias = QtWidgets.QCheckBox(self.layoutWidget)
        self.checkBoxFlatBias.setObjectName("checkBoxFlatBias")
        self.verticalLayoutCalibrate.addWidget(self.checkBoxFlatBias)
        self.checkBoxFlatDark = QtWidgets.QCheckBox(self.layoutWidget)
        self.checkBoxFlatDark.setObjectName("checkBoxFlatDark")
        self.verticalLayoutCalibrate.addWidget(self.checkBoxFlatDark)
        self.label_5 = QtWidgets.QLabel(self.layoutWidget)
        self.label_5.setObjectName("label_5")
        self.verticalLayoutCalibrate.addWidget(self.label_5)
        self.checkBoxLightBias = QtWidgets.QCheckBox(self.layoutWidget)
        self.checkBoxLightBias.setObjectName("checkBoxLightBias")
        self.verticalLayoutCalibrate.addWidget(self.checkBoxLightBias)
        self.checkBoxLightDark = QtWidgets.QCheckBox(self.layoutWidget)
        self.checkBoxLightDark.setObjectName("checkBoxLightDark")
        self.verticalLayoutCalibrate.addWidget(self.checkBoxLightDark)
        self.checkBoxLightFlat = QtWidgets.QCheckBox(self.layoutWidget)
        self.checkBoxLightFlat.setObjectName("checkBoxLightFlat")
        self.verticalLayoutCalibrate.addWidget(self.checkBoxLightFlat)
        self.toolBox.addItem(self.pageCalib, "")
        self.pageDebayer = QtWidgets.QWidget()
        self.pageDebayer.setGeometry(QtCore.QRect(0, 0, 200, 486))
        self.pageDebayer.setObjectName("pageDebayer")
        self.layoutWidget1 = QtWidgets.QWidget(self.pageDebayer)
        self.layoutWidget1.setGeometry(QtCore.QRect(0, 0, 161, 111))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayoutDebayer = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayoutDebayer.setContentsMargins(0, 0, 0, 0)
        self.verticalLayoutDebayer.setObjectName("verticalLayoutDebayer")
        self.radioButtonBilinearCyt = QtWidgets.QRadioButton(self.layoutWidget1)
        self.radioButtonBilinearCyt.setObjectName("radioButtonBilinearCyt")
        self.buttonDebayer = QtWidgets.QButtonGroup(MainWindow)
        self.buttonDebayer.setObjectName("buttonDebayer")
        self.buttonDebayer.addButton(self.radioButtonBilinearCyt)
        self.verticalLayoutDebayer.addWidget(self.radioButtonBilinearCyt)
        self.radioButtonVNGCyt = QtWidgets.QRadioButton(self.layoutWidget1)
        self.radioButtonVNGCyt.setObjectName("radioButtonVNGCyt")
        self.buttonDebayer.addButton(self.radioButtonVNGCyt)
        self.verticalLayoutDebayer.addWidget(self.radioButtonVNGCyt)
        self.radioButtonBilinearCL = QtWidgets.QRadioButton(self.layoutWidget1)
        self.radioButtonBilinearCL.setObjectName("radioButtonBilinearCL")
        self.buttonDebayer.addButton(self.radioButtonBilinearCL)
        self.verticalLayoutDebayer.addWidget(self.radioButtonBilinearCL)
        self.radioButtonVNGCL = QtWidgets.QRadioButton(self.layoutWidget1)
        self.radioButtonVNGCL.setObjectName("radioButtonVNGCL")
        self.buttonDebayer.addButton(self.radioButtonVNGCL)
        self.verticalLayoutDebayer.addWidget(self.radioButtonVNGCL)
        self.toolBox.addItem(self.pageDebayer, "")
        self.pageReg = QtWidgets.QWidget()
        self.pageReg.setGeometry(QtCore.QRect(0, 0, 200, 486))
        self.pageReg.setObjectName("pageReg")
        self.layoutWidget2 = QtWidgets.QWidget(self.pageReg)
        self.layoutWidget2.setGeometry(QtCore.QRect(10, 40, 81, 31))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.verticalLayoutRegister = QtWidgets.QVBoxLayout(self.layoutWidget2)
        self.verticalLayoutRegister.setContentsMargins(0, 0, 0, 0)
        self.verticalLayoutRegister.setObjectName("verticalLayoutRegister")
        self.radioButtonGroth = QtWidgets.QRadioButton(self.layoutWidget2)
        self.radioButtonGroth.setObjectName("radioButtonGroth")
        self.buttonMatcher = QtWidgets.QButtonGroup(MainWindow)
        self.buttonMatcher.setObjectName("buttonMatcher")
        self.buttonMatcher.addButton(self.radioButtonGroth)
        self.verticalLayoutRegister.addWidget(self.radioButtonGroth)
        self.label_9 = QtWidgets.QLabel(self.pageReg)
        self.label_9.setGeometry(QtCore.QRect(10, 20, 101, 16))
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.pageReg)
        self.label_10.setGeometry(QtCore.QRect(10, 90, 161, 16))
        self.label_10.setObjectName("label_10")
        self.layoutWidget_2 = QtWidgets.QWidget(self.pageReg)
        self.layoutWidget_2.setGeometry(QtCore.QRect(10, 110, 121, 48))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.verticalLayoutRegister_2 = QtWidgets.QVBoxLayout(self.layoutWidget_2)
        self.verticalLayoutRegister_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayoutRegister_2.setObjectName("verticalLayoutRegister_2")
        self.radioButtonScikit = QtWidgets.QRadioButton(self.layoutWidget_2)
        self.radioButtonScikit.setObjectName("radioButtonScikit")
        self.buttonTransformer = QtWidgets.QButtonGroup(MainWindow)
        self.buttonTransformer.setObjectName("buttonTransformer")
        self.buttonTransformer.addButton(self.radioButtonScikit)
        self.verticalLayoutRegister_2.addWidget(self.radioButtonScikit)
        self.radioButtonImagick = QtWidgets.QRadioButton(self.layoutWidget_2)
        self.radioButtonImagick.setObjectName("radioButtonImagick")
        self.buttonTransformer.addButton(self.radioButtonImagick)
        self.verticalLayoutRegister_2.addWidget(self.radioButtonImagick)
        self.toolBox.addItem(self.pageReg, "")
        self.pageStack = QtWidgets.QWidget()
        self.pageStack.setGeometry(QtCore.QRect(0, 0, 200, 486))
        self.pageStack.setObjectName("pageStack")
        self.layoutWidget3 = QtWidgets.QWidget(self.pageStack)
        self.layoutWidget3.setGeometry(QtCore.QRect(10, 10, 117, 148))
        self.layoutWidget3.setObjectName("layoutWidget3")
        self.verticalLayoutStack = QtWidgets.QVBoxLayout(self.layoutWidget3)
        self.verticalLayoutStack.setContentsMargins(0, 0, 0, 0)
        self.verticalLayoutStack.setObjectName("verticalLayoutStack")
        self.radioButtonMaximum = QtWidgets.QRadioButton(self.layoutWidget3)
        self.radioButtonMaximum.setObjectName("radioButtonMaximum")
        self.buttonStack = QtWidgets.QButtonGroup(MainWindow)
        self.buttonStack.setObjectName("buttonStack")
        self.buttonStack.addButton(self.radioButtonMaximum)
        self.verticalLayoutStack.addWidget(self.radioButtonMaximum)
        self.radioButtonMinimum = QtWidgets.QRadioButton(self.layoutWidget3)
        self.radioButtonMinimum.setObjectName("radioButtonMinimum")
        self.buttonStack.addButton(self.radioButtonMinimum)
        self.verticalLayoutStack.addWidget(self.radioButtonMinimum)
        self.radioButtonMean = QtWidgets.QRadioButton(self.layoutWidget3)
        self.radioButtonMean.setObjectName("radioButtonMean")
        self.buttonStack.addButton(self.radioButtonMean)
        self.verticalLayoutStack.addWidget(self.radioButtonMean)
        self.radioButtonMedian = QtWidgets.QRadioButton(self.layoutWidget3)
        self.radioButtonMedian.setObjectName("radioButtonMedian")
        self.buttonStack.addButton(self.radioButtonMedian)
        self.verticalLayoutStack.addWidget(self.radioButtonMedian)
        self.radioButtonSClip = QtWidgets.QRadioButton(self.layoutWidget3)
        self.radioButtonSClip.setObjectName("radioButtonSClip")
        self.buttonStack.addButton(self.radioButtonSClip)
        self.verticalLayoutStack.addWidget(self.radioButtonSClip)
        self.radioButtonSMedian = QtWidgets.QRadioButton(self.layoutWidget3)
        self.radioButtonSMedian.setObjectName("radioButtonSMedian")
        self.buttonStack.addButton(self.radioButtonSMedian)
        self.verticalLayoutStack.addWidget(self.radioButtonSMedian)
        self.layoutWidget4 = QtWidgets.QWidget(self.pageStack)
        self.layoutWidget4.setGeometry(QtCore.QRect(10, 170, 141, 24))
        self.layoutWidget4.setObjectName("layoutWidget4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget4)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_kappa = QtWidgets.QLabel(self.layoutWidget4)
        self.label_kappa.setObjectName("label_kappa")
        self.horizontalLayout_2.addWidget(self.label_kappa)
        self.lineEditKappa = QtWidgets.QLineEdit(self.layoutWidget4)
        self.lineEditKappa.setObjectName("lineEditKappa")
        self.horizontalLayout_2.addWidget(self.lineEditKappa)
        self.toolBox.addItem(self.pageStack, "")
        self.pageRun = QtWidgets.QWidget()
        self.pageRun.setGeometry(QtCore.QRect(0, 0, 200, 486))
        self.pageRun.setObjectName("pageRun")
        self.label_2 = QtWidgets.QLabel(self.pageRun)
        self.label_2.setGeometry(QtCore.QRect(0, 0, 91, 16))
        self.label_2.setObjectName("label_2")
        self.layoutWidget5 = QtWidgets.QWidget(self.pageRun)
        self.layoutWidget5.setGeometry(QtCore.QRect(0, 20, 161, 123))
        self.layoutWidget5.setObjectName("layoutWidget5")
        self.verticalLayoutRun = QtWidgets.QVBoxLayout(self.layoutWidget5)
        self.verticalLayoutRun.setContentsMargins(0, 0, 0, 0)
        self.verticalLayoutRun.setObjectName("verticalLayoutRun")
        self.checkBoxCalib = QtWidgets.QCheckBox(self.layoutWidget5)
        self.checkBoxCalib.setObjectName("checkBoxCalib")
        self.verticalLayoutRun.addWidget(self.checkBoxCalib)
        self.checkBoxDebayer = QtWidgets.QCheckBox(self.layoutWidget5)
        self.checkBoxDebayer.setObjectName("checkBoxDebayer")
        self.verticalLayoutRun.addWidget(self.checkBoxDebayer)
        self.checkBoxReg = QtWidgets.QCheckBox(self.layoutWidget5)
        self.checkBoxReg.setObjectName("checkBoxReg")
        self.verticalLayoutRun.addWidget(self.checkBoxReg)
        self.checkBoxStack = QtWidgets.QCheckBox(self.layoutWidget5)
        self.checkBoxStack.setObjectName("checkBoxStack")
        self.verticalLayoutRun.addWidget(self.checkBoxStack)
        self.toolBox.addItem(self.pageRun, "")
        self.gridLayout_2.addWidget(self.toolBox, 1, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.tableView = QtWidgets.QTableView(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.setObjectName("tableView")
        self.gridLayout.addWidget(self.tableView, 1, 0, 1, 1)
        self.widget2 = QtWidgets.QWidget(self.centralwidget)
        self.widget2.setObjectName("widget2")
        self.formLayout = QtWidgets.QFormLayout(self.widget2)
        self.formLayout.setObjectName("formLayout")
        self.label_7 = QtWidgets.QLabel(self.widget2)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.projectName = QtWidgets.QLabel(self.widget2)
        self.projectName.setObjectName("projectName")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.projectName)
        self.gridLayout.addWidget(self.widget2, 0, 0, 1, 1)
        self.widget_2 = QtWidgets.QWidget(self.centralwidget)
        self.widget_2.setObjectName("widget_2")
        self.layoutWidget6 = QtWidgets.QWidget(self.widget_2)
        self.layoutWidget6.setGeometry(QtCore.QRect(0, 0, 801, 25))
        self.layoutWidget6.setObjectName("layoutWidget6")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget6)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButtonRemoveFrame = QtWidgets.QPushButton(self.layoutWidget6)
        self.pushButtonRemoveFrame.setObjectName("pushButtonRemoveFrame")
        self.horizontalLayout.addWidget(self.pushButtonRemoveFrame)
        self.pushButtonMakeRef = QtWidgets.QPushButton(self.layoutWidget6)
        self.pushButtonMakeRef.setObjectName("pushButtonMakeRef")
        self.horizontalLayout.addWidget(self.pushButtonMakeRef)
        self.pushButtonCrop = QtWidgets.QPushButton(self.layoutWidget6)
        self.pushButtonCrop.setObjectName("pushButtonCrop")
        self.horizontalLayout.addWidget(self.pushButtonCrop)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButtonRun = QtWidgets.QPushButton(self.layoutWidget6)
        self.pushButtonRun.setMinimumSize(QtCore.QSize(100, 0))
        self.pushButtonRun.setObjectName("pushButtonRun")
        self.horizontalLayout.addWidget(self.pushButtonRun)
        self.gridLayout.addWidget(self.widget_2, 2, 0, 1, 1)
        self.gridLayout.setRowMinimumHeight(2, 30)
        self.gridLayout_3.addLayout(self.gridLayout, 0, 1, 1, 1)
        self.widget_5 = QtWidgets.QWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(50)
        sizePolicy.setHeightForWidth(self.widget_5.sizePolicy().hasHeightForWidth())
        self.widget_5.setSizePolicy(sizePolicy)
        self.widget_5.setObjectName("widget_5")
        self.tableView_2 = QtWidgets.QTableView(self.widget_5)
        self.tableView_2.setGeometry(QtCore.QRect(220, 0, 841, 131))
        self.tableView_2.setObjectName("tableView_2")
        self.label_8 = QtWidgets.QLabel(self.widget_5)
        self.label_8.setGeometry(QtCore.QRect(10, 10, 111, 16))
        self.label_8.setObjectName("label_8")
        self.layoutWidget7 = QtWidgets.QWidget(self.widget_5)
        self.layoutWidget7.setGeometry(QtCore.QRect(10, 40, 121, 73))
        self.layoutWidget7.setObjectName("layoutWidget7")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.layoutWidget7)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.checkBoxBias = QtWidgets.QCheckBox(self.layoutWidget7)
        self.checkBoxBias.setCheckable(False)
        self.checkBoxBias.setObjectName("checkBoxBias")
        self.verticalLayout_3.addWidget(self.checkBoxBias)
        self.checkBoxDark = QtWidgets.QCheckBox(self.layoutWidget7)
        self.checkBoxDark.setCheckable(False)
        self.checkBoxDark.setObjectName("checkBoxDark")
        self.verticalLayout_3.addWidget(self.checkBoxDark)
        self.checkBoxFlat = QtWidgets.QCheckBox(self.layoutWidget7)
        self.checkBoxFlat.setEnabled(True)
        self.checkBoxFlat.setCheckable(False)
        self.checkBoxFlat.setObjectName("checkBoxFlat")
        self.verticalLayout_3.addWidget(self.checkBoxFlat)
        self.gridLayout_3.addWidget(self.widget_5, 1, 0, 1, 2)
        self.gridLayout_3.setColumnMinimumWidth(0, 200)
        self.gridLayout_3.setColumnStretch(0, 1)
        self.gridLayout_3.setColumnStretch(1, 4)
        self.gridLayout_3.setRowStretch(0, 10)
        self.gridLayout_3.setRowStretch(1, 2)
        self.widget_5.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1072, 20))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuAbout = QtWidgets.QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen_project = QtWidgets.QAction(MainWindow)
        self.actionOpen_project.setObjectName("actionOpen_project")
        self.actionSave_project = QtWidgets.QAction(MainWindow)
        self.actionSave_project.setObjectName("actionSave_project")
        self.actionNew_project = QtWidgets.QAction(MainWindow)
        self.actionNew_project.setObjectName("actionNew_project")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionSettings = QtWidgets.QAction(MainWindow)
        self.actionSettings.setObjectName("actionSettings")
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
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Mikko\'s Open Source Stacker"))
        self.label.setText(_translate("MainWindow", "Project settings"))
        self.label_6.setText(_translate("MainWindow", "Add"))
        self.label_master.setText(_translate("MainWindow", "Add master"))
        self.pushButtonMasterDark.setText(_translate("MainWindow", "Dark"))
        self.pushButtonMasterBias.setText(_translate("MainWindow", "Bias"))
        self.pushButtonMasterFlat.setText(_translate("MainWindow", "Flat"))
        self.pushLight.setText(_translate("MainWindow", "Light"))
        self.pushDark.setText(_translate("MainWindow", "Dark"))
        self.pushBias.setText(_translate("MainWindow", "Bias"))
        self.pushFlat.setText(_translate("MainWindow", "Flat"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.pageFrames), _translate("MainWindow", "Frames"))
        self.label_3.setText(_translate("MainWindow", "Dark frames"))
        self.checkBoxDarkBias.setText(_translate("MainWindow", "Subtract bias"))
        self.label_4.setText(_translate("MainWindow", "Flat frames"))
        self.checkBoxFlatBias.setText(_translate("MainWindow", "Subtract bias"))
        self.checkBoxFlatDark.setText(_translate("MainWindow", "Subtract dark"))
        self.label_5.setText(_translate("MainWindow", "Light frames"))
        self.checkBoxLightBias.setText(_translate("MainWindow", "Subtract bias"))
        self.checkBoxLightDark.setText(_translate("MainWindow", "Subtract dark"))
        self.checkBoxLightFlat.setText(_translate("MainWindow", "Divide by flat"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.pageCalib), _translate("MainWindow", "Calibrating"))
        self.radioButtonBilinearCyt.setText(_translate("MainWindow", "Bilinear Cython"))
        self.radioButtonVNGCyt.setText(_translate("MainWindow", "VNG Cython"))
        self.radioButtonBilinearCL.setText(_translate("MainWindow", "Bilinear OpenCL"))
        self.radioButtonVNGCL.setText(_translate("MainWindow", "VNG OpenCL"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.pageDebayer), _translate("MainWindow", "Debayering"))
        self.radioButtonGroth.setText(_translate("MainWindow", "Groth"))
        self.label_9.setText(_translate("MainWindow", "Star matching"))
        self.label_10.setText(_translate("MainWindow", "Image transformations"))
        self.radioButtonScikit.setText(_translate("MainWindow", "Scikit-image"))
        self.radioButtonImagick.setText(_translate("MainWindow", "ImageMagick"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.pageReg), _translate("MainWindow", "Registering"))
        self.radioButtonMaximum.setText(_translate("MainWindow", "Maximum"))
        self.radioButtonMinimum.setText(_translate("MainWindow", "Minimum"))
        self.radioButtonMean.setText(_translate("MainWindow", "Mean"))
        self.radioButtonMedian.setText(_translate("MainWindow", "Median"))
        self.radioButtonSClip.setText(_translate("MainWindow", "Sigma Clipping"))
        self.radioButtonSMedian.setText(_translate("MainWindow", "Sigma Median"))
        self.label_kappa.setText(_translate("MainWindow", "κ coefficient"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.pageStack), _translate("MainWindow", "Stacking"))
        self.label_2.setText(_translate("MainWindow", "Set workflow"))
        self.checkBoxCalib.setText(_translate("MainWindow", "Calibrate"))
        self.checkBoxDebayer.setText(_translate("MainWindow", "Debayer"))
        self.checkBoxReg.setText(_translate("MainWindow", "Register"))
        self.checkBoxStack.setText(_translate("MainWindow", "Stack"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.pageRun), _translate("MainWindow", "Workflow"))
        self.label_7.setText(_translate("MainWindow", "Project name:"))
        self.projectName.setText(_translate("MainWindow", "Not Set! Choose File -> New project"))
        self.pushButtonRemoveFrame.setToolTip(_translate("MainWindow", "Remove the selected frame"))
        self.pushButtonRemoveFrame.setText(_translate("MainWindow", "-"))
        self.pushButtonMakeRef.setToolTip(_translate("MainWindow", "Selected frame will be made the reference frame"))
        self.pushButtonMakeRef.setText(_translate("MainWindow", "Reference"))
        self.pushButtonCrop.setText(_translate("MainWindow", "Crop"))
        self.pushButtonRun.setText(_translate("MainWindow", "Run"))
        self.label_8.setText(_translate("MainWindow", "Master frames"))
        self.checkBoxBias.setText(_translate("MainWindow", "Bias"))
        self.checkBoxDark.setText(_translate("MainWindow", "Dark"))
        self.checkBoxFlat.setText(_translate("MainWindow", "Flat"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuAbout.setTitle(_translate("MainWindow", "Help"))
        self.actionOpen_project.setText(_translate("MainWindow", "Open project"))
        self.actionSave_project.setText(_translate("MainWindow", "Save project"))
        self.actionNew_project.setText(_translate("MainWindow", "New project"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionSettings.setText(_translate("MainWindow", "Settings"))

from . import icons_rc