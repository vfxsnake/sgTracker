# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'utility_notes.ui'
#
# Created: Wed Sep 21 18:55:36 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_DockWidget(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName("DockWidget")
        DockWidget.resize(481, 675)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.horizontalLayout = QtGui.QHBoxLayout(self.dockWidgetContents)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.projectNotesLay = QtGui.QVBoxLayout()
        self.projectNotesLay.setObjectName("projectNotesLay")
        self.utilitiesLay = QtGui.QVBoxLayout()
        self.utilitiesLay.setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)
        self.utilitiesLay.setObjectName("utilitiesLay")
        self.setProjectButton = QtGui.QPushButton(self.dockWidgetContents)
        self.setProjectButton.setObjectName("setProjectButton")
        self.utilitiesLay.addWidget(self.setProjectButton)
        self.downloadButton = QtGui.QPushButton(self.dockWidgetContents)
        self.downloadButton.setObjectName("downloadButton")
        self.utilitiesLay.addWidget(self.downloadButton)
        self.notesLay = QtGui.QVBoxLayout()
        self.notesLay.setObjectName("notesLay")
        self.notesLabel = QtGui.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.notesLabel.setFont(font)
        self.notesLabel.setObjectName("notesLabel")
        self.notesLay.addWidget(self.notesLabel)
        self.NoteTextEdit = QtGui.QTextEdit(self.dockWidgetContents)
        self.NoteTextEdit.setObjectName("NoteTextEdit")
        self.notesLay.addWidget(self.NoteTextEdit)
        self.replayButton = QtGui.QPushButton(self.dockWidgetContents)
        self.replayButton.setObjectName("replayButton")
        self.notesLay.addWidget(self.replayButton)
        self.attachButton = QtGui.QPushButton(self.dockWidgetContents)
        self.attachButton.setObjectName("attachButton")
        self.notesLay.addWidget(self.attachButton)
        self.utilitiesLay.addLayout(self.notesLay)
        self.projectNotesLay.addLayout(self.utilitiesLay)
        self.horizontalLayout.addLayout(self.projectNotesLay)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        DockWidget.setWindowTitle(QtGui.QApplication.translate("DockWidget", "DockWidget", None, QtGui.QApplication.UnicodeUTF8))
        self.setProjectButton.setText(QtGui.QApplication.translate("DockWidget", "Set Porject", None, QtGui.QApplication.UnicodeUTF8))
        self.downloadButton.setText(QtGui.QApplication.translate("DockWidget", "Download References", None, QtGui.QApplication.UnicodeUTF8))
        self.notesLabel.setText(QtGui.QApplication.translate("DockWidget", "Notes", None, QtGui.QApplication.UnicodeUTF8))
        self.replayButton.setText(QtGui.QApplication.translate("DockWidget", "Replay Note", None, QtGui.QApplication.UnicodeUTF8))
        self.attachButton.setText(QtGui.QApplication.translate("DockWidget", "Upload Attachment", None, QtGui.QApplication.UnicodeUTF8))

