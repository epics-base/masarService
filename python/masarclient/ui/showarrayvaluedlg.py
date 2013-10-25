'''
Created on Feb 27, 2012

@author: shengb
'''

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from PyQt4.QtGui import (QDialog, QTableView, QGridLayout, QLabel, QPushButton)
from PyQt4.QtCore import (QString, SIGNAL, QAbstractTableModel, QVariant, Qt)

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class ShowArrayValueDlg(QDialog):
    def __init__(self, pvname, savedValue, liveValue=None, parent=None):
        super(ShowArrayValueDlg, self).__init__(parent)
        self.setWindowTitle('waveform data')
        
        self.savedValue=savedValue
        self.liveValue=liveValue
        # create table
        tableview = self.createTable()

        # add label
        pvnameLabel = QLabel()
        label = 'Saved value (%d data points)' %(len(savedValue))
        if liveValue != None:
            label += ' and live value (%d data points)'%(len(liveValue))
        
        label += ' for\n'+pvname
        pvnameLabel.setText(label)
        
        #add Close button
        self.quit = QPushButton('Close Widget', self)
        self.quit.resize(self.quit.sizeHint())
        self.connect(self.quit, SIGNAL('clicked()'), self.close)
        
        #add plot figure
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        #plot the waveform data
        self.plotWfData() 
          
        # layout
        #layout = QVBoxLayout(self)
        layout = QGridLayout(self)
        # add pvname label
        layout.addWidget(pvnameLabel)
        #add table view
        layout.addWidget(tableview)
        #add plot stuff and push button 
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.quit)
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
        
    def plotWfData(self):
        #fig, ax1 = plt.subplots
        #ax1.hold(False)
        ax1 = self.figure.add_subplot(111)
        assert(self.savedValue != None) 
        self.t = range(len(self.savedValue))
        if self.liveValue != None:
            self.t = range(max(len(self.savedValue), len(self.liveValue)))
            ax2 = ax1.twinx()
            ax2.plot(self.t, self.liveValue, 'r-')
            for t2 in ax2.get_yticklabels():
                t2.set_color('r')
            #self.canvas.draw()
            ax2.set_ylabel("Live data Value", color='r')             

        ax1.plot(self.t, self.savedValue, 'b-')
        for t1 in ax1.get_yticklabels():
            t1.set_color('b')
        self.canvas.draw()
        ax1.set_xlabel("Data Point")
        ax1.set_ylabel("Saved data Value", color='b')            
        ax1.grid(1)
        
class ArrayDataTableModel(QAbstractTableModel):
    def __init__(self, savedData, liveData=None, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.savedData = savedData
        self.liveData = liveData
        
        #get array info: max Number of Element and an array for the indexing
        if self.liveData != None and len(self.liveData) > len(self.savedData):
            self.maxNelm = len(self.liveData)
        else:
            self.maxNelm = len(self.savedData)
        self.idx = range(self.maxNelm)
        
        if liveData == None:
            self.headerdata = ['#', 'saved value']
        else:
            self.headerdata = ['#', 'saved value', 'live data']
        
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
            if index.row() >= self.maxNelm:
                return QVariant('')
            else:
                return QVariant(self.idx[index.row()])
        if index.column() == 1:
            if index.row() >= len(self.savedData):
                return QVariant('')
            else:
                return QVariant(self.savedData[index.row()])
        elif index.column() == 2:
            if index.row() >= len(self.liveData):
                return QVariant('')
            else:
                return QVariant(self.liveData[index.row()])
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()
    