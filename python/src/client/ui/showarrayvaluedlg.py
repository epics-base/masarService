'''
Created on Feb 27, 2012

@author: shengb
'''

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from PyQt4.QtGui import (QDialog, QTableView, QVBoxLayout, QLabel)
from PyQt4.QtCore import (QAbstractTableModel, QVariant, Qt)

class ShowArrayValueDlg(QDialog):
    
    def __init__(self, pvname, savedValue, liveValue=None, parent=None):
        super(ShowArrayValueDlg, self).__init__(parent)
        self.savedValue=savedValue
        self.liveValue=liveValue
        # create table
        tableview = self.createTable()

        # add label
        pvnameLabel = QLabel()
        label = 'Saved value (%s)' %(len(savedValue))
        if liveValue != None:
            label += ', Live value (%s)'%(len(liveValue))
        
        label += ' for\n  '+pvname
        pvnameLabel.setText(label)
        
        # layout
        layout = QVBoxLayout(self)

        # add pvname label
        layout.addWidget(pvnameLabel)
        #add table view
        layout.addWidget(tableview)
        self.setLayout(layout)
        
    def createTable(self):
        # create the view
        tableview = QTableView()
        
        # set table model
        tablemodel = ArrayDataTableModel(self.savedValue, self.liveValue, self)
        tableview.setModel(tablemodel)

        # hide vertical header
        vh = tableview.verticalHeader()
        vh.setVisible(False)

        # set horizontal header properties
        hh = tableview.horizontalHeader()
        hh.setStretchLastSection(True)

        # set column width to fit contents
        tableview.resizeColumnsToContents()
        
        # enable sorting
        # does not work
        # tableview.setSortingEnabled(True)

        return tableview
        
class ArrayDataTableModel(QAbstractTableModel):
    def __init__(self, savedData, liveData=None, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.savedData = savedData
        self.liveData = liveData
        
        if liveData == None:
            self.headerdata = ['saved value']
        else:
            self.headerdata = ['saved value', 'live data']
        
    def rowCount(self, parent):
        if self.liveData != None and len(self.liveData) > len(self.savedData):
            return len(self.liveData)
        else:
            return len(self.savedData)

    def columnCount(self, parent):
        return len(self.headerdata)

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        if index.column() == 0:
            if index.row() >= len(self.savedData):
                return QVariant('')
            else:
                return QVariant(self.savedData[index.row()])
        elif index.column() == 1:
            if index.row() >= len(self.liveData):
                return QVariant('')
            else:
                return QVariant(self.liveData[index.row()])
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()
    