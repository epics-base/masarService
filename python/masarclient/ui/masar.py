#!/usr/bin/env python
'''
Created on Dec 1, 2011

@author: shengb
'''

from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals

import sys
import time
import datetime

from PyQt4.QtGui import (QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QTableWidget, QFileDialog)
from PyQt4.QtCore import (QDateTime, Qt, QString, QObject, SIGNAL)

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

if sys.version_info[:2]>=(2,7):
    from collections import OrderedDict as odict
else:
    print ('Python version 2.7 or higher is needed.')
    sys.exit()


import ui_masar
import commentdlg
from showarrayvaluedlg import ShowArrayValueDlg

import masarclient.masarClient as masarClient
from masarclient.channelRPC import epicsExit 

__version__ = "1.0.1"

def usage():
    print("""usage: masar.py [option]

command option:
-h  --help       help

masar.py v {0}. Copyright (c) 2011 Brookhaven National Laboratory. All rights reserved.
""".format(__version__))
    sys.exit()

# import this last to avoid import error on some platform and with different versions. 
import cothread.catools as cav3

class masarUI(QMainWindow, ui_masar.Ui_masar):
    severityDict= {0: 'NO_ALARM',
                   1: 'MINOR_ALARM',
                   2: 'MAJOR_ALARM',
                   3: 'INVALID_ALARM',
                   4: 'ALARM_NSEV'
    }
    
    alarmDict = { 0: 'NO_ALARM',
                 1: 'READ_ALARM',
                 2: 'WRITE_ALARM',
                 3: 'HIHI_ALARM',
                 4: 'HIGH_ALARM',
                 5: 'LOLO_ALARM',
                 6: 'LOW_ALARM',
                 7: 'STATE_ALARM',
                 8: 'COS_ALARM',
                 9: 'COMM_ALARM',
                 10: 'TIMEOUT_ALARM',
                 11: 'HW_LIMIT_ALARM',
                 12: 'CALC_ALARM',
                 13: 'SCAN_ALARM',
                 14: 'LINK_ALARM',
                 15: 'SOFT_ALARM',
                 16: 'BAD_SUB_ALARM',
                 17: 'UDF_ALARM',
                 18: 'DISABLE_ALARM',
                 19: 'SIMM_ALARM',
                 20: 'READ_ACCESS_ALARM',
                 21: 'WRITE_ACCESS_ALARM',
                 22: 'ALARM_NSTATUS'
    }

    def __init__(self, channelname='masarService', parent=None):
        super(masarUI, self).__init__(parent)
        self.setupUi(self)
        self.__setDateTime()
        self.tabWindowDict = {'comment': self.commentTab}
        self.e2cDict = {} # event to config dictionary
        self.pv4cDict = {} # pv name list for each selected configuration
        self.data4eid = {}
        self.arrayData = {} # store all array data
        
        self.__service = 'masar'
        self.mc = masarClient.client(channelname)
        
        self.__initSystemBomboBox()
        
        self.currentConfigFilter = str(self.configFilterLineEdit.text())
        self.eventConfigFilter = str(self.eventFilterLineEdit.text())
        self.authorText = str(self.authorTextEdit.text())
        self.UTC_OFFSET_TIMEDELTA = datetime.datetime.utcnow() - datetime.datetime.now()
        self.time_format = "%Y-%m-%d %H:%M:%S"
        self.previewId = None
        self.previewConfName = None
        self.isPreviewSaved = True

        # DBR_TYPE definition
        #define DBF_STRING  0
        #define DBF_INT     1
        #define DBF_SHORT   1
        #define DBF_FLOAT   2
        #define DBF_ENUM    3
        #define DBF_CHAR    4
        #define DBF_LONG    5
        #define DBF_DOUBLE  6
        self.epicsLong   = [1, 4, 5]
        self.epicsString = [0, 3]
        self.epicsDouble = [2, 6]
        self.epicsNoAccess = [7]

    def __initSystemBomboBox(self):
        self.systemCombox.addItem(_fromUtf8(""))
        self.systemCombox.setItemText(0, "all")
        results = self.getSystemList()
        if results:
            for i in range(len(results)):
                self.systemCombox.addItem(_fromUtf8(""))
                self.systemCombox.setItemText(i+1, results[i])
        self.system = str(self.systemCombox.currentText())

    def __setDateTime(self):
        self.eventStartDateTime.setDateTime(QDateTime.currentDateTime())
        self.eventEndDateTime.setDateTime(QDateTime.currentDateTime())
        
    def systemComboxChanged(self, qstring):
        self.system = str(qstring)
        
    def configFilterChanged(self):
        self.currentConfigFilter = str(self.configFilterLineEdit.text())

    def eventFilterChanged(self):
        self.eventConfigFilter = str(self.eventFilterLineEdit.text())

    def fetchConfigAction(self):
        self.setConfigTable()
        self.configTableWidget.resizeColumnsToContents()
        
    def authorTextChanged(self):
        self.authorText = str(self.authorTextEdit.text())
    
    def __getComment(self):
        cdlg = commentdlg.CommentDlg()
        cdlg.exec_()
        if cdlg.isAccepted:
            return (cdlg.result())
        else:
            return None
    
    def saveMachinePreviewAction(self):
        if self.isPreviewSaved:
            QMessageBox.warning(self,
                "Warning",
                "Preview (id: %s) for config (%s) has been save already." %(self.previewId, self.previewConfName))
            return
        elif self.previewId == None or self.previewConfName == None:
            QMessageBox.warning(self,
                "Warning",
                "No preview to save.")
        reply = QMessageBox.question(self, 'Message',
                             "Do you want to flag this preview as a good snapshot?",                                          
                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            comment = self.__getComment()
        else:
            return
        # comment result always returns a tuple
        # it return like (user, comment note)
        if comment and isinstance(comment, tuple):
            if comment[0] and comment[1]:
                self.saveMachinePreviewData(self.previewId, self.previewConfName, comment)
            else:
                QMessageBox.warning(self,
                    "Warning",
                    "Either user name or comment is empty.")
                return
        else:
            QMessageBox.warning(self,
                "Warning",
                "Comment is cancelled.")
            return
        self.isPreviewSaved = True

    def getMachinePreviewAction(self):
        selectedConfig = self.configTableWidget.selectionModel().selectedRows()
        lc = len(selectedConfig)
        if lc != 1:
            QMessageBox.warning(self,
                "Warning",
                "Please select one configuration, and one only.")
            return

        self.previewId = None
        self.previewConfName = None
        
        cname = str(self.configTableWidget.item(selectedConfig[0].row(), 0).text())
        result = self.getMachinePreviewData(cname)
        if result:
            eid = result[0]
            data = result[1]
            self.pv4cDict[str(eid)] = data['PV Name']
            self.data4eid[str(eid)] = data
            
            try:
                tabWidget = self.tabWindowDict['preview']
                index = self.snapshotTabWidget.indexOf(tabWidget)
            except:
                tabWidget = QTableWidget()
                index = self.snapshotTabWidget.count()
                self.tabWindowDict['preview'] = tabWidget
                QObject.connect(tabWidget, SIGNAL(_fromUtf8("cellDoubleClicked (int,int)")), self.__showArrayData)
            
            self.setSnapshotTable(data, tabWidget, eid)
            tabWidget.resizeColumnsToContents()
            label = QString.fromUtf8((cname+': Preview'))
            self.snapshotTabWidget.addTab(tabWidget, label)
    
            self.snapshotTabWidget.setTabText(index, label)        
            self.snapshotTabWidget.setCurrentIndex(index)
            
            self.previewId = eid
            self.previewConfName = cname
            self.isPreviewSaved = False
        
    def __find_key(self, dic, val):
        """return the key of dictionary dic given the value"""
        return [k for k, v in dic.iteritems() if v == val][0]

    def restoreSnapshotAction(self):
        curWidget = self.snapshotTabWidget.currentWidget()
        if not isinstance(curWidget, QTableWidget):
            QMessageBox.warning(self, 'Warning', 'No snapshot is selected yet.')
            return
        
        eid = self.__find_key(self.tabWindowDict, curWidget)
        if eid == 'comment' or eid == 'preview':
            QMessageBox.warning(self, 'Warning', 'No restore, preview is selected.')
            return
        selectedNoRestorePv = {}
        # get table rows
        rowCount = curWidget.rowCount()
        #Qt.Unchecked           0    The item is unchecked.
        #Qt.PartiallyChecked    1    The item is partially checked. 
        #                            Items in hierarchical models may be partially checked if some, 
        #                            but not all, of their children are checked.
        #Qt.Checked             2    The item is checked.
        for row in range(rowCount):
            selectedNoRestorePv[str(curWidget.item(row, 0).text())] = bool(curWidget.item(row, 8).checkState())
        pvlist = list(self.pv4cDict[str(eid)])
        data = self.data4eid[str(eid)]
        s_val = data['S_value']
        d_val = data['D_value']
        i_val = data['I_value']
        dbrtype = data['DBR']
        is_array = data['isArray']
        # is_connected = data['isConnected']
        # data['PV Name']
        array_value = data['arrayValue']
        
        r_pvlist = [] # restore all pv value in this list
        r_data = []   # value to be restored.
        no_restorepvs = []  # no restore from those pvs
        for index in range(len(pvlist)):
            try:
                # pv is unchecked, which means restore this pv
                if not selectedNoRestorePv[pvlist[index]]:
                    r_pvlist.append(pvlist[index])
                    if is_array[index]:
                        r_data.append(array_value[index])
                    elif dbrtype[index] in self.epicsDouble:
                        r_data.append(d_val[index])
                    elif dbrtype[index] in self.epicsLong:
                        r_data.append(i_val[index])
                    elif dbrtype[index] in self.epicsString:
                        r_data.append(s_val[index])
                    elif dbrtype[index] in self.epicsNoAccess:
                        QMessageBox.warning(self, 'Warning', 'Cannot restore machine. Value unknown for pv: %s'%(pvlist[index]))
                        return
                else:
                    no_restorepvs.append(pvlist[index])
            except:
                print (type(pvlist[index]), pvlist[index])
                QMessageBox.warning(self, 'Warning', 'PV (%s) not in the table.'%(pvlist[index]))
                return
    
        if len(no_restorepvs) == rowCount:
            QMessageBox.warning(self, 'Warning', 'All pvs are checked, and not restoring.')
            return
        if len(no_restorepvs) > 0:
            str_no_restore = "\n"
            for no_restorepv in no_restorepvs:
                str_no_restore += ' - %s' %no_restorepv + '\n'
            reply = QMessageBox.question(self, 'Message',
                                 "Partial pv will not be restored. Do you want to continue?\n(Please check terminal for a full list.)",                                          
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
#            reply = QMessageBox.question(self, 'Message',
#                                 "Partial pv will not be restored. Do you want to continue? %s" %str_no_restore,                                          
#                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
            print("No restore for the following pvs:\n"+str_no_restore+"\n========list end (not to restore pv)========")
        
        bad_pvs = []
        try:
            results = cav3.caput(r_pvlist, r_data, wait=True, throw=False)
            for i in range(len(results)):
                res = results[i]
                if not res.ok:
                    # try 3 times again to set value to each pv
                    # first try wait 1 second, second try wait 2 seconds, and last try wait 3 seconds.
                    for j in range(3):
                        res = cav3.caput(r_pvlist[i], r_data[i], wait=True, throw=False, timeout=j)
                        if res.ok:
                            break
                    if not res.ok:
                        # record as a bad pv if it still fails
                        bad_pvs.append(res)
        except:
            QMessageBox.warning(self, 'Warning', 'Error during restoring snapshot to live machine.')
            return
        
        if len(bad_pvs) > 0:
            message = "Failed to restore some pvs. PLease check the terminal for a full list."
            QMessageBox.warning(self, 'Warning', message)
            output = ""
            for bad_pv in bad_pvs:
                output += "\n  "+bad_pv.name + ": "+cav3.cadef.ca_message(bad_pv.errorcode)
            print ("Failed to restore the following pvs which is caused by:"+output+"\n========list end (failed to restore pv)========")
        else:
            QMessageBox.information(self, "Success", "Successfully restore machine with selected snapshot.")
        
    def __arrayTextFormat(self, arrayvalue):
        """
        display max 8 characters in a table cell
        """
        array_text = str(arrayvalue)

        if len(str(array_text)) > 8:
            array_text = str(array_text)[:8]+' ..., ...)'

        return array_text

    def getLiveMachineAction(self):
        curWidget = self.snapshotTabWidget.currentWidget()
        if isinstance(curWidget, QTableWidget):
            # get event id
            eid = self.__find_key(self.tabWindowDict, curWidget)
            # 2 special case:
            if eid == 'preview':
                eid = self.previewId # get event id for preview snapshot
            elif eid == 'comment':
                return # nothing should do here
            pvlist = self.pv4cDict[str(eid)]
            
            data = self.getLiveMachineData(pvlist)
            if data:
                channelName = data[0]
                s_value = data[1]
                d_value = data[2]
                i_value = data[3]
                dbrtype = data[4]
#                isConnected = data[5]
                is_array = data[6]
                array_value = data[7]

                dd = {}
                noMatchedPv = []
                
                # put channel name and its order into a dictionary
                for i in range(len(channelName)):
                    dd[str(channelName[i])] = i
                
                # get table rows
                rowCount = curWidget.rowCount()
                for i in range(rowCount):
                    try:
                        index = dd[str(curWidget.item(i, 0).text())]
                        if is_array[index]:
                            self.__setTableItem(curWidget, i, 6, self.__arrayTextFormat(array_value[index]))
                            self.arrayData[channelName[index]+"_"+str(eid)+'_live'] = array_value[index]
                        else:
                            if dbrtype[index] in self.epicsDouble:
                                self.__setTableItem(curWidget, i, 6, str(d_value[index]))
            
                                try:
                                    saved_val = float(str(curWidget.item(i, 5).text()))
                                    if d_value[index] != None:
                                        delta = d_value[index] - saved_val
                                        if abs(delta) < 1.0e-6:
                                            delta = 0
                                    else:
                                        delta = None
                                except:
                                    delta='N/A'
                                self.__setTableItem(curWidget, i, 7, str(delta))
                            elif dbrtype[index] in self.epicsLong:
                                self.__setTableItem(curWidget, i, 6, str(i_value[index]))
            
                                if dbrtype[index] in self.epicsNoAccess:
                                    pass
                                else:
                                    try:
                                        saved_val = int(float(str(curWidget.item(i, 5).text())))
                                        if i_value[index] != None:
                                            delta = i_value[index] - saved_val
                                        else:
                                            delta = None
                                    except:
                                        delta='N/A'
                                    self.__setTableItem(curWidget, i, 7, str(delta))
                            elif dbrtype[index] in self.epicsString:
                                self.__setTableItem(curWidget, i, 6, str(s_value[index]))
                    except:
                        noMatchedPv.append(str(curWidget.item(i, 0).text()))
                if len(noMatchedPv) > 0:
                    print ("Can not find the following pv for this snapshot: \n", noMatchedPv)
        else:
            QMessageBox.warning(self, "Warning", "Not a snapshot.")
            return
        
    def useTimeRange(self, state):
        if state == Qt.Checked:
            self.eventStartDateTime.setEnabled(True)
            self.eventEndDateTime.setEnabled(True)
        else:
            self.eventStartDateTime.setEnabled(False)
            self.eventEndDateTime.setEnabled(False)
            
    def fetchEventAction(self):
        selectedConfigs = self.configTableWidget.selectionModel().selectedRows()
        configIds=[]
        configNames = []
        for idx in selectedConfigs: 
            configIds.append(str(self.configTableWidget.item(idx.row(), 4).text()))
            configNames.append(str(self.configTableWidget.item(idx.row(), 0).text()))
        
        data = self.retrieveEventData(configids=configIds, confignames=configNames)
        if data:
            self.setEventTable(data)
            self.eventTableWidget.resizeColumnsToContents()
    
    def retrieveSnapshot(self):
        selectedItems = self.eventTableWidget.selectionModel().selectedRows()
        if len(selectedItems) <= 0:
            QMessageBox.warning(self,
                            "Warning",
                            "Please select at least one event.")
            return

        eventTs=[]
        eventNames=[]
        eventIds = []
        for idx in selectedItems: 
            eventNames.append(str(self.eventTableWidget.item(idx.row(), 0).text()))
            eventTs.append(str(self.eventTableWidget.item(idx.row(), 3).text()))
            eventIds.append(str(self.eventTableWidget.item(idx.row(), 4).text()))
            
        self.snapshotTabWidget.setStatusTip("Snapshot data")
        self.setSnapshotTabWindow(eventNames, eventTs, eventIds)
        
    def setConfigTable(self):
        data = self.retrieveConfigData()
        if data:
            self.setTable(data, self.configTableWidget)
    
    def setSnapshotTabWindow(self, eventNames, eventTs, eventIds):
        tabWidget = None
        isNew = True
        
        for i in range(len(eventIds)):
            if self.tabWindowDict.has_key(eventIds[i]):
                tabWidget = self.tabWindowDict[eventIds[i]]
            else:
                tabWidget = QTableWidget()
                self.tabWindowDict[eventIds[i]] = tabWidget
                QObject.connect(tabWidget, SIGNAL(_fromUtf8("cellDoubleClicked (int,int)")), self.__showArrayData)
            
            data = self.retrieveMasarData(eventid=eventIds[i])
            if data:
                if isNew:
                    for j in range(self.snapshotTabWidget.count(), 0, -1):
                        self.snapshotTabWidget.removeTab(j)
            
                    self.pv4cDict.clear()
                    self.data4eid.clear()
                    self.arrayData.clear()
                    isNew = False

                tabWidget.clear()
                self.setSnapshotTable(data, tabWidget, eventIds[i])
                tabWidget.resizeColumnsToContents()
                ts = eventTs[i].split('.')[0]
                
                label = QString.fromUtf8((eventNames[i]+': ' + ts))
                self.snapshotTabWidget.addTab(tabWidget, label)
                self.snapshotTabWidget.setTabText(i+1, label)
                self.pv4cDict[str(eventIds[i])] = data['PV Name']
                self.data4eid[str(eventIds[i])] = data
            
        self.snapshotTabWidget.setCurrentIndex(1)
        
    def __showArrayData(self, row, column):
        if column != 5 and column != 6: # display the array value only
            return
        curWidget = self.snapshotTabWidget.currentWidget()
        if not isinstance(curWidget, QTableWidget):
            QMessageBox.warning(self, 'Warning', 'No snapshot is selected yet.')
            return
        
        eid = self.__find_key(self.tabWindowDict, curWidget)
        if eid == 'comment':
            QMessageBox.warning(self, 'Warning', 'It is comment panel.')

        if eid == 'preview':
            eid = self.previewId
        pvname = str(curWidget.item(row, 0).text())
        try:
            arraySaved = self.arrayData[pvname+'_'+str(eid)]
        except:
            QMessageBox.warning(self, 'Warning', 'No array data found for this pv.')
            return
        if eid != 'preview':
            try:
                arrayLive = self.arrayData[pvname+"_"+str(eid)+'_live']
                arrardlg = ShowArrayValueDlg(pvname, arraySaved, arrayLive)
            except:
                arrardlg = ShowArrayValueDlg(pvname, arraySaved)
        else:
            arrardlg = ShowArrayValueDlg(pvname, arraySaved)
        arrardlg.exec_()
    
    def setEventTable(self, data):
        self.setTable(data, self.eventTableWidget)

    def __setTableItem(self, table, row, col, text):
        item = table.item(row, col)
        if item:
            item.setText(text)
        else:
            newitem = QTableWidgetItem(text)
            newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
            table.setItem(row, col, newitem)
                
    def setSnapshotTable(self, data, table, eventid):
        if data:
            length = len(data.values()[0])
        else:
            print ('data is empty, exit.')
            return
        
        for i in range(1, len(data.values())):
            if length != len(data.values()[i]):
                QMessageBox.warning(self,
                                    "Warning",
                                    "Data length are not consistent.")

                return

        if isinstance(data, odict) and isinstance(table, QTableWidget):
            table.setSortingEnabled(False)
            table.clear()
        
            nrows = len(data.values()[0])
            #    ('pv name label',  'dbr_type label', 'string value', 'int value', 'double value', 'status label', 'severity label', 
            #     'ioc time stamp label', 'ioc time stamp nano label', 'is_array', 'array_value'),
            # => (pv_name, status, severity, ioc_timestamp, saved value)
            # ncols = len(data) - 6
            # ncols = ncols + 3  # 2 columns for live data and (live data - saved data), selected restore pv
            ncols = len(data) - 3
            table.setRowCount(nrows)
            table.setColumnCount(ncols)
            
            pvnames = data['PV Name']
            status = data['Status']
            severity = data['Severity']
            ts = data['Time stamp']
            ts_nano = data['Time stamp (nano)']
            dbrtype = data['DBR']
            s_value = data['S_value']
            i_value = data['I_value']
            d_value = data['D_value']
            isConnected = data['isConnected']
            is_array = data['isArray'] 
            array_value = data['arrayValue']
            
            keys = ['Name', 'Status', 'Severity', 'Time Stamp', 'Connection', 'Saved Value', 'Live Value', 'Delta', 'Not Restore']
            table.setHorizontalHeaderLabels(keys)
            
            for i in range(nrows):
                item = table.item(i, 8)
                if item:
                    item.setCheckState(False)
                else:
                    newitem = QTableWidgetItem()
                    newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsUserCheckable)
                    table.setItem(i, 8, newitem)
                    newitem.setCheckState(False)

                if pvnames[i]:
                    self.__setTableItem(table, i, 0, pvnames[i])
                if status[i]:
                    self.__setTableItem(table, i, 1, str(status[i]))
                if severity[i]:
                    self.__setTableItem(table, i, 2, str(severity[i]))
                if ts[i]:
                    dt = str(datetime.datetime.fromtimestamp(ts[i]+ts_nano[i]*1.0e-9))
                    self.__setTableItem(table, i, 3, dt)
                if isConnected[i]:
                    self.__setTableItem(table, i, 4, str(bool(isConnected[i])))
                if is_array[i]:
                    self.__setTableItem(table, i, 5, self.__arrayTextFormat(array_value[i]))
                    self.arrayData[pvnames[i]+'_'+str(eventid)] = array_value[i]
                else:
                    if dbrtype[i] in self.epicsDouble:
                        self.__setTableItem(table, i, 5, str(d_value[i]))
                    elif dbrtype[i] in self.epicsLong:
                        self.__setTableItem(table, i, 5, str(i_value[i]))
                    elif dbrtype[i] in self.epicsString:
                        self.__setTableItem(table, i, 5, str(s_value[i]))
                    elif dbrtype[i] in self.epicsNoAccess:
                        # channel are not connected.
                        pass
                    else:
                        print('invalid dbr type (code = %s)'%(dbrtype[i]))
            table.setSortingEnabled(True)
        else:
            raise "Either given data is not an instance of OrderedDict or table is not an instance of QtGui.QTableWidget"

    def setTable(self, data, table):
        """
        Set data view.
        The data has to be an ordered dictionary, and table is a QtGui.QTableWidget
        Here is an example to construct an ordered dictionary.
        """
        if data:
            length = len(data.values()[0])
        else:
            print ('data is empty, exit.')
            return
        for i in range(1, len(data.values())):
            if length != len(data.values()[i]):
                QMessageBox.warning(self,
                                    "Warning",
                                    "Data length are not consistent.")

                return

        if isinstance(data, odict) and isinstance(table, QTableWidget):
            nrows = len(data.values()[0])
            ncols = len(data)
            table.setRowCount(nrows)
            table.setColumnCount(ncols)
            # Removes all items in the view, and also all selections
            table.clear()
            table.setHorizontalHeaderLabels(data.keys())
            
            n = 0
            for key in data:
                m = 0
                for item in data[key]:
                    if not isinstance(item, basestring):
                        item = str(item)
                    if item:
                        newitem = QTableWidgetItem(item)
                        newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
                        table.setItem(m, n, newitem)
                    m += 1
                n += 1
        else:
            raise "Either given data is not an instance of OrderedDict or table is not an instance of QtGui.QTableWidget"

    def getSystemList(self):
        try:
            return self.mc.retrieveSystemList()
        except:
            QMessageBox.warning(self,
                                "Warning",
                                "Cannot connect to MASAR server.\nPlease check the serviceName, network connection, and service status.")

            return
    
    def retrieveConfigData(self):
        data = odict()

        params = {"system": self.system,
                  "servicename": self.__service,
                  "configname": self.currentConfigFilter}
        try:
            rpcResult = self.mc.retrieveServiceConfigs(params)
            
            utctimes = rpcResult[3]
            config_ts = []
            for ut in utctimes:
                ts = str(datetime.datetime.fromtimestamp(time.mktime(time.strptime(ut, self.time_format))) - self.UTC_OFFSET_TIMEDELTA)
                config_ts.append(ts)

        except:
            QMessageBox.warning(self,
                                "Warning",
                                "Exception happened during retrieving configurations.")
            return False
        
        if not rpcResult:
            return False
        
        data['Name'] = rpcResult[1]
        data['Description'] = rpcResult[2]
        data['Date'] = config_ts
        data['Version'] = rpcResult[4]
        data['Id'] = rpcResult[0]
        return data
    
    def retrieveEventData(self,configids=None,confignames=None):
        start = None
        end = None
        if self.timeRangeCheckBox.isChecked():
            start = self.eventStartDateTime.dateTime().toPyDateTime() + self.UTC_OFFSET_TIMEDELTA
            end = self.eventEndDateTime.dateTime().toPyDateTime() + self.UTC_OFFSET_TIMEDELTA
            if start > end:
                QMessageBox.warning(self,
                            "Warning",
                            "Please select a correct time range.")
                return

        event_ids = []
        event_ts = []
        event_desc = []
        c_names = []
        event_author = []
        self.e2cDict.clear()

        if configids:
            for i in range(len(configids)):
                cid = configids[i]
                params = {'configid': cid,
                          "comment": self.eventConfigFilter,
                          "user": self.authorText}
                if self.timeRangeCheckBox.isChecked():
                    params['start'] = str(start)
                    params['end'] = str(end)
                try:
                    rpcResult = self.mc.retrieveServiceEvents(params)
                except:
                    QMessageBox.warning(self,
                                "Warning",
                                "Except happened during retrieving events.")
                    return False
                if not rpcResult:
                    return False
                eids = rpcResult[0]
                usertag = rpcResult[1]
                utctimes = rpcResult[2]
                author = rpcResult[3]

                event_ids = event_ids[:] + (list(eids))[:]
                event_desc = event_desc[:] + (list(usertag))[:]
                event_author = event_author[:] + (list(author))[:]
                for j in range(len(eids)):
                    self.e2cDict[str(eids[j])] = [cid, usertag[j],confignames[i]]
                for ut in utctimes:
                    c_names.append(confignames[i])
                    ts = str(datetime.datetime.fromtimestamp(time.mktime(time.strptime(ut, self.time_format))) - self.UTC_OFFSET_TIMEDELTA)
                    event_ts.append(ts)
        else:
            return False
                    
        data = odict()
        data['Config'] = c_names
        data['Description'] = event_desc
        data['Author'] = event_author
        data['Time stamp'] = event_ts
        data['Id'] = event_ids
        return data

    def retrieveMasarData(self, eventid=None):
        data = odict()

        params = {'eventid': eventid}
        
        try:
            rpcResult = self.mc.retrieveSnapshot(params)
        except:
            QMessageBox.warning(self,
                                "Warning",
                                "Except happened during retrieving snapshot data.")
            return False
        if not rpcResult:
            return False
        pvnames = rpcResult[0]
        s_value = rpcResult[1]
        d_value = rpcResult[2]
        i_value = rpcResult[3]
        dbrtype = rpcResult[4]
        isConnected = rpcResult[5]
        ts = rpcResult[6]
        ts_nano = rpcResult[7]
        severity = list(rpcResult[8])
        status = list(rpcResult[9])
        is_array = rpcResult[10]
        raw_array_value  = rpcResult[11]
        
        array_value = []
        for i in range(len(severity)):
            try:
                severity[i] = self.severityDict[severity[i]]
            except:
                severity[i] = 'N/A'
            try:
                status[i] = self.alarmDict[status[i]]
            except:
                status[i] = 'N/A'

            if dbrtype[i] in self.epicsLong:
                array_value.append(raw_array_value[i][2])
            elif dbrtype[i] in self.epicsDouble:
                array_value.append(raw_array_value[i][1])
            elif dbrtype[i] in self.epicsString:
                # string value
                array_value.append(raw_array_value[i][0])
            elif dbrtype[i] in self.epicsNoAccess:
                # when the value is no_access, use the double value no matter what it is
                array_value.append(raw_array_value[i][1])

        data['PV Name'] = pvnames
        data['Status'] = status
        data['Severity'] = severity
        data['Time stamp'] = ts
        data['Time stamp (nano)'] = ts_nano
        data['DBR'] = dbrtype
        data['S_value'] = s_value
        data['I_value'] = i_value
        data['D_value'] = d_value
        data['isConnected'] = isConnected
        data['isArray'] = is_array
        data['arrayValue'] = array_value
        
        return data

    def saveMachinePreviewData(self, eventid, confname, comment):
        if not eventid:
            QMessageBox.warning(self,
                        "Warning",
                        "Unknown event.")
            return

        params = {'eventid':    str(eventid),
                  'configname': str(confname),
                  'user':       str(comment[0]),
                  'desc':       str(comment[1])}
        try:
            result = self.mc.updateSnapshotEvent(params)
        except:
            QMessageBox.warning(self,
                                "Warning",
                                "Except happened during update snapshot event.")
            return False
        if result:
            QMessageBox.information(self,"Successful", 
                                    " Succeed to save preview")
        else:
            QMessageBox.information(self, "Failures",
                                    "Failed to save preview.")

    def getMachinePreviewData(self, configName):
        params = {'configname': configName,
                  'servicename': 'masar'}
        
        try:
            rpcResult = self.mc.saveSnapshot(params)
        except:
            QMessageBox.warning(self,
                                "Warning",
                                "Except happened during getting machine preview.")
            return False
        if not rpcResult:
            return False
        eventid = rpcResult[0]
        pvnames = rpcResult[1]
        s_value = rpcResult[2]
        d_value = rpcResult[3]
        i_value = rpcResult[4]
        dbrtype = rpcResult[5]
        isConnected = rpcResult[6]
        ts = rpcResult[7]
        ts_nano = list(rpcResult[8])
        severity = list(rpcResult[9])
        status = list(rpcResult[10])
        is_array = rpcResult[11]
        raw_array_value  = rpcResult[12]

        array_value = []
        for i in range(len(severity)):
            try:
                severity[i] = self.severityDict[severity[i]]
            except:
                severity[i] = 'N/A'
            try:
                status[i] = self.alarmDict[status[i]]
            except:
                status[i] = 'N/A'

            if dbrtype[i] in self.epicsLong:
                array_value.append(raw_array_value[i][2])
            elif dbrtype[i] in self.epicsDouble:
                array_value.append(raw_array_value[i][1])
            elif dbrtype[i] in self.epicsString:
                # string value
                array_value.append(raw_array_value[i][0])
            elif dbrtype[i] in self.epicsNoAccess:
                # when the value is no_access, use the double value no matter what it is
                array_value.append(raw_array_value[i][1])
        
        data = odict()
        data['PV Name'] = pvnames
        data['Status'] = status
        data['Severity'] = severity
        data['Time stamp'] = ts
        data['Time stamp (nano)'] = ts_nano
        data['DBR'] = dbrtype
        data['S_value'] = s_value
        data['I_value'] = i_value
        data['D_value'] = d_value
        data['isConnected'] = isConnected
        data['isArray'] = is_array
        data['arrayValue'] = array_value

        return (eventid, data)
        
    def getLiveMachineData(self, pvlist):
        params = {}
        for pv in pvlist:
            params[pv] = pv
        # channelName,stringValue,doubleValue,longValue,dbrType,isConnected, is_array, array_value
        array_value = []
        try:
            rpcResult = self.mc.getLiveMachine(params)
        except:
            QMessageBox.warning(self,
                                "Warning",
                                "Except happened during getting live machine.")
            return False
        if not rpcResult:
            return False
        channelName = rpcResult[0]
        stringValue = rpcResult[1]
        doubleValue = rpcResult[2]
        longValue = rpcResult[3]
        dbrtype = rpcResult[4]
        isConnected = rpcResult[5]
        is_array = rpcResult[6]
        raw_array_value = rpcResult[7]
        for i in range(len(is_array)):
            if dbrtype[i] in self.epicsLong:
                array_value.append(raw_array_value[i][2])
            elif dbrtype[i] in self.epicsDouble:
                array_value.append(raw_array_value[i][1])
            elif dbrtype[i] in self.epicsString:
                # string value
                array_value.append(raw_array_value[i][0])
            elif dbrtype[i] in self.epicsNoAccess:
                # when the value is no_access, use the double value no matter what it is
                array_value.append(raw_array_value[i][1])
        
        return (channelName,stringValue,doubleValue,longValue,dbrtype,isConnected,is_array, array_value)

    def saveDataFileAction(self):
        """
        Save data into a CSV file.
        """
        curWidget = self.snapshotTabWidget.currentWidget()
        if not isinstance(curWidget, QTableWidget):
            QMessageBox.warning(self, 'Warning', 'No snapshot is selected yet.')
            return
        eid = self.__find_key(self.tabWindowDict, curWidget)
#        if eid == 'comment' or eid == 'preview':
#            QMessageBox.warning(self, 'Warning', 'No restore, preview is selected.')
#            return
        data = self.data4eid[str(eid)]
        
        pvnames = data['PV Name']
        status = data['Status']
        severity = data['Severity']
        ts = data['Time stamp']
        ts_nano = data['Time stamp (nano)']
        dbrtype = data['DBR']
        s_value = data['S_value']
        i_value = data['I_value']
        d_value = data['D_value']
        isConnected = data['isConnected']
        is_array = data['isArray'] 
        array_value = data['arrayValue']
        
        head = '# pv name, status, severity, time stamp, epics dbr, is connected, is array, value'

        filename = QFileDialog.getSaveFileName(self, 'Save File', '.')
        if not filename:
            return
        try:
            fname = open(filename, 'w')
            fname.write(head+'\n')
            for i in range(len(pvnames)):
                line = pvnames[i]
                line += ','+str(status[i])
                line += ','+str(severity[i])
                line += ','+str(datetime.datetime.fromtimestamp(ts[i]+ts_nano[i]*1.0e-9))
                line += ','+str(dbrtype[i])
                line += ','+str(bool(isConnected[i]))
                line += ','+str(bool(is_array[i]))
                if is_array[i]:
                    line += ','+str(array_value[i])
                else:
                    if dbrtype[i] in self.epicsDouble:
                        line += ','+str(d_value[i])
                    elif dbrtype[i] in self.epicsLong:
                        line += ','+str(i_value[i])
                    elif dbrtype[i] in self.epicsString:
                        line += ','+str(s_value[i])
                    else:
                        line += ''
                fname.write(line+'\n')
            fname.close()
        except:
            QMessageBox.warning(self,
                                "Warning",
                                "Cannot write to the file. Please check the writing permission.")

def main(channelname = None):
    app = QApplication(sys.argv)
    app.setOrganizationName("NSLS II")
    app.setOrganizationDomain("BNL")
    app.setApplicationName("MASAR Viewer")
    if channelname:
        form = masarUI(channelname=channelname)
    else:
        form = masarUI()
    form.show()
    app.exec_()
    
    import atexit
    # clean Python local objects first, especially the cothread stuff.
    # Cothread adds a new function in catools._catools_atexit(), ca_flush_io(), since version 2.8
    # to flush all io and do a clean up. This function registered at Python exit, and will be called 
    # by Python exit handler.
    # This forces the clean up has be done before calling epicsExit(). 
    atexit._run_exitfuncs()

    # it is safe to clean epics objects now.
    epicsExit()
    
    # call os.exit() instead of sys.exit()
    # os._exit(0)
    # however, os._exit() does nothing when exiting.
    # It would be better to call sys.exit
    sys.exit()

if __name__ == '__main__':
    args = sys.argv[1:]
    while args:
        arg = args.pop(0)
        if arg in ("-h", "--help", "help"):
            usage()
        else:
            print ('Unknown option.')   

    main()
