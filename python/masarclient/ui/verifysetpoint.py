'''
Created on April 28, 2014

@author: yhu
'''

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from PyQt4.QtGui import (QDialog, QGridLayout, QTableWidget, QLineEdit, QPushButton, QBrush, 
                         QLabel, QSizePolicy, QTableWidgetItem, QDesktopWidget)
from PyQt4.QtCore import (QString, QObject, SIGNAL, Qt, QSize)
import cothread
from cothread.catools import caget, camonitor, FORMAT_TIME, connect
import threading, time, traceback
try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class VerifySetpoint(QDialog):
    def __init__(self, configFile, rowCount, verifyWindowDict, parent=None):
        super(VerifySetpoint, self).__init__(parent, Qt.CustomizeWindowHint|Qt.WindowTitleHint)
        self.configFile = configFile
        self.rowCount = rowCount
        self.verifyWindowDict = verifyWindowDict
        self.setWindowTitle('%s: setpoint v.s. readback'%self.configFile.split('/')[-1])  
        resolution = QDesktopWidget().screenGeometry()
        #self.setGeometry(resolution.width(), resolution.height() ,250, 150)
        self.setGeometry(resolution.width(),0, 250, 150)
        self.startUpdate = 1   
        self.keys = []       
        
        fd = open(self.configFile)
        lines = fd.readlines()
        #print(lines)
        setpointPVList = []
        readbackPVList = []
        self.allPVList = []
        #thresholdList = []
        rampRatePVList = []
        for line in lines:
            #print(line.split())
            setpointPVList.append(str(line.split()[0]))
            readbackPVList.append(str(line.split()[1]))
            if len(line.split())>2:
                #thresholdList.append(str(line.split()[2]))
                rampRatePVList.append(str(line.split()[2]))
        self.allPVList = setpointPVList + readbackPVList + rampRatePVList
        self.pvListColumn = 3
        #print(setpointPVList)
        #print(readbackPVList)
        #print(self.allPVList)
        #print(thresholdList) 
        #print(rampRatePVList)      
        
        layout = QGridLayout(self)  
        self.label = QLabel()
        if self.rowCount > len(readbackPVList):
            self.label.setText("%d PVs in the original snapshot, but only %d pairs of setpoint &\
readback PVs in this table because some setpoint PVs don't have readbacks\n\nPlease click the \
button below to update data\n"%(self.rowCount,len(readbackPVList)))   
        else:
            self.label.setText("%d pairs of setpoint & readback PVs in this table\n\n \
Please click the button below to update data\n"%(len(readbackPVList)))             
        layout.addWidget(self.label, 0, 0, 1, 2)
         
        self.table = QTableWidget()
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.table.sizePolicy().hasHeightForWidth())
        self.table.setSizePolicy(sizePolicy)
        self.table.setMinimumSize(QSize(700, 500))
        self.table.resize(self.table.sizeHint())
        
        self.table.setRowCount(len(setpointPVList))
        #if len(thresholdList):
        if len(rampRatePVList):
            #self.keys = ['setpoint PV','readback PV','SP value','RB value','diff', 'threshold']
            self.keys = ['setpoint PV','readback PV','SP value (Amp)','RB value (Amp)','diff', 'ramp-rate (Amp/Sec)']
        else:
            self.keys = ['setpoint PV','readback PV','SP value','RB value','diff']
        
        self.table.setColumnCount(len(self.keys))
        self.table.setHorizontalHeaderLabels(self.keys)             
        layout.addWidget(self.table, 1, 0, 1, 2)    

        #=======================================================================
        # toggleButton = QPushButton('Updating started', self)
        # toggleButton.clicked.connect(self.toggle)
        # layout.addWidget(toggleButton, 2, 0, 1, 1)
        #=======================================================================
        
        updateButton = QPushButton('Update Table', self)
        updateButton.clicked.connect(self.updateTable)
        layout.addWidget(updateButton, 2, 0, 1, 1)
        
        self.quit = QPushButton('Close Widget', self)
        #self.connect(self.quit, SIGNAL('clicked()'), self.close)
        #self.destroyed.connect(self.cleanup())
        #self.deleteLater.connect(self.cleanup())
        self.connect(self.quit, SIGNAL('clicked()'), self.cleanup)
        layout.addWidget(self.quit, 2, 1, 1, 1)
        self.setLayout(layout)    
        #self.timer = cothread.Timer(2, self.updateTable, retrigger=True, reuse=True)
        self.updateTable()
        #camonitor(self.allPVList, self.callback)
        #t = threading.Timer(2, self.updateTable)
        #t.start()  
    
    #===========================================================================
    # def toggle(self):
    #    source = self.sender()
    #    if self.startUpdate:
    #        source.setText("Updating stopped")
    #        self.startUpdate = 0
    #    else:
    #        source.setText("Updating started")
    #        self.startUpdate = 1
    #    print(self.startUpdate)    
    #===========================================================================
            
 
    def __setTableItem(self, table, row, col, text):
        item = table.item(row, col)
        if item:
            item.setText(text)
        else:
            newitem = QTableWidgetItem(text)
            newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
            table.setItem(row, col, newitem)    
        
    #def updateTable(self):
        #camonitor(self.allPVList, self.callback)
        #cothread.WaitForQuit()
       
    def updateTable(self):
    #def callback(self, value, index):
        #while(True):
            #if self.startUpdate: 
        disConnectedPVs = []
        connectedPVs = []
        self.table.clear()
        self.table.setHorizontalHeaderLabels(self.keys) 
        self.table.setSortingEnabled(False)
        #print("update table:")
        #print(self.allPVList)
        #cothread.Sleep(2)
        connnectionStatus = connect(self.allPVList, cainfo=True, wait=False, timeout=2, throw=False)
        for status in connnectionStatus:
            if status.ok != True:
                disConnectedPVs.append(status.name)
            else:
                connectedPVs.append(status.name)
        
        if len(disConnectedPVs) > 0:
            print("%d PVs seem disconnected: \n"%len(disConnectedPVs))
            print(disConnectedPVs)
            self.label.setText("%d PVs in the original snapshot, but only %d pairs of setpoint &\
readback in this table because some PVs don't have readbacks or they are disconnected\n\nPlease click the \
button below to update data\n"%(self.rowCount,len(connectedPVs)))
            self.allPVList = connectedPVs
        
        try:
            pvValues = caget(self.allPVList)
        except:
            print("Oops: can't get PV values to verify setpoint and readback")
            self.label.setText("Oops: can't get PV values to verify setpoint and readback\n\n")
            traceback.print_exc()
            return
        #print(pvValues)
        
        for i in range(int(len(self.allPVList)/self.pvListColumn)):
            self.__setTableItem(self.table, i, 0, str(self.allPVList[i]))#setpoint PV name
            self.__setTableItem(self.table, i, 1, str(self.allPVList[i+int(len(self.allPVList)/self.pvListColumn)]))
            self.__setTableItem(self.table, i, 2, str(pvValues[i]))
            self.__setTableItem(self.table, i, 3, str(pvValues[i+int(len(self.allPVList)/self.pvListColumn)]))
            diff_ = abs(pvValues[i] - pvValues[i+int(len(self.allPVList)/self.pvListColumn)])
            diff = diff_.__format__('.9f')
            self.__setTableItem(self.table, i, 4, str(diff))
            self.__setTableItem(self.table, i, 5, str(pvValues[i+int((self.pvListColumn-1)*len(self.allPVList)/self.pvListColumn)]))
    
        #self.table.resize(self.table.sizeHint())
        self.table.setSortingEnabled(True)
        self.table.sortItems(4,1)
        self.table.resizeColumnsToContents()
        #print("end of update table:")
        #return 2
        #self.timer.reset(2, retrigger=True)
                #time.sleep(2)
    def cleanup(self):
        del self.verifyWindowDict[self.configFile]#closed verifyWindow can be opened again
        self.close()
        