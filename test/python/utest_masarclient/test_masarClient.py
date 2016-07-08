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

            res = saveServicePvGroup(conn,  masarconf, [pvgname])
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
        self.mc = None

    def testRetrieveSystemList(self):
        result = self.mc.retrieveSystemList()
        self.assertNotEqual(result, None)  # Can not be assertTrue because there is no case where it returns True
        self.assertNotEqual(result, False)  # Instead asserting both not None and not False
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 'SR')  # expected result

    def testRetrieveServiceConfigs(self):
        params = {'system': 'SR'}
        # Test should return empty data set as 'bad system' does not exist
        bad_params = {'system': 'bad system'}
        bad_res = self.mc.retrieveServiceConfigs(bad_params)
        self.assertEqual((), bad_res[0])
        self.assertEqual((), bad_res[1])
        self.assertEqual((), bad_res[2])
        self.assertEqual((), bad_res[3])
        self.assertEqual((), bad_res[4])
        self.assertEqual((), bad_res[5])
        # Remaining tests are for expected results
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
        bad_params = {'configname': 'SR_All_20140421',
                  'servicename': 'bad_servicename'}
        params = {'configname': 'SR_All_20140421',
                  'servicename': 'masar'}
        bad_res = self.mc.saveSnapshot(bad_params)
        self.assertEqual(False, bad_res)
        result = self.mc.saveSnapshot(params)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)
        # The following tests are for expected outputs
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1][0], 'masarExample0000')  # ChannelName 0
        self.assertEqual(result[1][1], 'masarExample0001')  # ChannelName 1
        self.assertEqual(result[1][2], 'masarExampleBoUninit')  # ChannelName 2
        self.assertEqual(result[1][3], 'masarExampleMbboUninit')  # ChannelName 3
        self.assertEqual(result[1][4], 'masarExample0002')  # ChannelName 4
        self.assertEqual(result[1][5], 'masarExample0003')  # ChannelName 5
        self.assertEqual(result[1][6], 'masarExample0004')  # ChannelName 6
        self.assertEqual(result[1][7], 'masarExampleCharArray')  # ChannelName 7
        self.assertEqual(result[1][8], 'masarExampleShortArray')  # ChannelName 8
        self.assertEqual(result[1][9], 'masarExampleLongArray')  # ChannelName 9
        self.assertEqual(result[1][10], 'masarExampleStringArray')  # ChannelName 10
        self.assertEqual(result[1][11], 'masarExampleFloatArray')  # ChannelName 11
        self.assertEqual(result[1][12], 'masarExampleDoubleArray')  # ChannelName 12
        self.assertEqual(result[1][13], 'masarExampleMbboUninitTest')  # ChannelName 13
        self.assertEqual(result[2][0], 10)  # 0000 Value
        self.assertEqual(result[2][1], 'string value')  # 0001 Value
        self.assertEqual(result[2][2], 0)  # BoUninit Value
        self.assertEqual(result[2][3], 1)  # MbboUninit Value
        self.assertEqual(result[2][4], 'zero')  # 0002 Value
        self.assertEqual(result[2][5], 'one')  # 0003 Value
        self.assertEqual(result[2][6], 1.9)  # 0004 Value
        self.assertEqual(result[2][7], ())  # CharArray Value
        self.assertEqual(result[2][8], ())  # ShortArray Value
        self.assertEqual(result[2][9], ())  # LongArray Value
        self.assertEqual(result[2][10], ())  # StringArray Value
        self.assertEqual(result[2][11], ())  # FloatArrayValue
        self.assertEqual(result[2][12], ())  # DoubleArray Value
        self.assertEqual(result[2][13], 1)  # MbboUninitTest Value
        self.assertEqual(result[3], (5, 0, 0, 5, 0, 0, 6, 4, 1, 5, 0, 2, 6, 5))  # DBR type
        self.assertEqual(result[4], (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1))  # isConnected
        self.assertEqual(result[5], (631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000))  # SecondsPastEpoch
        self.assertEqual(result[6], (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))  # NanoSeconds
        self.assertEqual(result[7], (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))  # UserTag
        self.assertEqual(result[8], (0, 0, 3, 0, 3, 0, 0, 3, 3, 3, 3, 3, 3, 0))  # Severity
        self.assertEqual(result[9], (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3))  # Status
        self.assertEqual(result[10], ('UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM'))  # Message

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
        self.assertEqual(result[0][0], 'masarExample0000')  # ChannelName 0
        self.assertEqual(result[0][1], 'masarExample0001')  # ChannelName 1
        self.assertEqual(result[0][2], 'masarExampleBoUninit')  # ChannelName 2
        self.assertEqual(result[0][3], 'masarExampleMbboUninit')  # ChannelName 3
        self.assertEqual(result[0][4], 'masarExample0002')  # ChannelName 4
        self.assertEqual(result[0][5], 'masarExample0003')  # ChannelName 5
        self.assertEqual(result[0][6], 'masarExample0004')  # ChannelName 6
        self.assertEqual(result[0][7], 'masarExampleCharArray')  # ChannelName 7
        self.assertEqual(result[0][8], 'masarExampleShortArray')  # ChannelName 8
        self.assertEqual(result[0][9], 'masarExampleLongArray')  # ChannelName 9
        self.assertEqual(result[0][10], 'masarExampleStringArray')  # ChannelName 10
        self.assertEqual(result[0][11], 'masarExampleFloatArray')  # ChannelName 11
        self.assertEqual(result[0][12], 'masarExampleDoubleArray')  # ChannelName 12
        self.assertEqual(result[0][13], 'masarExampleMbboUninitTest')  # ChannelName 13
        self.assertEqual(result[1][0], 10)  # 0000 Value
        self.assertEqual(result[1][1], 'string value')  # 0001 Value
        self.assertEqual(result[1][2], '0')  # BoUninit Value (appropriately returned as string)
        self.assertEqual(result[1][3], 1)  # MbboUninit Value
        self.assertEqual(result[1][4], 'zero')  # 0002 Value
        self.assertEqual(result[1][5], 'one')  # 0003 Value
        self.assertEqual(result[1][6], 1.9)  # 0004 Value
        self.assertEqual(result[1][7], ())  # CharArray Value
        self.assertEqual(result[1][8], ())  # ShortArray Value
        self.assertEqual(result[1][9], ())  # LongArray Value
        self.assertEqual(result[1][10], ())  # StringArray Value
        self.assertEqual(result[1][11], ())  # FloatArrayValue
        self.assertEqual(result[1][12], ())  # DoubleArray Value
        self.assertEqual(result[1][13], 1)  # MbboUninitTest Value
        self.assertEqual(result[2], (5, 0, 0, 5, 0, 0, 6, 4, 1, 5, 0, 2, 6, 5))  # DBR type
        self.assertEqual(result[3], (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1))  # isConnected
        self.assertEqual(result[4], (631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000))  # SecondsPastEpoch
        self.assertEqual(result[5], (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))  # NanoSeconds
        self.assertEqual(result[6], (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))  # UserTag
        self.assertEqual(result[7], (0, 0, 3, 0, 3, 0, 0, 3, 3, 3, 3, 3, 3, 0))  # Severity
        self.assertEqual(result[8], (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3))  # Status
        self.assertEqual(result[9], ('UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM'))  # Message

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
        pvlist = {"masarExample0000": "masarExample0000",
                  "masarExample0001": "masarExample0001",
                  "masarExampleBoUninit": "masarExampleBoUninit",
                  "masarExampleMbboUninit": "masarExampleMbboUninit",
                  "masarExample0002": "masarExample0002",
                  "masarExample0003": "masarExample0003",
                  "masarExample0004": "masarExample0004",
                  "masarExampleCharArray": "masarExampleCharArray",
                  "masarExampleShortArray": "masarExampleShortArray",
                  "masarExampleLongArray": "masarExampleLongArray",
                  "masarExampleStringArray": "masarExampleStringArray",
                  "masarExampleFloatArray": "masarExampleFloatArray",
                  "masarExampleDoubleArray": "masarExampleDoubleArray",
                  "masarExampleMbboUninitTest": "masarExampleMbboUninitTest"}
        result = self.mc.getLiveMachine(pvlist)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)
        # The following tests are for expected outputs
        self.assertEqual(result[0][0], 'masarExampleCharArray')  # ChannelName 0
        self.assertEqual(result[0][1], 'masarExample0004')  # ChannelName 1
        self.assertEqual(result[0][2], 'masarExampleDoubleArray')  # ChannelName 2
        self.assertEqual(result[0][3], 'masarExample0002')  # ChannelName 3
        self.assertEqual(result[0][4], 'masarExample0003')  # ChannelName 4
        self.assertEqual(result[0][5], 'masarExample0000')  # ChannelName 5
        self.assertEqual(result[0][6], 'masarExample0001')  # ChannelName 6
        self.assertEqual(result[0][7], 'masarExampleStringArray')  # ChannelName 7
        self.assertEqual(result[0][8], 'masarExampleLongArray')  # ChannelName 8
        self.assertEqual(result[0][9], 'masarExampleShortArray')  # ChannelName 9
        self.assertEqual(result[0][10], 'masarExampleMbboUninitTest')  # ChannelName 10
        self.assertEqual(result[0][11], 'masarExampleMbboUninit')  # ChannelName 10
        self.assertEqual(result[0][12], 'masarExampleFloatArray')  # ChannelName 11
        self.assertEqual(result[0][13], 'masarExampleBoUninit')  # ChannelName 12
        self.assertEqual(result[1][0], ())  # CharArray Value
        self.assertEqual(result[1][1], 1.9)  # 0004 Value
        self.assertEqual(result[1][2], ())  # DoubleArray Value
        self.assertEqual(result[1][3], 'zero')  # 0002 Value
        self.assertEqual(result[1][4], 'one')  # 0003 Value
        self.assertEqual(result[1][5], 10)  # 0000 Value
        self.assertEqual(result[1][6], 'string value')  # 0001 Value
        self.assertEqual(result[1][7], ())  # StringArray Value
        self.assertEqual(result[1][8], ())  # LongArray Value
        self.assertEqual(result[1][9], ())  # ShortArray Value
        self.assertEqual(result[1][10], 1)  # MbboUninitTest Value
        self.assertEqual(result[1][11], 1)  # MbboUninit Value
        self.assertEqual(result[1][12], ())  # FloatArray Value
        self.assertEqual(result[1][13], 0)  # BoUninit Value
        self.assertEqual(result[2], (4, 6, 6, 0, 0, 5, 0, 0, 5, 1, 5, 5, 2, 0))  # DBR type
        self.assertEqual(result[3], (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1))  # isConnected
        self.assertEqual(result[4], (631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000))  # SecondsPastEpoch
        self.assertEqual(result[5], (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))  # NanoSeconds
        self.assertEqual(result[6], (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))  # UserTag
        self.assertEqual(result[7], (3, 0, 3, 3, 0, 0, 0, 3, 3, 3, 0, 0, 3, 3))  # Severity
        self.assertEqual(result[8], (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3))  # Status
        self.assertEqual(result[9], ('UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM'))  # Message

    if __name__ == '__main__':
        unittest.main()
