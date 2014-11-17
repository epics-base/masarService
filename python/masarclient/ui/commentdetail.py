
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from PyQt4.QtCore import (pyqtSignature)
from PyQt4.QtGui import (QApplication, QDialog, QDialogButtonBox)

import ui_commentdetail

class CommentDetail(QDialog,
        ui_commentdetail.Ui_commentdetail):

    def __init__(self, parent=None):
        super(CommentDetail, self).__init__(parent)
        self.setupUi(self)
        self.updateUi()
        #self.authorLineEdit.setFocus()
        self.isAccepted = False

    def accept(self, *args, **kwargs):
        self.isAccepted = True
        return QDialog.accept(self, *args, **kwargs)

    def reject(self, *args, **kwargs):
        self.isAccepted = False
        return QDialog.reject(self, *args, **kwargs)    

    @pyqtSignature("QString")
    def on_commentTextEdit_textChanged(self):
        self.updateUi()

    def updateUi(self):
        enable =  not self.commentTextEdit.toPlainText().isEmpty()
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enable)

    def result(self):
        if not self.isAccepted:
            return None
        else:
            return (unicode(self.commentTextEdit.toPlainText()))


