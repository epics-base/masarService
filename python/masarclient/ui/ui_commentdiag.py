# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_commentdiag.ui'
#
# Created: Tue Feb 14 16:58:46 2012
#      by: PyQt4 UI code generator 4.8.6
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
        commentdlg.resize(416, 209)
        commentdlg.setWindowTitle(QtGui.QApplication.translate("commentdlg", "Comment", None, QtGui.QApplication.UnicodeUTF8))
        self.verticalLayout = QtGui.QVBoxLayout(commentdlg)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(commentdlg)
        self.label.setText(QtGui.QApplication.translate("commentdlg", "Author:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.authorLineEdit = QtGui.QLineEdit(commentdlg)
        self.authorLineEdit.setObjectName(_fromUtf8("authorLineEdit"))
        self.horizontalLayout.addWidget(self.authorLineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label_2 = QtGui.QLabel(commentdlg)
        self.label_2.setText(QtGui.QApplication.translate("commentdlg", "Comment:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.commentTextEdit = QtGui.QTextEdit(commentdlg)
        self.commentTextEdit.setObjectName(_fromUtf8("commentTextEdit"))
        self.verticalLayout.addWidget(self.commentTextEdit)
        self.buttonBox = QtGui.QDialogButtonBox(commentdlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.label.setBuddy(self.authorLineEdit)

        self.retranslateUi(commentdlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), commentdlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), commentdlg.reject)
        QtCore.QObject.connect(self.commentTextEdit, QtCore.SIGNAL(_fromUtf8("textChanged()")), commentdlg.on_commentTextEdit_textChanged)
        QtCore.QMetaObject.connectSlotsByName(commentdlg)
        commentdlg.setTabOrder(self.authorLineEdit, self.buttonBox)

    def retranslateUi(self, commentdlg):
        pass

