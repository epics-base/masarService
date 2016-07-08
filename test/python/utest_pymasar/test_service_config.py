import unittest
import sys
import sqlite3
import os

from masarclient import masarClient
from pymasarsqlite.service.serviceconfig import (saveServiceConfig, retrieveServiceConfigs, retrieveServiceConfigPVs, saveServicePvGroup, retrieveServicePvGroups)
from pymasarsqlite.pvgroup.pvgroup import (savePvGroup, retrievePvGroups)
from pymasarsqlite.pvgroup.pv import (saveGroupPvs, retrieveGroupPvs)
from pymasarsqlite.service.service import (saveService)
from pymasarsqlite.masardata.masardata import (checkConnection, saveServiceEvent)
from masarclient.channelRPC import epicsExit
class test_service_config(unittest.TestCase):

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

    def testConfiguration(self):
        channel = 'masarService'
        self.mc = masarClient.client(channelname=channel)
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
            pvs = ["masarExampleDoubleArray"]
            res = savePvGroup(conn, pvgname, func=pvgdesc)
            self.assertEqual([1], res)
            res2 = saveGroupPvs(conn, pvgname, pvs)
            with self.assertRaises(Exception) as context:
                saveGroupPvs(conn, "badname", pvs)
            self.assertEqual(context.exception.message, 'pv group name (badname) is not unique, or not exist.')
            self.assertEqual([1], res2)
            pvgroups = retrievePvGroups(conn)
            self.assertEqual(5, len(pvgroups[0]))
            self.assertEqual(1, pvgroups[0][0])
            self.assertEqual(pvgname, pvgroups[0][1])
            self.assertEqual(pvgdesc, pvgroups[0][2])
            self.assertNotEqual(None, pvgroups[0][3])
            # The following 2 tests are to confirm the date string is in the correct format
            self.assertEqual(3, len(pvgroups[0][3].split('-')))
            self.assertEqual(3, len(pvgroups[0][3].split(':')))
            self.assertEqual(None, pvgroups[0][4])
            test_desc = 'test desc'
            test_system = 'SR'
            test_status = 'active'
            test_version = 20140420
            saveService(conn, servicename, desc=test_desc)

            with self.assertRaises(Exception) as context:
                saveServiceConfig(conn, "bad servicename", masarconf, system=test_system, status=test_status,
                              configversion=test_version, configdesc=test_desc)
            self.assertEqual("service with given name (bad servicename) does not exist.", context.exception.message)
            with self.assertRaises(Exception) as context:
                saveServiceConfig(conn, servicename, masarconf, system=test_system, status="bad status",
                              configversion=test_version, configdesc=test_desc)
            self.assertEqual("Service status has to be either active, or inactive", context.exception.message)
            saveServiceConfig(conn, servicename, masarconf, system=test_system, status=test_status,
                              configversion=test_version, configdesc=test_desc)
            with self.assertRaises(Exception) as context:
                saveServiceConfig(conn, servicename, masarconf, system=test_system, status=test_status,
                                  configversion=test_version, configdesc=test_desc)
            self.assertEqual('service config exists already.', context.exception.message)

            with self.assertRaises(IndexError):  # TODO: Should this be a more specific error message?
                saveServicePvGroup(conn, "bad config", [pvgname])
            with self.assertRaises(Exception) as context:
                res3 = saveServicePvGroup(conn, masarconf, ["bad pvgname"])  # this test prints a message to console
            self.assertEqual("given pv group name (bad pvgname) does not exist.", context.exception.message)
            res3 = saveServicePvGroup(conn, masarconf, [pvgname])
            self.assertEqual([1], res3)
            with self.assertRaises(Exception) as context:
                pvlist = retrieveServiceConfigPVs(conn, masarconf, servicename="bad servicename")
            pvlist = retrieveServiceConfigPVs(conn, masarconf, servicename=servicename)
            self.assertEqual(context.exception.message, 'Given service (bad servicename) does not exist.')
            self.assertEqual(pvs, pvlist)
            results = retrieveServiceConfigs(conn, "bad servicename", masarconf)
            self.assertEqual(1, len(results))  # IE: no data returned
            self.assertEqual(6, len(results[0]))
            self.assertEqual('config_idx', results[0][0])
            self.assertEqual('config_name', results[0][1])
            self.assertEqual('config_desc', results[0][2])
            self.assertEqual('config_create_date', results[0][3])
            self.assertEqual('config_version', results[0][4])
            self.assertEqual('status', results[0][5])
            results = retrieveServiceConfigs(conn, servicename, "bad conf")
            self.assertEqual(1, len(results))  # IE: no data returned
            self.assertEqual(6, len(results[0]))
            self.assertEqual('config_idx', results[0][0])
            self.assertEqual('config_name', results[0][1])
            self.assertEqual('config_desc', results[0][2])
            self.assertEqual('config_create_date', results[0][3])
            self.assertEqual('config_version', results[0][4])
            self.assertEqual('status', results[0][5])
            results = retrieveServiceConfigs(conn, servicename, masarconf)
            # Label tests
            self.assertEqual(6, len(results[0]))
            self.assertEqual(2, len(results))
            self.assertEqual('config_idx', results[0][0])
            self.assertEqual('config_name', results[0][1])
            self.assertEqual('config_desc', results[0][2])
            self.assertEqual('config_create_date', results[0][3])
            self.assertEqual('config_version', results[0][4])
            self.assertEqual('status', results[0][5])
            # Data tests
            self.assertEqual(6, len(results[1]))
            self.assertEqual(1, results[1][0])
            self.assertEqual(masarconf, results[1][1])
            self.assertEqual(test_desc, results[1][2])
            self.assertNotEqual(None, results[1][3])
            # The following 2 tests are to confirm the date string is in the correct format
            self.assertEqual(3, len(results[1][3].split('-')))
            self.assertEqual(3, len(results[1][3].split(':')))
            self.assertEqual(test_version, results[1][4])
            self.assertEqual(test_status, results[1][5])
            conn.commit()
            conn.close()
        except sqlite3.Error, e:
            print ("Error %s:" % e.args[0])
            raise

    if __name__ == '__main__':
        unittest.main()
