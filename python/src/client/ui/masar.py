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

from PyQt4.QtGui import (QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QTableWidget, QInputDialog)
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
        self.__service = 'masar'
        if source == 'epics':
            self.mc = masarClient.client(channelname)
        
        self.__initSystemBomboBox()
        
        self.currentConfigFilter = str(self.configFilterLineEdit.text())
        self.eventConfigFilter = str(self.eventFilterLineEdit.text())
        self.UTC_OFFSET_TIMEDELTA = datetime.datetime.utcnow() - datetime.datetime.now()
        self.time_format = "%Y-%m-%d %H:%M:%S"

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
        
    def saveSnapshotAction(self):
        selectedConfigs = self.configTableWidget.selectionModel().selectedRows()
        if len(selectedConfigs) > 0:
            configIds=[]
            configNames = []
            descs = []
            configMessages = "Do you want to save snapshots for all the following configurations?\n"
            for idx in selectedConfigs: 
                configIds.append(str(self.configTableWidget.item(idx.row(), 4).text()))
                descs.append(str(self.configTableWidget.item(idx.row(), 1).text()))
                tmp = str(self.configTableWidget.item(idx.row(), 0).text())
                configNames.append(tmp)
                configMessages += " - "+tmp+"\n"
    
            reply = QMessageBox.question(self, 'Message',
                                         configMessages,                                          
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.saveSnapshotData(configNames, descs)
            else:
                return  
        else:
            QMessageBox.warning(self,
                "Warning",
                "You did not select any configuration yet.")
            return

    def restoreSnapshotAction(self):
        print ('Reserved for restoring snapshot action')
  
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
            eventIds.append(str(self.eventTableWidget.item(idx.row(), 3).text()))
            
        self.snapshotTabWidget.setStatusTip("Snapshot data")
        self.setSnapshotTabWindow(eventNames, eventTs, eventIds)
        
    def setConfigTable(self):
        data = self.retrieveConfigData()
        self.setTable(data, self.configTableWidget)

    def setSnapshotTabWindow(self, eventNames, eventTs, eventIds):
        tabWidget = None
        
        for i in range(self.snapshotTabWidget.count(), 0, -1):
            self.snapshotTabWidget.removeTab(i)
        
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
            label = QString.fromUtf8((eventNames[i]+': ' + eventTs[i]))
            self.snapshotTabWidget.addTab(tabWidget, label)
            self.snapshotTabWidget.setTabText(i+1, label)

    def setEventTable(self, data):
        self.setTable(data, self.eventTableWidget)
    
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
            nrows = len(data.values()[0])
            #    ('pv name label',  'dbr_type label', 'string value', 'int value', 'double value', 'status label', 'severity label', 'ioc time stamp label', 'ioc time stamp nano label'),
            # => (pv_name, status, severity, ioc_timestamp, saved value)
            ncols = len(data) - 4
            table.setRowCount(nrows)
            table.setColumnCount(ncols)
            table.setSortingEnabled(True)
            
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

            # DBR_TYPE definition
            #define DBF_STRING  0
            #define DBF_INT     1
            #define DBF_SHORT   1
            #define DBF_FLOAT   2
            #define DBF_ENUM    3
            #define DBF_CHAR    4
            #define DBF_LONG    5
            #define DBF_DOUBLE  6
            epicsLong   = [1, 4, 5]
            epicsString = [0, 3]
            epicsDouble = [2, 6]

            keys = ['PV Name', 'Status', 'Severity', 'Time stamp', 'Connection', 'Saved value']
            table.setHorizontalHeaderLabels(keys)
            
            for i in range(nrows):
                if pvnames[i]:
                    newitem = QTableWidgetItem(pvnames[i])
                    newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
                    table.setItem(i, 0, newitem)
                if status[i]:
                    newitem = QTableWidgetItem(status[i])
                    newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
                    table.setItem(i, 1, newitem)
                if severity[i]:
                    newitem = QTableWidgetItem(severity[i])
                    newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
                    table.setItem(i, 2, newitem)
                if ts[i]:
                    dt = str(datetime.datetime.fromtimestamp(ts[i]+ts_nano[i]*1.0e-9))
                    newitem = QTableWidgetItem(dt)
                    newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
                    table.setItem(i, 3, newitem)
                if isConnected[i]:
                    newitem = QTableWidgetItem(str(bool(isConnected[i])))
                    newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
                    table.setItem(i, 4, newitem)
                    
                if dbrtype[i] in epicsDouble:
                    newitem = QTableWidgetItem(str(d_value[i]))
                    table.setItem(i, 5, newitem)
                    newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
                elif dbrtype[i] in epicsLong:
                    newitem = QTableWidgetItem(str(i_value[i]))
                    table.setItem(i, 5, newitem)
                    newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
                elif dbrtype[i] in epicsString:
                    newitem = QTableWidgetItem(str(s_value[i]))
                    newitem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
                    table.setItem(i, 5, newitem)
                else:
                    print('invalid dbr type (code = %s)'%(dbrtype[i]))
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
        elif source == 'epics':
            if configids:
                for i in range(len(configids)):
                    cid = configids[i]
                    params = {'configid': cid}
                    if self.timeRangeCheckBox.isChecked():
                        params['start'] = str(start)
                        params['end'] = str(end)
                    eids, usertag, utctimes = self.mc.retrieveServiceEvents(params)
                    event_ids = event_ids[:] + (list(eids))[:]
                    event_desc = event_desc[:] + (list(usertag))[:]
                    for ut in utctimes:
                        c_names.append(confignames[i])
                        ts = str(datetime.datetime.fromtimestamp(time.mktime(time.strptime(ut, self.time_format))) - self.UTC_OFFSET_TIMEDELTA)
                        event_ts.append(ts)
        data = odict()
        data['Config'] = c_names
        data['Time stamp'] = event_ts
        data['Description'] = event_desc
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

    def saveSnapshotData(self, configNames, comments):
        if source == 'sqlite':
            pass
        elif source == 'epics':
            for i in range(len(configNames)):
                count = 0
                while (True):
                    text, ok = QInputDialog.getText(self, 'Event Description', 
                                                    'Enter description for %s: \n(Use default by click Cancel)'%configNames[i])
                    if ok:
                        reply = QMessageBox.question(self, 'Confirm',
                            "Use description? \n%s"%text, QMessageBox.Yes | 
                            QMessageBox.No, QMessageBox.No)
                
                        if reply == QMessageBox.Yes:
                            comment = str(text)
                            break
                    else:
                        reply = QMessageBox.question(self, 'Confirm',
                            "Use default description? \n%s"%comments[i], QMessageBox.Yes | 
                            QMessageBox.No, QMessageBox.No)
                
                        if reply == QMessageBox.Yes:
                            comment = comments[i]
                            break
                    if count == 3:
                        reply = QMessageBox.question(self, 'Confirm',
                            "Do you want to cancel this operation?", QMessageBox.Yes | 
                            QMessageBox.No, QMessageBox.No)
                        if reply == QMessageBox.Yes:
                            return
                        else:
                            count = 0
                    else:
                        count += 1
                params = {'configname': configNames[i],
                          'comment': comment,
                          'servicename': 'masar'}
                result = self.mc.saveSnapshot(params)
                if not result:
                    QMessageBox.warning(self,
                        "Warning",
                        "Failed to save snapshot for configuration %s"%(configNames[i]))

def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("NSLS II")
    app.setOrganizationDomain("BNL")
    app.setApplicationName("MASAR Viewer")
    form = masarUI(source=source)
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()