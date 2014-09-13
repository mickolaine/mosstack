# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings.ui'
#
# Created: Sat Sep 13 14:29:28 2014
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(511, 216)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(340, 170, 161, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.layoutWidget = QtGui.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 20, 481, 45))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_2 = QtGui.QLabel(self.layoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lineEditTemp = QtGui.QLineEdit(self.layoutWidget)
        self.lineEditTemp.setObjectName(_fromUtf8("lineEditTemp"))
        self.horizontalLayout.addWidget(self.lineEditTemp)
        self.pushButtonBrowseTemp = QtGui.QPushButton(self.layoutWidget)
        self.pushButtonBrowseTemp.setObjectName(_fromUtf8("pushButtonBrowseTemp"))
        self.horizontalLayout.addWidget(self.pushButtonBrowseTemp)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.layoutWidget1 = QtGui.QWidget(Dialog)
        self.layoutWidget1.setGeometry(QtCore.QRect(20, 160, 70, 42))
        self.layoutWidget1.setObjectName(_fromUtf8("layoutWidget1"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label = QtGui.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.label)
        self.comboBox = QtGui.QComboBox(self.layoutWidget1)
        self.comboBox.setEditable(True)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.verticalLayout_2.addWidget(self.comboBox)
        self.layoutWidget2 = QtGui.QWidget(Dialog)
        self.layoutWidget2.setGeometry(QtCore.QRect(20, 90, 481, 45))
        self.layoutWidget2.setObjectName(_fromUtf8("layoutWidget2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.layoutWidget2)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label_3 = QtGui.QLabel(self.layoutWidget2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout_3.addWidget(self.label_3)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lineEditSex = QtGui.QLineEdit(self.layoutWidget2)
        self.lineEditSex.setObjectName(_fromUtf8("lineEditSex"))
        self.horizontalLayout_2.addWidget(self.lineEditSex)
        self.pushButtonBrowseSex = QtGui.QPushButton(self.layoutWidget2)
        self.pushButtonBrowseSex.setObjectName(_fromUtf8("pushButtonBrowseSex"))
        self.horizontalLayout_2.addWidget(self.pushButtonBrowseSex)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.layoutWidget_2 = QtGui.QWidget(Dialog)
        self.layoutWidget_2.setGeometry(QtCore.QRect(110, 160, 91, 45))
        self.layoutWidget_2.setObjectName(_fromUtf8("layoutWidget_2"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.layoutWidget_2)
        self.verticalLayout_4.setMargin(0)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.label_memory = QtGui.QLabel(self.layoutWidget_2)
        self.label_memory.setObjectName(_fromUtf8("label_memory"))
        self.verticalLayout_4.addWidget(self.label_memory)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.lineEditSex_2 = QtGui.QLineEdit(self.layoutWidget_2)
        self.lineEditSex_2.setObjectName(_fromUtf8("lineEditSex_2"))
        self.horizontalLayout_3.addWidget(self.lineEditSex_2)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Program settings", None))
        self.label_2.setText(_translate("Dialog", "Working directory:", None))
        self.pushButtonBrowseTemp.setText(_translate("Dialog", "Browse", None))
        self.label.setText(_translate("Dialog", "Processes:", None))
        self.comboBox.setItemText(0, _translate("Dialog", "1", None))
        self.comboBox.setItemText(1, _translate("Dialog", "2", None))
        self.comboBox.setItemText(2, _translate("Dialog", "3", None))
        self.comboBox.setItemText(3, _translate("Dialog", "4", None))
        self.comboBox.setItemText(4, _translate("Dialog", "5", None))
        self.comboBox.setItemText(5, _translate("Dialog", "6", None))
        self.comboBox.setItemText(6, _translate("Dialog", "7", None))
        self.comboBox.setItemText(7, _translate("Dialog", "8", None))
        self.comboBox.setItemText(8, _translate("Dialog", "9", None))
        self.comboBox.setItemText(9, _translate("Dialog", "10", None))
        self.label_3.setText(_translate("Dialog", "SExtractor executable", None))
        self.pushButtonBrowseSex.setText(_translate("Dialog", "Browse", None))
        self.label_memory.setToolTip(_translate("Dialog", "How many megabytes you want to use for stacking process", None))
        self.label_memory.setText(_translate("Dialog", "Memory (MiB)", None))

