# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'astrostack/imageDialog.ui'
#
# Created: Sun Dec  7 14:09:04 2014
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
        Dialog.resize(893, 754)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.scrollArea_2 = QtGui.QScrollArea(Dialog)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName(_fromUtf8("scrollArea_2"))
        self.scrollAreaWidgetContents_2 = QtGui.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 879, 706))
        self.scrollAreaWidgetContents_2.setObjectName(_fromUtf8("scrollAreaWidgetContents_2"))
        self.label = QtGui.QLabel(self.scrollAreaWidgetContents_2)
        self.label.setGeometry(QtCore.QRect(0, 0, 881, 711))
        self.label.setText(_fromUtf8(""))
        self.label.setObjectName(_fromUtf8("label"))
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.gridLayout.addWidget(self.scrollArea_2, 0, 0, 1, 1)
        self.widget = QtGui.QWidget(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMinimumSize(QtCore.QSize(0, 30))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.layoutWidget = QtGui.QWidget(self.widget)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 0, 701, 26))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_5.setMargin(0)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_x0 = QtGui.QLabel(self.layoutWidget)
        self.label_x0.setObjectName(_fromUtf8("label_x0"))
        self.horizontalLayout.addWidget(self.label_x0)
        self.lineEdit_x0 = QtGui.QLineEdit(self.layoutWidget)
        self.lineEdit_x0.setObjectName(_fromUtf8("lineEdit_x0"))
        self.horizontalLayout.addWidget(self.lineEdit_x0)
        self.horizontalLayout_5.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_x1 = QtGui.QLabel(self.layoutWidget)
        self.label_x1.setObjectName(_fromUtf8("label_x1"))
        self.horizontalLayout_2.addWidget(self.label_x1)
        self.lineEdit_x1 = QtGui.QLineEdit(self.layoutWidget)
        self.lineEdit_x1.setObjectName(_fromUtf8("lineEdit_x1"))
        self.horizontalLayout_2.addWidget(self.lineEdit_x1)
        self.horizontalLayout_5.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_y0 = QtGui.QLabel(self.layoutWidget)
        self.label_y0.setObjectName(_fromUtf8("label_y0"))
        self.horizontalLayout_3.addWidget(self.label_y0)
        self.lineEdit_y0 = QtGui.QLineEdit(self.layoutWidget)
        self.lineEdit_y0.setObjectName(_fromUtf8("lineEdit_y0"))
        self.horizontalLayout_3.addWidget(self.lineEdit_y0)
        self.horizontalLayout_5.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_y1 = QtGui.QLabel(self.layoutWidget)
        self.label_y1.setObjectName(_fromUtf8("label_y1"))
        self.horizontalLayout_4.addWidget(self.label_y1)
        self.lineEdit_y1 = QtGui.QLineEdit(self.layoutWidget)
        self.lineEdit_y1.setObjectName(_fromUtf8("lineEdit_y1"))
        self.horizontalLayout_4.addWidget(self.lineEdit_y1)
        self.horizontalLayout_5.addLayout(self.horizontalLayout_4)
        self.buttonBox = QtGui.QDialogButtonBox(self.widget)
        self.buttonBox.setGeometry(QtCore.QRect(710, 0, 161, 31))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.widget, 1, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label_x0.setText(_translate("Dialog", "<html><head/><body><p>X<span style=\" vertical-align:sub;\">0</span></p></body></html>", None))
        self.label_x1.setText(_translate("Dialog", "<html><head/><body><p>X<span style=\" vertical-align:sub;\">1</span></p></body></html>", None))
        self.label_y0.setText(_translate("Dialog", "<html><head/><body><p>Y<span style=\" vertical-align:sub;\">0</span></p></body></html>", None))
        self.label_y1.setText(_translate("Dialog", "<html><head/><body><p>Y<span style=\" vertical-align:sub;\">1</span></p></body></html>", None))

