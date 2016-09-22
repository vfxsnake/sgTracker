# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LoginDialog.ui'
#
# Created: Tue Sep 20 16:22:02 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(411, 141)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(60, 100, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayoutWidget = QtGui.QWidget(Dialog)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 10, 391, 91))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.LogingLay = QtGui.QFormLayout(self.formLayoutWidget)
        self.LogingLay.setContentsMargins(0, 0, 0, 0)
        self.LogingLay.setObjectName("LogingLay")
        self.userLabel = QtGui.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setWeight(75)
        font.setBold(True)
        self.userLabel.setFont(font)
        self.userLabel.setObjectName("userLabel")
        self.LogingLay.setWidget(0, QtGui.QFormLayout.LabelRole, self.userLabel)
        self.passwordLabel = QtGui.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setWeight(75)
        font.setItalic(False)
        font.setBold(True)
        self.passwordLabel.setFont(font)
        self.passwordLabel.setObjectName("passwordLabel")
        self.LogingLay.setWidget(1, QtGui.QFormLayout.LabelRole, self.passwordLabel)
        self.userLineText = QtGui.QLineEdit(self.formLayoutWidget)
        self.userLineText.setEchoMode(QtGui.QLineEdit.Normal)
        self.userLineText.setObjectName("userLineText")
        self.LogingLay.setWidget(0, QtGui.QFormLayout.FieldRole, self.userLineText)
        self.passwordLineText = QtGui.QLineEdit(self.formLayoutWidget)
        self.passwordLineText.setEchoMode(QtGui.QLineEdit.Password)
        self.passwordLineText.setObjectName("passwordLineText")
        self.LogingLay.setWidget(1, QtGui.QFormLayout.FieldRole, self.passwordLineText)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Login Info", None, QtGui.QApplication.UnicodeUTF8))
        self.userLabel.setText(QtGui.QApplication.translate("Dialog", "UserName", None, QtGui.QApplication.UnicodeUTF8))
        self.passwordLabel.setText(QtGui.QApplication.translate("Dialog", "Password", None, QtGui.QApplication.UnicodeUTF8))

