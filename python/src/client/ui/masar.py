#!/usr/bin/env python
'''
Created on Dec 1, 2011

@author: shengb
'''

from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals

import sys
import os
import time
import datetime

from PyQt4.QtGui import (QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QTableWidget)
from PyQt4.QtCore import (QDateTime, Qt, QString)

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

__version__ = "0.0.1"

def usage():
    print("""usage: masar.py [source]

Sources to get data (which can be given in any of the forms shown):
-e  --epics      epics [default]
-i  --irmis      irmis 
-l  --sqlite     sqlite
or
-h  --help       help

source defaults to epics

masar.py v {0}. Copyright (c) 2011 Brookhaven National Laboratory. All rights reserved.
""".format(__version__))
    sys.exit()

source = 'epics'
args = sys.argv[1:]
while args:
    arg = args.pop(0)
    if arg in ("-i", "--irmis", "irmis"):
        print ('use IRMIS as data source')
        source = 'irmis'
    elif arg in ("-l", "--sqlite", "sqlite"):
        print ('use SQLite as data source')
        source = 'sqlite'
        import pymasar
        import sqlite3
        __db = '/'.join((os.path.abspath(os.path.dirname(__file__)), '../../../pymasar/example', 'masar.db'))
        conn = sqlite3.connect(__db)
    elif arg in ("-e", "--epics", "epics"):
        print ('use EPICS V4 as data source')
    elif arg in ("-h", "--help", "help"):
        usage()
    else:
        print ('Unknown data source. use EPICS V4 as data source')
if source == 'epics':
    import masarClient

# have to put this as last import, otherwise, import error. 
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

    def __init__(self, parent=None, channelname='masarService', source='epics'):
        super(masarUI, self).__init__(parent)
        self.setupUi(self)
        self.__setDateTime()
        self.tabWindowDict = {'comment': self.commentTab}
        self.e2cDict = {} # event to config dictionary
        self.pv4cDict = {} # pv name list for each selected configuration
        self.data4eid = {}
        
        self.__service = 'masar'
        if source == 'epics':
            self.mc = masarClient.client(channelname)
        
        self.__initSystemBomboBox()
        
        self.currentConfigFilter = str(self.configFilterLineEdit.text())
        self.eventConfigFilter = str(self.eventFilterLineEdit.text())
        self.UTC_OFFSET_TIMEDELTA = datetime.datetime.utcnow() - datetime.datetime.now()
        self.time_format = "%Y-%m-%d %H:%M:%S"
        self.previewId = None
        self.previewConfName = None
        
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
        
#        cid = str(self.configTableWidget.item(selectedConfig[0].row(), 4).text())
        cname = str(self.configTableWidget.item(selectedConfig[0].row(), 0).text())
        eid, data = self.getMachinePreviewData(cname)
        self.pv4cDict[str(eid)] = data['PV Name']
        self.data4eid[str(eid)] = data
        
        try:
            tabWidget = self.tabWindowDict['preview']
            index = self.snapshotTabWidget.indexOf(tabWidget)
        except:
            tabWidget = QTableWidget()
            index = self.snapshotTabWidget.count()
            self.tabWindowDict['preview'] = tabWidget
        
#        tabWidget = self.tabWindowDict['preview']
#        tabWidget.clear()
#        
#        index = self.snapshotTabWidget.indexOf(tabWidget)
#        # create a new widget.
#        # problem to reuse widget: sorting
#        tabWidget = QTableWidget()
#        self.tabWindowDict['preview'] = tabWidget
        
        self.setSnapshotTable(data, tabWidget)
        tabWidget.resizeColumnsToContents()
        label = QString.fromUtf8((cname+': Preview'))
        self.snapshotTabWidget.addTab(tabWidget, label)

        self.snapshotTabWidget.setTabText(index, label)        
        self.snapshotTabWidget.setCurrentIndex(index)
        
        self.previewId = eid
        self.previewConfName = cname
        self.isPreviewSaved = False
        
#        self.__doSaveSnapshot(selectedConfigs)
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
        pvlist = list(self.pv4cDict[str(eid)])
        data = self.data4eid[str(eid)]
        s_val = data['S_value']
        d_val = data['D_value']
        i_val = data['I_value']
        dbrtype = data['DBR']
        
        r_data = []
        for index in range(len(pvlist)):
            if dbrtype[index] in self.epicsDouble:
                r_data.append(d_val[index])
            elif dbrtype[index] in self.epicsLong:
                r_data.append(i_val[index])
            elif dbrtype[index] in self.epicsString:
                r_data.append(s_val[index])
            elif dbrtype[index] in self.epicsNoAccess:
                QMessageBox.warning(self, 'Warning', 'Cannot restore machine.Value unknown for pv: %s'%(pvlist[index]))
                return
        
        bad_pvs = []
        try:
            results = cav3.caput(list(pvlist), r_data)
            for res in results:
                if not res.ok:
                    bad_pvs.append(res.name)
        except:
            QMessageBox.warning(self, 'Warning', 'Error during restoring snapshot to live machine.')
        
        if len(bad_pvs) > 0:
            message = "Restore failed for the following pvs:\n"
            for bad_pv in bad_pvs:
                message += " -- "+bad_pv + "\n"
            QMessageBox.warning(self, 'Warning', message)
        
#        data['PV Name'] = pvnames
#        data['Status'] = status
#        data['Severity'] = severity
#        data['Time stamp'] = ts
#        data['Time stamp (nano)'] = ts_nano
#        data['DBR'] = dbrtype
#        data['S_value'] = s_value
#        data['I_value'] = i_value
#        data['D_value'] = d_value
#        data['isConnected'] = isConnected

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
            channelName, s_value, d_value, i_value, dbrtype, isConnected = self.getLiveMachineData(pvlist)
            
            dd = {}
            noMatchedPv = []
            
            # put channel name and its order into a dictionary
            for i in range(len(channelName)):
                dd[channelName[i]] = i
            
            # get table rows
            rowCount = curWidget.rowCount()
            for i in range(rowCount):
                try:
                    index = dd[str(curWidget.item(i, 0).text())]
                except:
                    print (channelName[index])
                    noMatchedPv.append(channelName[index])
                
                if dbrtype[index] in self.epicsDouble:
                    newitem = QTableWidgetItem(str(d_value[index]))
                    curWidget.setItem(i, 6, newitem)
                    newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
                    
                    saved_val = float(str(curWidget.item(i, 5).text()))
                    if d_value[index] != None:
                        delta = d_value[index] - saved_val
                        if abs(delta) < 1.0e-6:
                            delta = 0
                    else:
                        delta = None  
                    
                    newitem = QTableWidgetItem(str(delta))
                    curWidget.setItem(i, 7, newitem)
                    newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)                    
                elif dbrtype[index] in self.epicsLong:
                    newitem = QTableWidgetItem(str(i_value[index]))
                    curWidget.setItem(i, 6, newitem)
                    newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
                    
                    if dbrtype[index] in self.epicsNoAccess:
                        pass
#                        if isConnected[index]:
#                            pass
#                        else:
#                            pass
                    else:
                        saved_val = int(float(str(curWidget.item(i, 5).text())))
                        if i_value[index] != None:
                            delta = i_value[index] - saved_val
                        else:
                            delta = None
                        
                        newitem = QTableWidgetItem(str(delta))
                        curWidget.setItem(i, 7, newitem)
                        newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)

                elif dbrtype[index] in self.epicsString:
                    newitem = QTableWidgetItem(str(s_value[index]))
                    curWidget.setItem(i, 6, newitem)
                    newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
            if len(noMatchedPv) > 0:
                print ("Can not find the following pv for this snapshot: \n", noMatchedPv)
            # list some pv 
        else:
            QMessageBox.warning(self, "Warning", "Not a snapshot.")
            return
        
    def updateChanValue(self, pvlist, curWidget):
        pass
    
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
            eventTs.append(str(self.eventTableWidget.item(idx.row(), 1).text()))
            eventIds.append(str(self.eventTableWidget.item(idx.row(), 4).text()))
            
        self.snapshotTabWidget.setStatusTip("Snapshot data")
        self.setSnapshotTabWindow(eventNames, eventTs, eventIds)
        
    def setConfigTable(self):
        data = self.retrieveConfigData()
        self.setTable(data, self.configTableWidget)

#    def snapshotTabSelector(self):
#        curWidget = self.snapshotTabWidget.currentWidget()
#        eid = self.__find_key(self.tabWindowDict, curWidget)
#        if eid != 'comment':
##            print (eid)        
#            pvs = self.pv4cDict[str(eid)]
##            print (len(pvs), pvs)
    
    def setSnapshotTabWindow(self, eventNames, eventTs, eventIds):
        tabWidget = None
        
        for i in range(self.snapshotTabWidget.count(), 0, -1):
            self.snapshotTabWidget.removeTab(i)

        self.pv4cDict.clear()
        self.data4eid.clear()
        
        for i in range(len(eventIds)):
            if self.tabWindowDict.has_key(eventIds[i]):
                tabWidget = self.tabWindowDict[eventIds[i]]
            else:
                tabWidget = QTableWidget()
                self.tabWindowDict[eventIds[i]] = tabWidget
            
            data = self.retrieveMasarData(eventid=eventIds[i])
            tabWidget.clear()
            self.setSnapshotTable(data, tabWidget)
            tabWidget.resizeColumnsToContents()
            ts = eventTs[i].split('.')[0]
            
            label = QString.fromUtf8((eventNames[i]+': ' + ts))
            self.snapshotTabWidget.addTab(tabWidget, label)
            self.snapshotTabWidget.setTabText(i+1, label)
            self.pv4cDict[str(eventIds[i])] = data['PV Name']
            self.data4eid[str(eventIds[i])] = data
                
        self.snapshotTabWidget.setCurrentIndex(1)
        
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
                
    def setSnapshotTable(self, data, table):
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
            #     'ioc time stamp label', 'ioc time stamp nano label'),
            # => (pv_name, status, severity, ioc_timestamp, saved value)
            # ncols = len(data) - 4
            # ncols = ncols + 2  # 2 columns for live data and (live data - saved data)
            ncols = len(data) - 2
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
            
            keys = ['PV Name', 'Status', 'Severity', 'Time stamp', 'Connection', 'Saved value', 'Live value', 'Delta']
            table.setHorizontalHeaderLabels(keys)
            
            for i in range(nrows):
                if pvnames[i]:
                    self.__setTableItem(table, i, 0, pvnames[i])
#                    item = table.item(i, 0)
#                    if item:
#                        item.setText(pvnames[i])
#                    else:
#                        newitem = QTableWidgetItem(pvnames[i])
#                        newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
#                        table.setItem(i, 0, newitem)
                if status[i]:
                    self.__setTableItem(table, i, 1, str(status[i]))
#                    item = table.item(i, 1)
#                    if item:
#                        item.setText(str(status[i]))
#                    else:
#                        newitem = QTableWidgetItem(str(status[i]))
#                        newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
#                        table.setItem(i, 1, newitem)
                if severity[i]:
                    self.__setTableItem(table, i, 2, str(severity[i]))
#                    item = table.item(i, 2)
#                    if item:
#                        item.setText(severity[i])
#                    else:
#                        newitem = QTableWidgetItem(str(severity[i]))
#                        newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
#                        table.setItem(i, 2, newitem)
                if ts[i]:
                    dt = str(datetime.datetime.fromtimestamp(ts[i]+ts_nano[i]*1.0e-9))
                    self.__setTableItem(table, i, 3, dt)
#                    item = table.item(i, 3)
#                    if item:
#                        item.setText(dt)
#                    else:
#                        newitem = QTableWidgetItem(dt)
#                        newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
#                        table.setItem(i, 3, newitem)
                if isConnected[i]:
                    self.__setTableItem(table, i, 4, str(bool(isConnected[i])))
#                    item = table.item(i, 4)
#                    if item:
#                        item.setText(str(bool(isConnected[i])))
#                    else:
#                        newitem = QTableWidgetItem(str(bool(isConnected[i])))
#                        newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
#                        table.setItem(i, 4, newitem)

                if dbrtype[i] in self.epicsDouble:
                    self.__setTableItem(table, i, 5, str(d_value[i]))
#                    item = table.item(i, 5)
#                    if item:
#                        item.setText(str(d_value[i]))
#                    else:
#                        newitem = QTableWidgetItem(str(d_value[i]))
#                        table.setItem(i, 5, newitem)
#                        newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
                elif dbrtype[i] in self.epicsLong:
                    self.__setTableItem(table, i, 5, str(i_value[i]))
#                    item = table.item(i, 5)
#                    if item:
#                        item.setText(str(i_value[i]))
#                    else:
#                        newitem = QTableWidgetItem(str(i_value[i]))
#                        table.setItem(i, 5, newitem)
#                        newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
                elif dbrtype[i] in self.epicsString:
                    self.__setTableItem(table, i, 5, str(s_value[i]))
#                    item = table.item(i, 5)
#                    if item:
#                        item.setText(str(s_value[i]))
#                    else:
#                        newitem = QTableWidgetItem(str(s_value[i]))
#                        newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
#                        table.setItem(i, 5, newitem)
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
        if source == 'sqlite':
            results = pymasar.service.retrieveServiceConfigProps(conn)
            system = []
            for result in results[1:]:
                system.append(result[3])
            return sorted(set(system))
        elif source == 'epics':
            try:
                return self.mc.retrieveSystemList()
            except:
                QMessageBox.warning(self,
                                    "Warning",
                                    "Cannot connect to MASAR server.\nPlease check the serviceName, network connection, and service status.")

                return
    
    def retrieveConfigData(self):
        data = odict()
        if source == 'sqlite':
            results = pymasar.service.retrieveServiceConfigs(conn, servicename=self.__service, system=self.system)[1:]
            # the rturned data format looks like
            # [(service_config_id, service_config_name, service_config_desc, service_config_create_date, 
            #   service_config_version, and service_name)]

            #  + self.UTC_OFFSET_TIMEDELTA
            config_id = []
            config_name = []
            config_desc = []
            config_date = []
            config_version = []
            if results:
                for res in results:
                    config_id.append(str(res[0]))
                    config_name.append(res[1])
                    config_desc.append(res[2])
                    config_date.append(res[3])
                    config_version.append(res[4])
        elif source == 'epics':
            params = {"system": self.system,
                      "servicename": self.__service}
            config_id, config_name, config_desc, config_date, config_version = self.mc.retrieveServiceConfigs(params)
        data['Name'] = config_name
        data['Description'] = config_desc
        data['Date'] = config_date
        data['Version'] = config_version
        data['Id'] = config_id
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
        event_initializer = []
        self.e2cDict.clear()
        if source == 'sqlite':
            if configids:
                for i in range(len(configids)):
                    cid = configids[i]
                    if self.timeRangeCheckBox.isChecked():
                        results = pymasar.service.retrieveServiceEvents(conn, configid= cid, start=start, end=end)
                    else:
                        results = pymasar.service.retrieveServiceEvents(conn, configid= cid)
                    #service_event_id, service_config_id, service_event_user_tag, service_event_UTC_time, service_event_serial_tag
                    for res in results[1:]:
                        c_names.append(confignames[i])
                        event_ids.append(str(res[0]))
                        ts = str(datetime.datetime.fromtimestamp(time.mktime(time.strptime(res[3], self.time_format))) - self.UTC_OFFSET_TIMEDELTA)
                        event_ts.append(ts)
                        event_desc.append(res[2])
                        event_initializer.append(str(res[4]))
                        self.e2cDict[str(res[0])] = [cid, res[2], confignames[i]]
        elif source == 'epics':
            if configids:
                for i in range(len(configids)):
                    cid = configids[i]
                    params = {'configid': cid}
                    if self.timeRangeCheckBox.isChecked():
                        params['start'] = str(start)
                        params['end'] = str(end)
                    eids, usertag, utctimes, initializer = self.mc.retrieveServiceEvents(params)

                    event_ids = event_ids[:] + (list(eids))[:]
                    event_desc = event_desc[:] + (list(usertag))[:]
                    event_initializer = event_initializer[:] + (list(initializer))[:]
                    for j in range(len(eids)):
                        self.e2cDict[str(eids[j])] = [cid, usertag[j],confignames[i]]
                    for ut in utctimes:
                        c_names.append(confignames[i])
                        ts = str(datetime.datetime.fromtimestamp(time.mktime(time.strptime(ut, self.time_format))) - self.UTC_OFFSET_TIMEDELTA)
                        event_ts.append(ts)
                    
        data = odict()
        data['Config'] = c_names
        data['Time stamp'] = event_ts
        data['Description'] = event_desc
        data['Initializer'] = event_initializer
        data['Id'] = event_ids
        return data

    def retrieveMasarData(self, eventid=None):
        data = odict()
        if source == 'sqlite':
            # result format:
            # ('user tag', 'event UTC time', 'service config name', 'service name'),
            # ('pv name', 'string value', 'double value', 'long value', 'dbr type', 'isConnected', 
            #  'secondsPastEpoch', 'nanoSeconds', 'timeStampTag', 'alarmSeverity', 'alarmStatus', 'alarmMessage')
            results = pymasar.masardata.masardata.retrieveSnapshot(conn, eventid=eventid)[1]
            pvnames = []
            s_value = []
            d_value = []
            i_value = []
            dbrtype = []
            isConnected = []
            ts = []
            ts_nano = []
            ts_tag = []
            severity = []
            status = []
            alarm_message = []

            if len(results) > 2:
                for i in range(2, len(results)):
                    res = results[i]

                    pvnames.append(res[0])
                    s_value.append(res[1])
                    d_value.append(res[2])
                    i_value.append(res[3])
                    dbrtype.append(res[4])
                    isConnected.append(res[5])
                    ts.append(res[6])
                    ts_nano.append(res[7])
                    ts_tag.append(res[8])
                    severity.append(res[9])
                    status.append(res[10])
                    alarm_message.append(res[11])
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
        elif source == 'epics':
            params = {'eventid': eventid}
            pvnames, s_value, d_value, i_value, dbrtype, isConnected, ts, ts_nano, severity, status = self.mc.retrieveSnapshot(params)
            severity = list(severity)
            status = list(status)

        for i in range(len(severity)):
            try:
                severity[i] = self.severityDict[severity[i]]
            except:
                severity[i] = 'N/A'
            try:
                status[i] = self.alarmDict[status[i]]
            except:
                status[i] = 'N/A'

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
        
        return data

    def saveMachinePreviewData(self, eventid, confname, comment):
        if source == 'sqlite':
            pass
        elif source == 'epics':
            if not eventid:
                QMessageBox.warning(self,
                            "Warning",
                            "Unknown event.")
                return

            params = {'eventid':    str(eventid),
                      'configname': str(confname),
                      'user':       str(comment[0]),
                      'desc':       str(comment[1])}
            result = self.mc.updateSnapshotEvent(params)
            if result:
                QMessageBox.information(self,"Successful", 
                                        " Succeed to save preview")
            else:
                QMessageBox.information(self, "Failures",
                                        "Failed to save preview.")
    
    def getMachinePreviewData(self, configName):
        if source == 'sqlite':
            pass
        elif source == 'epics':
            params = {'configname': configName,
                      'servicename': 'masar'}
            
            eventid, pvnames, s_value, d_value, i_value, dbrtype, isConnected, ts, ts_nano, severity, status = self.mc.saveSnapshot(params)
            severity = list(severity)
            status = list(status)
    
            for i in range(len(severity)):
                try:
                    severity[i] = self.severityDict[severity[i]]
                except:
                    severity[i] = 'N/A'
                try:
                    status[i] = self.alarmDict[status[i]]
                except:
                    status[i] = 'N/A'
    
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
    
            return (eventid, data)
        
    def getLiveMachineData(self, pvlist):
        if source == 'sqlite':
            pass
        elif source == 'epics':
            params = {}
            for pv in pvlist:
                params[pv] = pv
            # channelName,stringValue,doubleValue,longValue,dbrType,isConnected
            return self.mc.getLiveMachine(params)

def main(channelname = None):
    app = QApplication(sys.argv)
    app.setOrganizationName("NSLS II")
    app.setOrganizationDomain("BNL")
    app.setApplicationName("MASAR Viewer")
    if channelname:
        form = masarUI(channelname=channelname, source=source)
    else:
        form = masarUI(source=source)
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
