"""This is a utils to manage MASAR database configurations.
It could be used to add a new configuration, and update status of each configuration.
"""
from __future__ import division
from __future__ import print_function

__author__ = 'shengb'

import os
import sys
from operator import itemgetter
import numpy as np
import ConfigParser

from PyQt4 import QtGui
from PyQt4.QtGui import (QApplication, QMainWindow, QMessageBox,
                         QTableWidgetItem, QFileDialog, QSizePolicy,
                         QAbstractItemView, QStandardItemModel, QStandardItem, QItemSelectionModel)

from PyQt4 import QtCore
from PyQt4.QtCore import (Qt, QString)

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

try:
    assert sys.version_info[:2] >= (2, 7)
    # from collections import OrderedDict as odict
except AssertionError:
    print ('Python version 2.7 or higher is needed.')
    sys.exit()

import ui_dbmanager

__version__ = "1.0.0"


def usage():
    print("""usage: pythjon masarconfigmanager.py

command option:
-h  --help       help

masarconfigmanager.py v {0}. Copyright (c) 2014 Brookhaven National Laboratory. All rights reserved.
""".format(__version__))
    sys.exit()


class ShowPvMessageBox(QtGui.QMessageBox):
    def __init__(self):
        QtGui.QMessageBox.__init__(self)
        self.setSizeGripEnabled(True)

    def event(self, e):
        result = QtGui.QMessageBox.event(self, e)

        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.setMinimumWidth(0)
        self.setMaximumWidth(16777215)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        textEdit = self.findChild(QtGui.QTextEdit)
        if textEdit != None :
            textEdit.setMinimumHeight(0)
            textEdit.setMaximumHeight(16777215)
            textEdit.setMinimumWidth(0)
            textEdit.setMaximumWidth(16777215)
            textEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return result


class dbmanagerUI(QMainWindow, ui_dbmanager.Ui_dbmanagerUI):
    """Main UI for MASAR database manager."""
    def __init__(self):
        """"""
        super(dbmanagerUI, self).__init__()
        self.setupUi(self)
        self.statusbar.showMessage("Ready")

        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit Masar Configuration Manager.')
        exitAction.triggered.connect(QtGui.qApp.quit)

        self.groupdatabasemenubar()

        #default database source, could be 0: SQLite, 1: MongoDB, and 2: MySQL
        self.dbsource = None

        self.defaultdbinfo = self._loadmasarconfig()
        self.usedefaultdb = True

        self.comboxboxSignalMapper = QtCore.QSignalMapper(self)
        self.comboxboxSignalMapper.mapped[QtGui.QWidget].connect(self.comboboxSignalMapperMapped)

        self.pushbuttonSignalMapper = QtCore.QSignalMapper(self)
        self.pushbuttonSignalMapper.mapped[QtGui.QWidget].connect(self.pushbuttonSignalMapperMapped)

        self.showpvbuttonSignalMapper = QtCore.QSignalMapper(self)
        self.showpvbuttonSignalMapper.mapped[QtGui.QWidget].connect(self.showpvbuttonSignalMapperMapped)

        self.choosepvbuttonSignalMapper = QtCore.QSignalMapper(self)
        self.choosepvbuttonSignalMapper.mapped[QtGui.QWidget].connect(self.choosepvbuttonSignalMapperMapped)

        self.currentselectedrow4config = -1

        self.selectedsystem = "Others"

        # self.pvgrouptreeview = QTreeView()
        self.pvGroupTreeView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.pvgroupmodel = QStandardItemModel()
        # self.pvgroupmodel.setHorizontalHeaderLabels(['id', 'date', 'version', "description"])
        self.pvgroupmodel.setHorizontalHeaderLabels(["PV Groups"])
        self.pvGroupTreeView.setModel(self.pvgroupmodel)
        self.pvGroupTreeView.setUniformRowHeights(True)

    @QtCore.pyqtSlot(QtGui.QWidget)
    def comboboxSignalMapperMapped(self, comboBox):
        if self.masarConfigTableWidget.cellWidget(comboBox.row, comboBox.column + 1).isEnabled():
            self.masarConfigTableWidget.cellWidget(comboBox.row, comboBox.column + 1).setEnabled(False)
            button = self.masarConfigTableWidget.cellWidget(comboBox.row, comboBox.column + 1)
            palette = QtGui.QPalette(button.palette())  # make a copy of the palette
            palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor('grey'))
            button.setPalette(palette)
        else:
            self.masarConfigTableWidget.cellWidget(comboBox.row, comboBox.column + 1).setEnabled(True)
            button = self.masarConfigTableWidget.cellWidget(comboBox.row, comboBox.column + 1)
            palette = QtGui.QPalette(button.palette())  # make a copy of the palette
            palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor('red'))
            button.setPalette(palette)

    @QtCore.pyqtSlot(QtGui.QWidget)
    def pushbuttonSignalMapperMapped(self, pushbutton):
        configstatus = str(self.masarConfigTableWidget.cellWidget(pushbutton.row, pushbutton.column-1).currentText())
        cid = str(self.masarConfigTableWidget.item(pushbutton.row, 0).text())
        cname = str(self.masarConfigTableWidget.item(pushbutton.row, 1).text())

        if self.updatemasarconfigstatus(configstatus, cid, configname=cname):
            palette = QtGui.QPalette(pushbutton.palette())  # make a copy of the palette
            palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor('grey'))
            pushbutton.setPalette(palette)
            pushbutton.setEnabled(False)

    @QtCore.pyqtSlot(QtGui.QWidget)
    def showpvbuttonSignalMapperMapped(self, showpvbutton):
        if self.newConfigTableWidget.item(showpvbutton.row, showpvbutton.column + 2) is None:
            raise RuntimeError("Unknown pv file")
        pvfilename = self.newConfigTableWidget.item(showpvbutton.row, showpvbutton.column + 2).text()
        if not os.path.isfile(pvfilename):
            raise RuntimeError("Invalid pv file name for (row, col): (%s, %s)" % (showpvbutton.row,
                                                                                  showpvbutton.column + 2))

        text = ", ".join(np.loadtxt(str(pvfilename), dtype=str, comments="#"))
        if self.newConfigTableWidget.item(showpvbutton.row, 0) is not None:
            head = self.newConfigTableWidget.item(showpvbutton.row, 0).text()
        else:
            head = ""
        msg = QMessageBox(self,
                          windowTitle='PVs for group %s' % head,
                          text="The following PVs to be added:")
        msg.setDetailedText(text)
        msg.exec_()

    @QtCore.pyqtSlot(QtGui.QWidget)
    def choosepvbuttonSignalMapperMapped(self, chhosepvbutton):
        self.newConfigTableWidget.setItem(chhosepvbutton.row,
                                          chhosepvbutton.column+1,
                                          QTableWidgetItem(QFileDialog.getOpenFileName(self, "Open File")))

    def _loadmasarconfig(self):
        cf = ConfigParser.SafeConfigParser()
        cf.read([
            os.path.expanduser('~/.masarservice.conf'),
            '/etc/masarservice.conf',
            'masarservice.conf',
            "%s/masarservice.conf" % os.path.abspath(os.path.dirname(__file__))
        ])
        return cf

    def groupdatabasemenubar(self):
        """Group 3 Databases menu together to make selection exclusive."""
        group = QtGui.QActionGroup(self)
        self.actionSQLite.setActionGroup(group)
        self.actionMongoDB.setActionGroup(group)
        self.actionMySQL.setActionGroup(group)

    def actionsqlitemenu(self):
        """Answer action when SQLite is selected."""
        if self.actionSQLite.isChecked():
            self.dbsource = 0
            self.defaultsqlitedb()
            self.listPvGroupPushButton.setEnabled(True)

    def actionmongodbmenu(self):
        """Answer action when MongoDB is selected."""
        if self.actionMongoDB.isChecked():
            self.dbsource = 1
            self.defaultmongodb()
            self.listPvGroupPushButton.setEnabled(False)

    def actionmysqlmenu(self):
        """Answer action when MySQL is selected."""
        if self.actionMySQL.isChecked():
            QMessageBox.warning(self, 'Warning', "MySQL support not implemented yet.")
            self.actionMySQL.setChecked(False)
            if self.dbsource == 0:
                self.actionSQLite.setChecked(True)
            elif self.dbsource == 1:
                self.actionMongoDB.setChecked(True)

    def showdefaultdbinfo(self):
        """"""
        if self.dbsource == 0:
            self.defaultsqlitedb()
        elif self.dbsource == 1:
            self.defaultmongodb()
        elif self.dbsource == 2:
            QMessageBox.warning(self, 'Warning', "MySQL support not implemented yet.")

    def defaultsqlitedb(self):
        """"""
        if self.defaultdbinfo.has_section("sqlite"):
            self.databaseDefault.setText(self.defaultdbinfo.get("sqlite", "database"))
            self.hostDefault.clear()
            self.portDefault.clear()
            self.userDefault.clear()

    def defaultmongodb(self):
        """"""
        if self.defaultdbinfo.has_section("mongodb"):
            self.databaseDefault.setText(self.defaultdbinfo.get("mongodb", "database"))
            self.hostDefault.setText(self.defaultdbinfo.get("mongodb", "host"))
            self.portDefault.setText(self.defaultdbinfo.get("mongodb", "port"))
            self.userDefault.setText(self.defaultdbinfo.get("mongodb", "username"))

    def getdatabasename(self):
        """"""
        self.database = self.databaseLineEdit.text()

    def getdatabaseport(self):
        """"""
        self.databaseport = self.databaseportLineEdit.text()

    def getdatabasehost(self):
        """"""
        self.databasehost = self.databaseHostLineEdit.text()

    def getdatabasepw(self):
        """"""
        self.databasepw = self.databasePwLineEdit.text()

    def showmasarconfigs(self):
        """"""
        result = None
        if self.dbsource == 0:
            # get data from sqlite
            if self.usedefaultdb:
                # masardb = str(self.databaseDefault.text())
                masardb = str(self.databaseDefault.toPlainText())
            else:
                masardb = str(self.databaseLineEdit.text())

            if masardb != "":
                os.environ["MASAR_SQLITE_DB"] = masardb
            else:
                raise RuntimeError("Cannot find MASAR SQLite Database")

            import pymasarsqlite
            conn = pymasarsqlite.utils.connect()
            result = pymasarsqlite.service.retrieveServiceConfigs(conn, servicename="masar")
            pymasarsqlite.utils.close(conn)

        elif self.dbsource == 1:
            # get data from mongodb
            if self.usedefaultdb:
                database = str(self.databaseDefault.toPlainText())
                host = str(self.hostDefault.toPlainText())
                port = str(self.portDefault.toPlainText())
            else:
                database = str(self.databaseLineEdit.text())
                host = str(self.databaseHostLineEdit.text())
                port = str(self.databasePortLineEdit.text())

            import pymasarmongo
            mongoconn, collection = pymasarmongo.db.utils.conn(host=host, port=port, db=database)
            resultdict = pymasarmongo.pymasarmongo.pymasar.retrieveconfig(mongoconn, collection)
            pymasarmongo.db.utils.close(mongoconn)

            result = [['id', 'name', 'desc', 'date', 'version', 'status']]
            for res in resultdict:
                result.append([res['configidx'],
                               res['name'],
                               res['desc'],
                               res['created_on'],
                               res['version'],
                               res['status']])
                               # res['system']

        if result is not None:
            self._setconfigtable(result)

    def choosedbsrc(self, bool):
        """Choose DB source"""
        if bool:
            self.usedefaultdb = True
        else:
            self.usedefaultdb = False

    def _setconfigtable(self, content):
        """"""
        # head = self.masarConfigTableWidget.horizontalHeader()
        self.masarConfigTableWidget.clearContents()
        # self.masarConfigTableWidget.setHorizontalHeaderLabels(head)

        if len(content) > 1:
            self.masarConfigTableWidget.setRowCount(len(content)-1)

            n = 0
            data = sorted(content[1:], key=itemgetter(0), reverse=True)
            for res in data:
                m = 0
                for item in res:
                    if not isinstance(item, basestring):
                        item = str(item)
                    if item:
                        if m == 5:
                            newitem = QtGui.QComboBox()
                            newitem.addItem("active")
                            newitem.addItem("inactive")
                            if item == "active":
                                newitem.setCurrentIndex(0)
                            else:
                                newitem.setCurrentIndex(1)

                            newitem.row = n
                            newitem.column = m
                            self.masarConfigTableWidget.setCellWidget(n, m, newitem)
                            self.comboxboxSignalMapper.setMapping(newitem, newitem)
                            newitem.currentIndexChanged.connect(self.comboxboxSignalMapper.map)

                            updatebutton = QtGui.QPushButton()
                            updatebutton.setText("Update")
                            updatebutton.setEnabled(False)
                            updatebutton.row = n
                            updatebutton.column = m+1
                            self.pushbuttonSignalMapper.setMapping(updatebutton, updatebutton)
                            self.masarConfigTableWidget.setCellWidget(n, m+1, updatebutton)
                            updatebutton.clicked.connect(self.pushbuttonSignalMapper.map)
                        else:
                            newitem = QTableWidgetItem(item)
                            newitem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                            self.masarConfigTableWidget.setItem(n, m, newitem)
                    m += 1
                n += 1

            self.masarConfigTableWidget.resizeColumnsToContents()

    def updatemasarconfigstatus(self, configstatus, cid, configname=None):
        if self.dbsource == 0:
            # get data from sqlite
            if self.usedefaultdb:
                masardb = str(self.databaseDefault.toPlainText())
            else:
                masardb = str(self.databaseLineEdit.text())

            if masardb != "":
                os.environ["MASAR_SQLITE_DB"] = masardb
            else:
                raise RuntimeError("Cannot find MASAR SQLite Database")

            import pymasarsqlite

            conn = pymasarsqlite.utils.connect()
            pymasarsqlite.service.updateServiceConfigStatus(conn, cid, status=configstatus)
            pymasarsqlite.utils.save(conn)
            pymasarsqlite.utils.close(conn)

        elif self.dbsource == 1:
            # get data from mongodb
            if self.usedefaultdb:
                database = str(self.databaseDefault.toPlainText())
                host = str(self.hostDefault.toPlainText())
                port = str(self.portDefault.toPlainText())
            else:
                database = str(self.databaseLineEdit.text())
                host = str(self.databaseHostLineEdit.text())
                port = str(self.databasePortLineEdit.text())

            import pymasarmongo

            mongoconn, collection = pymasarmongo.db.utils.conn(host=host, port=port, db=database)
            pymasarmongo.pymasarmongo.pymasar.updateconfig(mongoconn, collection, configname,
                                                           configidx=int(cid), status=configstatus)
            pymasarmongo.db.utils.close(mongoconn)

        return True

    def addnewpvgrouprow(self):
        """Add a new row to add pv group to MASAR configuration"""
        print ("""Add a new row to add pv group to MASAR configuration""")
        currowcount = self.newConfigTableWidget.rowCount()
        self.newConfigTableWidget.setRowCount(currowcount + 1)

        showpvbutton = QtGui.QPushButton()
        showpvbutton.setText("Show PVs")
        showpvbutton.setEnabled(True)
        showpvbutton.row = currowcount
        showpvbutton.column = 2
        self.showpvbuttonSignalMapper.setMapping(showpvbutton, showpvbutton)
        self.newConfigTableWidget.setCellWidget(currowcount, showpvbutton.column, showpvbutton)
        showpvbutton.clicked.connect(self.showpvbuttonSignalMapper.map)

        choosepvbutton = QtGui.QPushButton()
        choosepvbutton.setText("PV File")
        choosepvbutton.setEnabled(True)
        choosepvbutton.row = currowcount
        choosepvbutton.column = 3
        self.choosepvbuttonSignalMapper.setMapping(choosepvbutton, choosepvbutton)
        self.newConfigTableWidget.setCellWidget(currowcount, choosepvbutton.column, choosepvbutton)
        choosepvbutton.clicked.connect(self.choosepvbuttonSignalMapper.map)

    def removepvgrouprow(self):
        """Remove selected pv group from the configuration to be added into MASAR database"""
        if self.currentselectedrow4config == -1:
            raise RuntimeError("No pv group selected.")
        rownametobedelete = self.newConfigTableWidget.item(self.currentselectedrow4config, 0)
        if rownametobedelete is not None:
            rownametobedelete = rownametobedelete.text()
        self.newConfigTableWidget.removeRow(self.currentselectedrow4config)
        if rownametobedelete is not None:
            print ("Successfully delete pv group: ", rownametobedelete)
        else:
            print ("Successfully delete row: ", self.currentselectedrow4config)
        self.currentselectedrow4config = -1

    def savemasarsqlite(self):
        """"""
        # get data from sqlite
        if self.usedefaultdb:
            masardb = str(self.databaseDefault.toPlainText())
        else:
            masardb = str(self.databaseLineEdit.text())

        if masardb != "":
            os.environ["MASAR_SQLITE_DB"] = masardb
        else:
            QMessageBox.warning(self, "Warning",
                                "Cannot find MASAR SQLite Database")

        import pymasarsqlite

        conn = pymasarsqlite.utils.connect()
        existedresult = pymasarsqlite.service.retrieveServiceConfigs(conn, servicename="masar")
        newcfgdata = self._getnewconfigurationdata(existedresult)

        if newcfgdata is None:
            # Nothing to be added.
            raise ValueError("Empty configuration.")

        newcfgname = newcfgdata[0]
        desc = newcfgdata[1]
        msystem = newcfgdata[2]
        # config data format: [[name], [desc], [pv files]]
        cfgdata = newcfgdata[3]

        for i in range(len(cfgdata[0])):
            if cfgdata[0][i] is None:
                QMessageBox.warning(self, "Warning", "Wrong PV group name")
                return

            if cfgdata[2][i] is not None and os.path.isfile(cfgdata[2][i]):
                pvs = list(np.loadtxt(cfgdata[2][i], dtype=str, comments="#"))
                if len(pvs) > 0:
                    for i, pv in enumerate(pvs):
                        pvs[i] = pv.strip()
                    pymasarsqlite.pvgroup.savePvGroup(conn, cfgdata[0][i], func=cfgdata[1][i])
                    pymasarsqlite.pvgroup.saveGroupPvs(conn, cfgdata[0][i], pvs)

        try:
            pymasarsqlite.service.saveServiceConfig(conn, "masar", newcfgname, configdesc=desc, system=msystem)
            pymasarsqlite.service.saveServicePvGroup(conn, newcfgname, cfgdata[0])
        except Exception as e:
            QMessageBox.warning(self, "Error", e.message)
            return

        pymasarsqlite.utils.save(conn)
        QMessageBox.information(self, "Congratulation", "A new configuration has been added successfully.")
        pymasarsqlite.utils.close(conn)

    def savemasarmongodb(self):
        """"""
        # get data from mongodb
        if self.usedefaultdb:
            database = str(self.databaseDefault.toPlainText())
            host = str(self.hostDefault.toPlainText())
            port = str(self.portDefault.toPlainText())
        else:
            database = str(self.databaseLineEdit.text())
            host = str(self.databaseHostLineEdit.text())
            port = str(self.databasePortLineEdit.text())

        import pymasarmongo

        mongoconn, collection = pymasarmongo.db.utils.conn(host=host, port=port, db=database)
        existedresult = pymasarmongo.pymasarmongo.pymasar.retrieveconfig(mongoconn, collection)
        existedcfg = []
        for res in existedresult:
            existedcfg.append([res['configidx'],
                               res['name'],
                               res['desc'],
                               res['created_on'],
                               res['version'],
                               res['status']])
        newcfgdata = self._getnewconfigurationdata(existedcfg)
        if newcfgdata is None:
            # Nothing to be added.
            raise ValueError("Empty configuration.")

        newcfgname = newcfgdata[0]
        desc = newcfgdata[1]
        msystem = newcfgdata[2]
        # config data format: [[name], [desc], [pv files]]
        cfgdata = newcfgdata[3]
        pvs = []
        for pvf in cfgdata[2]:
            if pvf is not None and os.path.isfile(pvf):
                pvs += list(np.loadtxt(pvf, dtype=str, comments="#"))
        if pvs:
            for i, pv in enumerate(pvs):
                pvs[i] = pv.strip()
            pymasarmongo.pymasarmongo.pymasar.saveconfig(mongoconn, collection, newcfgname,
                                                         desc=desc,
                                                         system=msystem,
                                                         pvlist={"names": pvs})
            QMessageBox.information(self, "Congratulation", "A new configuration has been added successfully.")
        else:
            QMessageBox.warning(self, "Warning", "No PVs available for the new configuration.")

        pymasarmongo.db.utils.close(mongoconn)

    def submitmasarconfig(self):
        """submit a new configuration to MASAR database"""
        if self.dbsource is None:
            QMessageBox.warning(self, "Warning",
                                "Unknown database source.\nPlease select which database should be use.")
            return
        if self.dbsource == 0:
            self.savemasarsqlite()
        elif self.dbsource == 1:
            self.savemasarmongodb()

    def _getnewconfigurationdata(self, existedresult):
        """"""
        newcfgname = self.newConfigurationLineEdit.text()
        if newcfgname is None or str(newcfgname) == "":
            QMessageBox.warning(self, "Warning",
                                "Name of configuration is empty.")
            return None
        elif str(newcfgname) in np.array(existedresult)[:, 1]:
            QMessageBox.warning(self, "Warning",
                                "Configuration (%s) exists already." % str(newcfgname))
            return None
        else:
            newcfgname = str(newcfgname)
        desc = self.newConfigurationDescription.text()
        if str(desc) == "":
            desc = None
        else:
            desc = str(desc)

        msystem = str(self.systemComboBox.currentText())
        if msystem == "Others":
            msystem = self.systemLineEdit.text()
            if msystem is None or str(msystem) == "":
                QMessageBox.warning(self, "Warning",
                                    "System for configuration (%s) not specified yet." % str(newcfgname))
                return None
            else:
                msystem = str(msystem)

        pvgroups = self.newConfigTableWidget.rowCount()
        if pvgroups == 0:
            QMessageBox.warning(self, "Warning",
                                "No PV founded for new configuration (%s)." % str(newcfgname))
            return None

        pvgroupnames = []
        pvgroupdescs = []
        pvgroupfiles = []
        for count in range(pvgroups):
            # Collect PV group name information
            if self.newConfigTableWidget.item(count, 0) is not None and str(self.newConfigTableWidget.item(count, 0).text()) != "":
                pvgname = str(self.newConfigTableWidget.item(count, 0).text())
                if pvgname in pvgroupnames:
                    QMessageBox.warning(self, "Warning",
                                        "Duplicated pv group name: %s." % str(pvgname))
                    return None
                pvgroupnames.append(pvgname)
            elif self.newConfigTableWidget.item(count, 4) is None or str(self.newConfigTableWidget.item(count, 4)) == "":
                continue
            elif self.dbsource == 1:
                pvgroupnames.append(None)
            else:
                QMessageBox.warning(self, "Warning",
                                    "Empty pv group name.")
                return None
                # reply = QMessageBox.question(self, "Message",
                #                              "pv group name not specified for row {}.\nContinue?".format(count),
                #                              QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                # if reply == QMessageBox.Yes:
                #     pvgroupnames.append(None)
                # else:
                #     return None

            # Collection PV group descriptions
            if self.newConfigTableWidget.item(count, 1) is not None:
                pvgroupdescs.append(str(self.newConfigTableWidget.item(count, 1).text()))
            else:
                pvgroupdescs.append(None)

            # PV files for the pv group.
            if self.newConfigTableWidget.item(count, 4) is not None:
                pvgroupfiles.append(str(self.newConfigTableWidget.item(count, 4).text()))
            else:
                pvgroupfiles.append(None)

        if pvgroupfiles:
            return newcfgname, desc, msystem, [pvgroupnames, pvgroupdescs, pvgroupfiles]
        else:
            return None

    def currentselectedrow(self, row, col):
        """Cache current selected row in MASAR configuration Table Widget."""
        self.currentselectedrow4config = row

    def updateselectedsystem(self, system):
        """Update selected system if value changed"""
        self.selectedsystem = str(system)

    def updatesystemcombobox(self):
        """Update selected system if value changed"""
        self.systemComboBox.clear()
        if self.dbsource == 0:
            # get data from sqlite
            if self.usedefaultdb:
                # masardb = str(self.databaseDefault.text())
                masardb = str(self.databaseDefault.toPlainText())
            else:
                masardb = str(self.databaseLineEdit.text())

            if masardb != "":
                os.environ["MASAR_SQLITE_DB"] = masardb
            else:
                raise RuntimeError("Cannot find MASAR SQLite Database")

            import pymasarsqlite

            conn = pymasarsqlite.utils.connect()
            result = pymasarsqlite.service.retrieveServiceConfigProps(conn, propname="system", servicename="masar")
            index = 0
            if len(result) > 1:
                res = sorted(set(list(np.array(result[1:])[:, 3])))
                #for res in result[1:]:
                self.systemComboBox.addItems(res)
                index = len(res)
            self.systemComboBox.addItem("Others")
            self.systemComboBox.setCurrentIndex(index)
            pymasarsqlite.utils.close(conn)

        elif self.dbsource == 1:
            # get data from mongodb
            if self.usedefaultdb:
                database = str(self.databaseDefault.toPlainText())
                host = str(self.hostDefault.toPlainText())
                port = str(self.portDefault.toPlainText())
            else:
                database = str(self.databaseLineEdit.text())
                host = str(self.databaseHostLineEdit.text())
                port = str(self.databasePortLineEdit.text())

            import pymasarmongo

            mongoconn, collection = pymasarmongo.db.utils.conn(host=host, port=port, db=database)

            result = pymasarmongo.pymasarmongo.pymasar.retrieveconfig(mongoconn, collection)
            pymasarmongo.db.utils.close(mongoconn)

            results = []
            for res in result:
                if res["system"] not in results:
                    results.append(res["system"])
            res = sorted(set(results))
            self.systemComboBox.addItems(res)
            index = len(res)
            self.systemComboBox.addItem("Others")
            self.systemComboBox.setCurrentIndex(index)

    def listpvgroups(self):
        """"""
        self.pvgroupmodel.clear()
        self.pvgroupmodel.setHorizontalHeaderLabels(["PV Groups"])
        if self.dbsource == 0:
            # get data from sqlite
            if self.usedefaultdb:
                # masardb = str(self.databaseDefault.text())
                masardb = str(self.databaseDefault.toPlainText())
            else:
                masardb = str(self.databaseLineEdit.text())

            if masardb != "":
                os.environ["MASAR_SQLITE_DB"] = masardb
            else:
                raise RuntimeError("Cannot find MASAR SQLite Database")

            import pymasarsqlite

            conn = pymasarsqlite.utils.connect()
            result = pymasarsqlite.pvgroup.retrievePvGroups(conn)
            if len(result) > 0:
                result = sorted(result, key=itemgetter(0), reverse=True)
            for res in result:
                parent1 = QStandardItem(res[1])
                child1 = QStandardItem('id: {}'.format(res[0]))
                child2 = QStandardItem('description: {}'.format(res[2]))
                child3 = QStandardItem('date: {}'.format(res[3]))
                child4 = QStandardItem('version: {}'.format(res[4]))
                parent1.appendColumn([child1, child2, child3, child4])
                self.pvgroupmodel.appendRow(parent1)
            selmod = self.pvGroupTreeView.selectionModel()
            index2 = self.pvgroupmodel.indexFromItem(child3)
            selmod.select(index2, QItemSelectionModel.Select | QItemSelectionModel.Rows)
            pymasarsqlite.utils.close(conn)

            self.pvGroupTreeView.setContextMenuPolicy(Qt.CustomContextMenu)
            self.pvGroupTreeView.clicked.connect(self.showpvsinpvgroup)
            # self.connect(self.pvGroupTreeView,
            #              QtCore.SIGNAL("clicked(QModelIndex)"),
            #              #QtCore.SIGNAL("customContextMenuRequested(const QPoint &)"),
            #              self.doMenu)

        elif self.dbsource == 1:
            # get data from mongodb
            if self.usedefaultdb:
                database = str(self.databaseDefault.toPlainText())
                host = str(self.hostDefault.toPlainText())
                port = str(self.portDefault.toPlainText())
            else:
                database = str(self.databaseLineEdit.text())
                host = str(self.databaseHostLineEdit.text())
                port = str(self.databasePortLineEdit.text())

            import pymasarmongo

    def showpvsinpvgroup(self, point):
        reply = QMessageBox.question(self, 'Message',
                                     "show all pvs belong to group {} ?".format(point.model().
                                                                                itemFromIndex(point).
                                                                                text()),
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            pvgroupidx = int(str(point.model().itemFromIndex(point).child(0).text().split(":")[1]).strip())

            # msg = QMessageBox(self)
            msg = ShowPvMessageBox()
            msg.setWindowTitle('PVs for group {}'.format(point.model().itemFromIndex(point).text()))
            msg.setText("Click show details to see all pvs.")
            # windowTitle = 'PVs for group {}'.format(point.model().itemFromIndex(point).text())

            if self.dbsource == 0:
                # get data from sqlite
                if self.usedefaultdb:
                    # masardb = str(self.databaseDefault.text())
                    masardb = str(self.databaseDefault.toPlainText())
                else:
                    masardb = str(self.databaseLineEdit.text())

                if masardb != "":
                    os.environ["MASAR_SQLITE_DB"] = masardb
                else:
                    raise RuntimeError("Cannot find MASAR SQLite Database")

                import pymasarsqlite

                conn = pymasarsqlite.utils.connect()
                result = pymasarsqlite.pvgroup.retrieveGroupPvs(conn, pvgroupidx)
                text = "\n".join(list(np.array(result)[:, 0]))
                msg.setDetailedText(text)
                msg.exec_()

            elif self.dbsource == 1:
                # get data from mongodb
                if self.usedefaultdb:
                    database = str(self.databaseDefault.toPlainText())
                    host = str(self.hostDefault.toPlainText())
                    port = str(self.portDefault.toPlainText())
                else:
                    database = str(self.databaseLineEdit.text())
                    host = str(self.databaseHostLineEdit.text())
                    port = str(self.databasePortLineEdit.text())

                import pymasarmongo


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("NSLS II")
    app.setOrganizationDomain("BNL")
    app.setApplicationName("MASAR Database Manager")

    form = dbmanagerUI()
    form.show()
    app.exec_()

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
