import unittest
import sqlite3
from utils.masarconfigmanager import *
from pymasarsqlite.service.serviceconfig import (saveServiceConfig, retrieveServiceConfigs, retrieveServiceConfigPVs, saveServicePvGroup)
from masarclient.channelRPC import epicsExit
from pymasarmongo.db import utils
from pymasarmongo.config._config import masarconfig

from pymasarmongo.pymasarmongo.pymasar import saveconfig
from pymasarmongo.pymasarmongo.pymasar import updateconfig, retrieveconfig
from unittest_utils import MONGODB_TEST_SETUP
'''

Unittests for masarService/python/utils/masarconfigmanager.py

'''


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.conn = MONGODB_TEST_SETUP(self)

    def tearDown(self):
        self.conn.drop_database(masarconfig.get('mongodb', 'database'))
        utils.close(self.conn)

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
        ui.dbsource = 1  # Called normally with menu selection
        ui.defaultmongodb()
        ui.showmasarconfigs()
        self.assertEqual(1, ui.masarConfigTableWidget.rowCount())
        self.assertEqual("1", ui.masarConfigTableWidget.item(0, 0).text())
        self.assertEqual("SR_All_20140421", ui.masarConfigTableWidget.item(0, 1).text())
        self.assertEqual("SR daily SCR setpoint without IS kick and septum: SR and RF", ui.masarConfigTableWidget.item(0, 2).text())
        self.assertNotEqual(None, ui.masarConfigTableWidget.item(0, 3).text())
        self.assertEqual("20140421", ui.masarConfigTableWidget.item(0, 4).text())


    def testUpdateMasarConfigStatus(self):
        app = QtGui.QApplication(sys.argv)
        ui = dbmanagerUI()
        ui.dbsource = 1  # Called normally with menu selection
        ui.defaultmongodb()
        masarconf = 'SR_All_20140421'
        conn, collection = utils.conn(host=masarconfig.get('mongodb', 'host'),
                                           port=masarconfig.get('mongodb', 'port'),
                                           db=masarconfig.get('mongodb', 'database'))
        ui.updatemasarconfigstatus("inactive", 1)
        res3 = retrieveconfig(conn, collection, masarconf, withpvs=True)
        self.assertEqual("inactive", res3[0]['status'])
        ui.updatemasarconfigstatus("active",1)
        res3 = retrieveconfig(conn, collection, masarconf, withpvs=True)
        self.assertEqual("active", res3[0]['status'])

    def testSaveMasarMongoDB(self):
        app = QtGui.QApplication(sys.argv)
        ui = dbmanagerUI()
        ui.dbsource = 1  # Called normally with menu selection
        ui.defaultmongodb()
        ui.test_in_progress_flag = 1
        ui.savemasarmongodb()
        masarconf = 'newcfgname'
        conn, collection = utils.conn(host=masarconfig.get('mongodb', 'host'),
                                           port=masarconfig.get('mongodb', 'port'),
                                           db=masarconfig.get('mongodb', 'database'))
        res3 = retrieveconfig(conn, collection, masarconf, withpvs=True)
        self.assertEqual('newcfgname', res3[0]['name'])
        self.assertEqual('newmsystem', res3[0]['system'])
        self.assertEqual('newcfgdesc', res3[0]['desc'])

    def testUpdateSystemComboBox(self):
        app = QtGui.QApplication(sys.argv)
        ui = dbmanagerUI()
        ui.dbsource = 1  # Called normally with menu selection
        ui.defaultmongodb()
        ui.updatesystemcombobox()
        self.assertEqual("SR", ui.systemComboBox.itemText(0))

    if __name__ == '__main__':
        unittest.main()
