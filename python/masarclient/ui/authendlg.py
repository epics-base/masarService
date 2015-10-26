'''
Created on Sept 06, 2013

@author: yhu
'''

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from PyQt4.QtGui import (QDialog, QVBoxLayout, QGridLayout, QLabel,
                         QDialogButtonBox, QLineEdit)
from PyQt4.QtCore import (QString, QObject, SIGNAL,Qt)

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class AuthenDlg(QDialog):
    def __init__(self, password, parent=None):
        super(AuthenDlg, self).__init__(parent)
        self.setWindowTitle('Authentication')
        self.password = password
        layout = QGridLayout(self)

        desc = QLabel()
        if self.password != "":#authentication is required only once Once it is correct
            desc.setText("Caution! your action will be recorded on the logbook\n \
Click OK if you want to continue, otherwise click Cancel")
        else: 
            desc.setText("Your action will be recorded on the logbook\n \
Please enter your password if you want to continue\n \
Otherwise Click Cancel \n")       
            self.passWdLineEdit = QLineEdit()
            self.passWdLineEdit.setEchoMode(QLineEdit.Password)
            vbox = QVBoxLayout()
            vbox.addWidget(self.passWdLineEdit)
            vbox.addStretch(1)    
            QObject.connect(self.passWdLineEdit, SIGNAL(_fromUtf8("textChanged(QString)")), 
                        self.getPassWd)
            layout.addWidget(self.passWdLineEdit,1,0,1,1)
        
        buttonBox = QDialogButtonBox()
        buttonBox.setOrientation(Qt.Horizontal)
        buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        QObject.connect(buttonBox, SIGNAL("rejected()"), self.reject)
        QObject.connect(buttonBox, SIGNAL("accepted()"), self.accept)
        
        layout.addWidget(desc,0,0,1,1)
        layout.addWidget(buttonBox,2,0,1,1)
        self.setLayout(layout)
            
    def getPassWd(self):
        self.password = str(self.passWdLineEdit.text())
         
    def accept(self, *args, **kwargs):
        self.isAccepted = True
        return QDialog.accept(self, *args, **kwargs)
    
    def reject(self, *args, **kwargs):
        self.isAccepted = False
        return QDialog.reject(self, *args, **kwargs)    
    
    def result(self):
        if not self.isAccepted:
            return None
        else:
            return (self.password)
        