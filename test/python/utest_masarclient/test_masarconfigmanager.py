import unittest
import sqlite3
from utils.masarconfigmanager import *
from pymasarsqlite.service.serviceconfig import (saveServiceConfig, retrieveServiceConfigs, retrieveServiceConfigPVs, saveServicePvGroup)
from pymasarsqlite.pvgroup.pvgroup import (savePvGroup, retrievePvGroups)
from pymasarsqlite.pvgroup.pv import (saveGroupPvs)
from pymasarsqlite.service.service import (saveService)

'''

Unittests for masarService/python/utils/masarconfigmanager.py

'''


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        channel = 'masarService'
        # DB SETUP
        __sqlitedb__ = os.environ["MASAR_SQLITE_DB"]
        try:
            conn = sqlite3.connect(__sqlitedb__)
            cur = conn.cursor()
            __sql__ = None
            if __sql__ is None:
                from pymasarsqlite.db.masarsqlite import SQL
            else:
                sqlfile = open(__sql__)
                SQL = sqlfile.read()
            if SQL is None:
                print ('SQLite script is empty. Cannot create SQLite db.')
                sys.exit()
            else:
                cur.executescript(SQL)
                cur.execute("PRAGMA main.page_size= 4096;")
                cur.execute("PRAGMA main.default_cache_size= 10000;")
                cur.execute("PRAGMA main.locking_mode=EXCLUSIVE;")
                cur.execute("PRAGMA main.synchronous=NORMAL;")
                cur.execute("PRAGMA main.journal_mode=WAL;")
                cur.execute("PRAGMA main.temp_store = MEMORY;")

            cur.execute('select name from sqlite_master where type=\'table\'')
            masarconf = 'SR_All_20140421'
            servicename = 'masar'

            pvgname = 'masarpvgroup'
            pvgdesc = 'this is my new pv group for masar service with same group name'
            pvs = ["masarExample0000",
                   "masarExample0001",
                   "masarExampleBoUninit",
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
            res = savePvGroup(conn, pvgname, func=pvgdesc)
            res = saveGroupPvs(conn, pvgname, pvs)
            pvgroups = retrievePvGroups(conn)
            saveService(conn, servicename, desc='test desc')
            saveServiceConfig(conn, servicename, masarconf, system='SR', status='active',
                              configversion=20140420, configdesc='test desc')

            res = saveServicePvGroup(conn, masarconf, [pvgname])
            pvlist = retrieveServiceConfigPVs(conn, masarconf, servicename=servicename)
            results = retrieveServiceConfigs(conn, servicename, masarconf)
            conn.commit()
            conn.close()
        except sqlite3.Error, e:
            print ("Error %s:" % e.args[0])
            raise

    def tearDown(self):
        __sqlitedb__ = os.environ["MASAR_SQLITE_DB"]
        try:
            conn = sqlite3.connect(__sqlitedb__)
            cur = conn.cursor()
            cur.execute("drop table if exists masar_data")
            cur.execute("drop table if exists pv")
            cur.execute("drop table if exists pv_pvgroup")
            cur.execute("drop table if exists pv_group")
            cur.execute("drop table if exists pvgroup_serviceconfig")
            cur.execute("drop table if exists service")
            cur.execute("drop table if exists service_config")
            cur.execute("drop table if exists service_config_prop")
            cur.execute("drop table if exists service_event")
            cur.execute("drop table if exists service_event_prop")
        except:
            raise
        finally:
            conn.commit()
            conn.close()

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
        conn = sqlite3.connect(__sqlitedb__)
        masarconf = 'SR_All_20140421'
        servicename = 'masar'
        ui.updatemasarconfigstatus("inactive",1)
        results = retrieveServiceConfigs(conn, servicename, masarconf)
        self.assertEqual("inactive", results[1][5])
        ui.updatemasarconfigstatus("active",1)
        results = retrieveServiceConfigs(conn, servicename, masarconf)
        self.assertEqual("active", results[1][5])

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
        conn = sqlite3.connect(__sqlitedb__)
        masarconf = 'newcfgname'
        servicename = 'masar'
        results = retrieveServiceConfigs(conn, servicename, masarconf)
        self.assertEqual('newcfgname', results[1][1])
        self.assertEqual('newcfgdesc', results[1][2])

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
