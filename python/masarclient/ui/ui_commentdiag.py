# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'python/masarclient/ui/ui_commentdiag.ui'
#
# Created: Wed Oct  2 14:36:38 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_commentdlg(object):
    def setupUi(self, commentdlg):
        commentdlg.setObjectName(_fromUtf8("commentdlg"))
        commentdlg.resize(426, 135)
        self.gridLayout = QtGui.QGridLayout(commentdlg)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.commentLineEdit = QtGui.QLineEdit(commentdlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.commentLineEdit.sizePolicy().hasHeightForWidth())
        self.commentLineEdit.setSizePolicy(sizePolicy)
        self.commentLineEdit.setMinimumSize(QtCore.QSize(408, 0))
        self.commentLineEdit.setText(_fromUtf8(""))
        self.commentLineEdit.setMaxLength(80)
        self.commentLineEdit.setDragEnabled(True)
        self.commentLineEdit.setObjectName(_fromUtf8("commentLineEdit"))
        self.gridLayout.addWidget(self.commentLineEdit, 2, 0, 1, 2)
        self.label_2 = QtGui.QLabel(commentdlg)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.authorInfo = QtGui.QLabel(commentdlg)
        self.authorInfo.setObjectName(_fromUtf8("authorInfo"))
        self.horizontalLayout.addWidget(self.authorInfo)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(commentdlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 1, 1, 1)

        self.retranslateUi(commentdlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), commentdlg.reject)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), commentdlg.accept)
        QtCore.QObject.connect(self.commentLineEdit, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), commentdlg.on_commentTextEdit_textChanged)
        QtCore.QMetaObject.connectSlotsByName(commentdlg)

    def retranslateUi(self, commentdlg):
        commentdlg.setWindowTitle(QtGui.QApplication.translate("commentdlg", "Comment", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("commentdlg", "Concise Description (<80 characters):", None, QtGui.QApplication.UnicodeUTF8))
        self.authorInfo.setText(QtGui.QApplication.translate("commentdlg", "Author:", None, QtGui.QApplication.UnicodeUTF8))

