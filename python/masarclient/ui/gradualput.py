'''
Created on July 23, 2014

@author: yhu
'''

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from PyQt4.QtGui import (QDialog, QGridLayout, QDialogButtonBox, QLineEdit, QPushButton, 
                         QLabel, QMessageBox)
from PyQt4.QtCore import (QString, QObject, SIGNAL, Qt)
import cothread
from cothread.catools import caget, caput
import traceback
try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class GradualPut(QDialog):
    def __init__(self, r_pvlist, r_data, r_dbrtype, no_restorepvs, parent=None):
        super(GradualPut, self).__init__(parent)
        if len(r_pvlist) != len(r_data):
            print("Odd: lengths of restore PV list and PV data are not the same")
            QMessageBox.warning(self, 'Warning', 
                    "No multiple-step gradual put: lengths of restore PV list and PV data are not the same.")
            return True #try one-step simple put
        
        self.rampPVList = []
        self.rampRestoreData = []
        noRampPVList = []
        self.setWindowTitle('Ramping machine using multiple-step gradual put')  
        dlgLayout = QGridLayout(self)
        dlgLabel = QLabel("Please enter the number of steps and the delay time between two steps. \n\
Click Yes when you are ready for the ramping, otherwise click No")
        dlgLayout.addWidget(dlgLabel, 0, 0, 1, 5)
        stepLabel = QLabel("Number of steps:")
        dlgLayout.addWidget(stepLabel, 1, 0, 1, 1)
        self.stepLineEdit = QLineEdit()
        self.stepLineEdit.setText("5")
        self.stepLineEdit.sizeHint()
        dlgLayout.addWidget(self.stepLineEdit, 1,1,1,1)
        emptyLabel = QLabel("        ")
        dlgLayout.addWidget(emptyLabel, 1,2,1,1)
        delayLabel = QLabel("Delay between steps (Seconds):")
        dlgLayout.addWidget(delayLabel, 1, 3, 1, 1)
        self.delayLineEdit = QLineEdit()
        self.delayLineEdit.setText("1")
        self.delayLineEdit.sizeHint()
        dlgLayout.addWidget(self.delayLineEdit, 1,4,1,1)
        totalRampingTimeLabel = QLabel("Total ramping time (Seconds):")
        dlgLayout.addWidget(totalRampingTimeLabel, 2, 0, 1, 1)
        self.totalRampingTimeLineEdit = QLineEdit()
        self.totalRampingTimeLineEdit.setText("5")
        self.totalRampingTimeLineEdit.sizeHint()
        dlgLayout.addWidget(self.totalRampingTimeLineEdit, 2,1,1,1)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)#Yes: 1; No: 0
        dlgLayout.addWidget(buttonBox,3,0,1,2)
        self.setLayout(dlgLayout)
        #Don't refer online Doc for QDialogButtonBox.Yes, QDialogButtonBox.No, rejected(), accepted() 
        #They are very confusing and seem wrong
        QObject.connect(buttonBox, SIGNAL(_fromUtf8("rejected()")), self.reject)#reject: 0
        QObject.connect(buttonBox, SIGNAL(_fromUtf8("accepted()")), self.accept)#accept: 1
        self.delayLineEdit.textChanged.connect(self.updateTotalRampingTime)
        self.stepLineEdit.textChanged.connect(self.updateTotalRampingTime)
        self.totalRampingTimeLineEdit.textChanged.connect(self.updateDelayTime)

        for i in range(len(r_pvlist)):
            #No string type: DBR_LONG(DOUBLE, etc.) or array with numbers
            if r_dbrtype[i] in [1, 2, 4, 5, 6] and  r_pvlist[i] not in no_restorepvs: 
                self.rampPVList.append(r_pvlist[i])
                self.rampRestoreData.append(r_data[i])
            else:
                noRampPVList.append(r_pvlist[i])
                
        if len(noRampPVList) > 0:
            print("No ramping put for these PVs because their values are not numbers or they are not accessible:")
            print(noRampPVList)
    
    def updateTotalRampingTime(self):
        try:
            totalRampingTime = float(self.delayLineEdit.text()) * int(self.stepLineEdit.text())
            self.totalRampingTimeLineEdit.setText(str(totalRampingTime))
        except:
            pass
            #print("Could not calculate total ramping time")
            #traceback.print_exc()

    def updateDelayTime(self):
        try:
            delayTime = float(self.totalRampingTimeLineEdit.text()) / int(self.stepLineEdit.text())
            self.delayLineEdit.setText(str(delayTime))
        except:
            pass
            #print("Could not calculate delay time")    
            #traceback.print_exc()         
       
    def rampingPut(self):
        try:
            step = int(self.stepLineEdit.text())
            delay = float(self.delayLineEdit.text())
        except:
            print("No ramping: wrong settings of Step or Delay time.")
            QMessageBox.warning(self, 'Warning', 'No ramping: wrong settings of Step or Delay time. Please try again')
            return
        #print("Number of steps: %d; Waiting time between steps: %d"%(step, delay))
        if step < 1:
            print("No ramping: number of steps can't be zero")
            QMessageBox.warning(self, 'Warning', 'No ramping: the number of Steps should be >=1. Please try again')
            return
        
        try:
            curValues = caget(self.rampPVList, timeout=2, throw=False)
        except:
            print("Oops: can't get PV values to ramp the machine, but will try one-step simple restore")
            traceback.print_exc()
            #QMessageBox.warning(self, 'Warning', "No multiple-step gradual put: some PVs seem disconnected")
            return True#try one-step simple put
        #print(self.rampPVList)
        #print(curValues)
        #print(self.rampRestoreData)
        try:
            stepSize = [(i - j)/step for i, j in zip(self.rampRestoreData, curValues)]
            #print(stepSize)
            for l in range(1, step):
                stepValues = [l * m + n for m, n in zip(stepSize, curValues)]
                #print(stepValues)
                caput(self.rampPVList, stepValues)
                cothread.Sleep(delay)             
        except:
            print("Oops: something wrong with ramping machine, but will try one-step simple restore")
            traceback.print_exc()
            #QMessageBox.warning(self, 'Warning', "Oops: something wrong with multiple-step gradual put")
            
        return True
        