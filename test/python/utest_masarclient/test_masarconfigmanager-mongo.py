import unittest
import sqlite3
from utils.masarconfigmanager import *
from pymasarsqlite.service.serviceconfig import (saveServiceConfig, retrieveServiceConfigs, retrieveServiceConfigPVs, saveServicePvGroup)
from masarclient import masarClient
from masarclient.channelRPC import epicsExit
from pymasarmongo.db import utils
from pymasarmongo.config._config import masarconfig

from pymasarmongo.pymasarmongo.pymasar import saveconfig
from pymasarmongo.pymasarmongo.pymasar import updateconfig, retrieveconfig

'''

Unittests for masarService/python/utils/masarconfigmanager.py

'''


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        channel = 'masarService'
        self.mc = masarClient.client(channelname=channel)
        # DB SETUP
        self.conn, collection = utils.conn(host=masarconfig.get('mongodb', 'host'),
                                           port=masarconfig.get('mongodb', 'port'),
                                           db=masarconfig.get('mongodb', 'database'))

        self.conn.drop_database(masarconfig.get('mongodb', 'database'))
        name = "SR_All_20140421"
        params = {"desc": "SR daily SCR setpoint without IS kick and septum: SR and RF",
                  "system": "SR",
                  "status": "active",
                  "version": 20140421,
                  }
        newid = saveconfig(self.conn, collection, name, **params)
        # res0 = retrieveconfig(self.conn, collection, name)
        pvs = ["masarExample0000",
               "masarExample0001",
               # "masarExampleBoUninit",
               "masarExampleMbboUninit",
               "masarExample0002",
               "masarExample0003",
               "masarExample0004",
               "masarExampleCharArray",
               "masarExampleShortArray",
               "masarExampleLongArray",
               "masarExampleStringArray",
               "masarExampleFloatArray",
               "masarExampleDoubleArray",
               "masarExampleMbboUninitTest"]
        # TODO: Save will fail if list contains only 1 PV
        updateconfig(self.conn, collection, name, pvlist={"names": pvs})
        # res3 = retrieveconfig(self.conn, collection, name, withpvs=True)

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
