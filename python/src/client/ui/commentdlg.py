
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from PyQt4.QtCore import (pyqtSignature)
from PyQt4.QtGui import (QApplication, QDialog, QDialogButtonBox)


import ui_commentdiag

class CommentDlg(QDialog,
        ui_commentdiag.Ui_commentdlg):

    def __init__(self, parent=None):
        super(CommentDlg, self).__init__(parent)
        self.setupUi(self)
        self.updateUi()
        self.authorLineEdit.setFocus()
        self.isAccepted = False

    def accept(self, *args, **kwargs):
        self.isAccepted = True
        return QDialog.accept(self, *args, **kwargs)

    def reject(self, *args, **kwargs):
        self.isAccepted = False
        return QDialog.reject(self, *args, **kwargs)    

    @pyqtSignature("QString")
    def on_authorLineEdit_textEdited(self, text):
        self.updateUi()

    @pyqtSignature("QString")
    def on_commentTextEdit_textChanged(self):
        self.updateUi()

    def updateUi(self):
        enable = (not self.authorLineEdit.text().isEmpty()) and (not self.commentTextEdit.toPlainText().isEmpty())
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enable)

    def result(self):
        if not self.isAccepted:
            return None
        else:
            return (unicode(self.authorLineEdit.text()), unicode(self.commentTextEdit.toPlainText()))

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

