
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from PyQt4.QtCore import (pyqtSignature)
from PyQt4.QtGui import (QApplication, QDialog, QDialogButtonBox)

import ui_commentdiag

class CommentDlg(QDialog,
        ui_commentdiag.Ui_commentdlg):

    def __init__(self, parent=None):
        super(CommentDlg, self).__init__(parent)
        self.setupUi(self)
        self.userID = os.popen('whoami').read()[:-1]#username without \n
        self.authorInfo.setText("Author: "+self.userID)
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
    #def on_authorLineEdit_textEdited(self, text):
        #author = os.popen('whoami').read()
        #self.authorLineEdit.setText(str(author))
        #self.updateUi()

    @pyqtSignature("QString")
    def on_commentTextEdit_textChanged(self):
        self.updateUi()

    def updateUi(self):
        #enable = (not self.authorLineEdit.text().isEmpty()) and (not self.commentTextEdit.toPlainText().isEmpty())
        #enable = (not self.authorLineEdit.text().isEmpty()) and (not self.commentLineEdit.text().isEmpty())
        enable =  not self.commentLineEdit.text().isEmpty()
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enable)

    def result(self):
        if not self.isAccepted:
            return None
        else:
            #return (unicode(self.authorLineEdit.text()), unicode(self.commentLineEdit.text()))
            return (self.userID, unicode(self.commentLineEdit.text()))

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = CommentDlg()
    form.show()
    app.exec_()
    if form.isAccepted:
        print(form.result())
    else:
        print('Do nothing')

