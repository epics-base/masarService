'''
Created on April 28, 2014

@author: yhu
'''

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from PyQt4.QtGui import (QDialog, QGridLayout, QLineEdit, QPushButton, QBrush, QLabel)
from PyQt4.QtCore import (QString, QObject, SIGNAL, Qt)
import re, fnmatch
#from masar import masarUI #ImportError: cannot import name masarUI
try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class FindDlg(QDialog):
    #def __init__(self, info, parent=None):
    def __init__(self, tab, dlg, parent=None):
        super(FindDlg, self).__init__(parent, Qt.CustomizeWindowHint|Qt.WindowTitleHint)
        #self.setModal(False)
        #self.table = tab.currentWidget()
        self.tab = tab
        self.dlg = dlg
        #print(self.dlg)
        self.setWindowTitle('PV Search')
        self.pattern = ""
        self.foundPVCount = 0
        self.foundPVPos = []
        self.pvIndex = 0
        #self.pvListStr = ""
      
        self.findLineEdit = QLineEdit() 
        self.findLineEdit.setToolTip("use *, ? in the search pattern")
        QObject.connect(self.findLineEdit, SIGNAL(_fromUtf8("textChanged(QString)")), 
                        self.getPattern)        
        self.findNextButton =  QPushButton("> Next", self)
        self.findNextButton.setToolTip("Find next PV which matches the pattern")
        self.findNextButton.resize(self.findNextButton.sizeHint())
        self.findNextButton.clicked.connect(self.findNext)
        findPrevButton =  QPushButton("< Previous",self)
        findPrevButton.setToolTip("Find previous PV which matches the pattern")
        findPrevButton.resize(findPrevButton.sizeHint())
        findPrevButton.clicked.connect(self.findPrev)
        closeButton =  QPushButton("Close")
        closeButton.resize(closeButton.sizeHint())
        #closeButton.clicked.connect(self.close)
        closeButton.clicked.connect(self.cleanup)
        self.infoLabel = QLabel("%d PVs found"%self.foundPVCount)
        self.infoLabel.resize(self.infoLabel.sizeHint())
        
        layout = QGridLayout(self)
        layout.addWidget(self.findLineEdit,   0, 0, 1, 3)#row, col, how-many-rows, col-span
        layout.addWidget(self.findNextButton, 1, 0, 1, 1)
        layout.addWidget(findPrevButton,      1, 1, 1, 1)
        layout.addWidget(closeButton,         1, 2, 1, 1)
        layout.addWidget(self.infoLabel,      2, 0, 1, 3)
        self.setLayout(layout)
                
    def getPattern(self):
        self.pattern = str(self.findLineEdit.text())
        
    def highlightPV(self):
        table = self.tab.currentWidget()
        for j in range(table.rowCount()):
            table.item(j,0).setBackground(QBrush(Qt.white))
            
        pattern_ = self.pattern
        pattern = fnmatch.translate(pattern_)
        regex = re.compile(pattern, re.IGNORECASE)
        foundPVPos = []#pv position -- the row where PV is 
        for i in range(table.rowCount()):
            pvName = str(table.item(i,0).text())
            if regex.search(pvName):
                foundPVPos.append(i)
                table.item(i,0).setBackground(QBrush(Qt.yellow))
        
        self.foundPVCount = len(foundPVPos)
        #print(foundPVPos)
        if self.foundPVCount > 0:
            self.infoLabel.setText("%d PVs found: the first PV is at row #%d, the last @%d"
                               %(self.foundPVCount,foundPVPos[0]+1, foundPVPos[-1]+1))
        else:
            self.infoLabel.setText("No matching PV found. Remember to use * or ? for searching")
        return foundPVPos
         
    def findNext(self):
        table = self.tab.currentWidget()
        self.foundPVPos = self.highlightPV()
        #print("find next %d PVs: %s"%(self.foundPVCount, self.pattern))
        if self.foundPVCount>0:
            #print("pv index: %d"%self.pvIndex)
            if self.pvIndex >= self.foundPVCount or self.pvIndex < 0:
                self.pvIndex = 0 
            table.setCurrentCell(self.foundPVPos[self.pvIndex], 0)
            self.pvIndex += 1
            #print("next pv position: %d / %d"%(self.pvIndex, self.foundPVPos[self.pvIndex]))
                                                               
    def findPrev(self):
        table = self.tab.currentWidget()
        self.foundPVPos = self.highlightPV()
        #print("find prev %d PVs: %s"%(self.foundPVCount, self.pattern))
        if self.foundPVCount>0:
            #print("pv index: %d"%self.pvIndex)
            if self.pvIndex <= 0 or self.pvIndex >= self.foundPVCount:
                self.pvIndex = self.foundPVCount 
            self.pvIndex -= 1
            table.setCurrentCell(self.foundPVPos[self.pvIndex], 0)
            #print("prev pv position: %d / %d"%(self.pvIndex, self.foundPVPos[self.pvIndex]))

    def cleanup(self):
        #print("cleanup, then close")   
        self.dlg[0]=0 # make sure Find Dialog could pop up after it is closed    
        #print(self.dlg)
        table = self.tab.currentWidget()
        for i in range(len(self.foundPVPos)):
            table.item(self.foundPVPos[i],0).setBackground(QBrush(Qt.white))
        
        self.close()
    