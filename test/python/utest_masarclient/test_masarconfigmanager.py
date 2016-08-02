import unittest
import sqlite3
from utils.masarconfigmanager import *
from pymasarsqlite.service.serviceconfig import (saveServiceConfig, retrieveServiceConfigs, retrieveServiceConfigPVs, saveServicePvGroup)
from pymasarsqlite.pvgroup.pvgroup import (savePvGroup, retrievePvGroups)
from pymasarsqlite.pvgroup.pv import (saveGroupPvs)
from pymasarsqlite.service.service import (saveService)
from unittest_utils import SQLITE_DB_TEST_SETUP, SQLITE_DROP_ALL_TABLES
'''

Unittests for masarService/python/utils/masarconfigmanager.py

'''


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        SQLITE_DB_TEST_SETUP()

    def tearDown(self):
        SQLITE_DROP_ALL_TABLES()

    def testReadConfFile(self):
        app = QtGui.QApplication(sys.argv)
        ui = dbmanagerUI()
        self.assertEqual("MasarService", ui.defaultdbinfo.get("mongodb", "database"))
        self.assertEqual("localhost", ui.defaultdbinfo.get("mongodb", "host"))
        self.assertEqual("27017", ui.defaultdbinfo.get("mongodb", "port"))
        self.assertEqual("test", ui.defaultdbinfo.get("mongodb", "username"))

    def testShowMasarConfigs(self):
        app = QtGui.QApplication(sys.argv)
        ui = dbmanagerUI()
        ui.dbsource = 0  # Called normally with menu selection
        ui.databaseDefault.setText(os.environ["MASAR_SQLITE_DB"])
        ui.databaseLineEdit.setText(os.environ["MASAR_SQLITE_DB"])
        #ui.defaultsqlitedb()
        ui.showmasarconfigs()
        self.assertEqual(1, ui.masarConfigTableWidget.rowCount())
        self.assertEqual("1", ui.masarConfigTableWidget.item(0, 0).text())
        self.assertEqual("SR_All_20140421", ui.masarConfigTableWidget.item(0, 1).text())
        self.assertEqual("test desc", ui.masarConfigTableWidget.item(0, 2).text())
        self.assertNotEqual(None, ui.masarConfigTableWidget.item(0, 3).text())
        self.assertEqual("20140420", ui.masarConfigTableWidget.item(0, 4).text())

    def testListPVGroups(self):
        app = QtGui.QApplication(sys.argv)
        ui = dbmanagerUI()
        ui.dbsource = 0  # Called normally with menu selection
        ui.databaseDefault.setText(os.environ["MASAR_SQLITE_DB"])
        ui.databaseLineEdit.setText(os.environ["MASAR_SQLITE_DB"])
        #ui.defaultsqlitedb()
        ui.listpvgroups()
        self.assertEqual('masarpvgroup', ui.pvgroupmodel.takeRow(0)[0].text())

    def testUpdateMasarConfigStatus(self):
        app = QtGui.QApplication(sys.argv)
        ui = dbmanagerUI()
        ui.dbsource = 0  # Called normally with menu selection
        ui.databaseDefault.setText(os.environ["MASAR_SQLITE_DB"])
        ui.databaseLineEdit.setText(os.environ["MASAR_SQLITE_DB"])
        #ui.defaultsqlitedb()
        __sqlitedb__ = os.environ["MASAR_SQLITE_DB"]
        with sqlite3.connect(__sqlitedb__) as conn:
            masarconf = 'SR_All_20140421'
            servicename = 'masar'
            ui.updatemasarconfigstatus("inactive",1)
            results = retrieveServiceConfigs(conn, servicename, masarconf)
            self.assertEqual("inactive", results[1][5])
            ui.updatemasarconfigstatus("active",1)
            results = retrieveServiceConfigs(conn, servicename, masarconf)
            self.assertEqual("active", results[1][5])
            conn.commit()

    def testSaveMasarSqlite(self):
        app = QtGui.QApplication(sys.argv)
        ui = dbmanagerUI()
        ui.dbsource = 0  # Called normally with menu selection
        ui.databaseDefault.setText(os.environ["MASAR_SQLITE_DB"])
        ui.databaseLineEdit.setText(os.environ["MASAR_SQLITE_DB"])
        #ui.defaultsqlitedb()
        ui.test_in_progress_flag = 1
        ui.savemasarsqlite()
        __sqlitedb__ = os.environ["MASAR_SQLITE_DB"]
        with sqlite3.connect(__sqlitedb__) as conn:
            masarconf = 'newcfgname'
            servicename = 'masar'
            results = retrieveServiceConfigs(conn, servicename, masarconf)
            self.assertEqual('newcfgname', results[1][1])
            self.assertEqual('newcfgdesc', results[1][2])
            conn.commit()

    def testUpdateSystemComboBox(self):
        app = QtGui.QApplication(sys.argv)
        ui = dbmanagerUI()
        ui.dbsource = 0  # Called normally with menu selection
        ui.databaseDefault.setText(os.environ["MASAR_SQLITE_DB"])
        ui.databaseLineEdit.setText(os.environ["MASAR_SQLITE_DB"])
        #ui.defaultsqlitedb()
        ui.updatesystemcombobox()
        self.assertEqual("SR", ui.systemComboBox.itemText(0))

    if __name__ == '__main__':
        unittest.main()
