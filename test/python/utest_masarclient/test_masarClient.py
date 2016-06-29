import sys
import unittest
import sqlite3
import os

from masarclient import masarClient
from pymasarsqlite.service.serviceconfig import (saveServiceConfig, retrieveServiceConfigs, retrieveServiceConfigPVs, saveServicePvGroup, retrieveServicePvGroups)
from pymasarsqlite.pvgroup.pvgroup import (savePvGroup, retrievePvGroups)
from pymasarsqlite.pvgroup.pv import (saveGroupPvs, retrieveGroupPvs)
from pymasarsqlite.service.service import (saveService)
from pymasarsqlite.masardata.masardata import (checkConnection, saveServiceEvent)
from masarclient.channelRPC import epicsExit

'''

Unittests for masarService/python/masarclient/masarClient.py

'''


class TestMasarClient(unittest.TestCase):

    def setUp(self):
        channel = 'masarService'
        self.mc = masarClient.client(channelname=channel)
        #DB SETUP
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
            res = saveGroupPvs(conn, pvgname, pvs)
            pvgroups = retrievePvGroups(conn)
            saveService(conn, servicename, desc='test desc')
            saveServiceConfig(conn, servicename, masarconf, system='SR', status='active',
                              configversion=20140420, configdesc='test desc')

            res == saveServicePvGroup(conn, masarconf, [pvgname])
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

    def testRetrieveSystemList(self):
        result = self.mc.retrieveSystemList()
        self.assertNotEqual(result, None)  # Can not be assertTrue because there is no case where it returns True
        self.assertNotEqual(result, False)  # Instead asserting both not None and not False
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 'SR')  # expected result

    def testRetrieveServiceConfigs(self):
        params = {'system': 'SR'}
        result = self.mc.retrieveServiceConfigs(params)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)
        self.assertEqual(len(result), 6)  # expected results
        self.assertEqual(1, result[0][0])
        self.assertEqual('SR_All_20140421', result[1][0])
        self.assertEqual('test desc', result[2][0])
        self.assertNotEqual(None, result[3][0])
        self.assertEqual('', result[4][0])
        self.assertEqual('active', result[5][0])

    def testRetrieveServiceEvents(self):
        print "RetrieveServiceEvents"
        params = {'configid': '1'}
        result = self.mc.retrieveServiceEvents(params)
        print "retrieveServiceEvents:  " +str(result)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)

    def testSaveSnapshot(self):
        params = {'configname': 'SR_All_20140421',
                  'servicename': 'masar'}
        result = self.mc.saveSnapshot(params)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)
        # The following tests are for expected outputs
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], ('masarExampleDoubleArray',))  # ChannelName
        self.assertEqual(result[2], ((),))  # Value
        self.assertEqual(result[3], (6,))  # DBR type
        self.assertEqual(result[4], (1,))  # isConnected
        self.assertEqual(result[5], (631152000,))  # SecondsPastEpoch
        self.assertEqual(result[6], (0,))  # NanoSeconds
        self.assertEqual(result[7], (0,))  # UserTag
        self.assertEqual(result[8], (3,))  # Severity
        self.assertEqual(result[9], (3,))  # Status
        self.assertEqual(result[10], ('UDF_ALARM',))  # Message

    def testRetrieveSnapshot(self):
        save_params = {'configname': 'SR_All_20140421',
                  'servicename': 'masar'}
        res1 = self.mc.saveSnapshot(save_params)
        self.assertNotEqual(res1, None)
        self.assertNotEqual(res1, False)
        event_id = res1[0]
        retrieve_params = {'eventid': str(event_id)}
        result = self.mc.retrieveSnapshot(retrieve_params)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)
        # The following tests are for expected outputs
        self.assertEqual(result[0], ('masarExampleDoubleArray',))  # ChannelName
        self.assertEqual(result[1], ((),))  # Value
        self.assertEqual(result[2], (6,))  # DBR type
        self.assertEqual(result[3], (1,))  # isConnected
        self.assertEqual(result[4], (631152000,))  # SecondsPastEpoch
        self.assertEqual(result[5], (0,))  # NanoSeconds
        self.assertEqual(result[6], (0,))  # UserTag
        self.assertEqual(result[7], (3,))  # Severity
        self.assertEqual(result[8], (3,))  # Status
        self.assertEqual(result[9], ('UDF_ALARM',))  # Message

    def testApproveSnapshot(self):
        save_params = {'configname': 'SR_All_20140421',
                       'servicename': 'masar'}

        res1 = self.mc.saveSnapshot(save_params)
        self.assertNotEqual(res1, None)
        self.assertNotEqual(res1, False)  # Can not be assertTrue because there is no case where it returns True
        event_id = res1[0]
        approve_params = {'eventid': str(event_id),
                  'configname': 'SR_All_20140421',
                  'user': 'test',
                  'desc': 'this is a good snapshot, and I approved it.'}
        result = self.mc.updateSnapshotEvent(approve_params)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)
        self.assertEqual(result, True)  # Expected Output

    def testGetLiveMachine(self):
        pvlist = ["masarExampleDoubleArray"]
        for i in range(len(pvlist)):
            params = {}
            for pv in pvlist[i:]:
                params[pv] = pv
                result = self.mc.getLiveMachine(params)
                self.assertNotEqual(result, None)
                self.assertNotEqual(result, False)
                # The following tests are for expected outputs
                self.assertEqual(result[0], ('masarExampleDoubleArray',))  # ChannelName
                self.assertEqual(result[1], ((),))  # Value
                self.assertEqual(result[2], (6,))  # DBR type
                self.assertEqual(result[3], (1,))  # isConnected
                self.assertEqual(result[4], (631152000,))  # SecondsPastEpoch
                self.assertEqual(result[5], (0,))  # NanoSeconds
                self.assertEqual(result[6], (0,))  # UserTag
                self.assertEqual(result[7], (3,))  # Severity
                self.assertEqual(result[8], (3,))  # Status
                self.assertEqual(result[9], ('UDF_ALARM',))  # Message

    if __name__ == '__main__':
        unittest.main()
