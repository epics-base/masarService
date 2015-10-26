# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_commentdetail.ui'
#
# Created: Mon Apr 21 23:44:11 2014
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_commentdetail(object):
    def setupUi(self, commentdetail):
        commentdetail.setObjectName(_fromUtf8("commentdetail"))
        commentdetail.resize(416, 209)
        self.verticalLayout = QtGui.QVBoxLayout(commentdetail)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label_2 = QtGui.QLabel(commentdetail)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.commentTextEdit = QtGui.QTextEdit(commentdetail)
        self.commentTextEdit.setObjectName(_fromUtf8("commentTextEdit"))
        self.verticalLayout.addWidget(self.commentTextEdit)
        self.buttonBox = QtGui.QDialogButtonBox(commentdetail)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(commentdetail)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), commentdetail.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), commentdetail.reject)
        QtCore.QObject.connect(self.commentTextEdit, QtCore.SIGNAL(_fromUtf8("textChanged()")), commentdetail.on_commentTextEdit_textChanged)
        QtCore.QMetaObject.connectSlotsByName(commentdetail)

    def retranslateUi(self, commentdetail):
        commentdetail.setWindowTitle(QtGui.QApplication.translate("commentdetail", "Comment", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("commentdetail", "Put your detailed comment which will be shown in the Olog:", None, QtGui.QApplication.UnicodeUTF8))

