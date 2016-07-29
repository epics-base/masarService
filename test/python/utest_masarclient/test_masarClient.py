import sys
import unittest
import sqlite3
import os

from masarclient import masarClient
from pymasarsqlite.service.serviceconfig import (saveServiceConfig, retrieveServiceConfigs, retrieveServiceConfigPVs, saveServicePvGroup, retrieveServicePvGroups)
from pymasarsqlite.pvgroup.pvgroup import (savePvGroup, retrievePvGroups)
from pymasarsqlite.pvgroup.pv import (saveGroupPvs, retrieveGroupPvs)
from pymasarsqlite.service.service import (saveService)
from unittest_utils import SQLITE_DB_TEST_SETUP, SQLITE_DROP_ALL_TABLES

'''

Unittests for masarService/python/masarclient/masarClient.py

'''


class TestMasarClient(unittest.TestCase):

    def setUp(self):
        channel = 'sqliteMasarTestService'
        self.mc = masarClient.client(channelname=channel)
        SQLITE_DB_TEST_SETUP()


    def tearDown(self):
        SQLITE_DROP_ALL_TABLES()

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
        params = {'configid': '1'}
        result = self.mc.retrieveServiceEvents(params)
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
        expected_result = (1, ('masarExample0000',  # ChannelName 0
                                'masarExample0001',  # ChannelName 1
                                'masarExampleBoUninit',  # ChannelName 2
                                'masarExampleMbboUninit',  # ChannelName 3
                                'masarExample0002',  # ChannelName 4
                                'masarExample0003',  # ChannelName 5
                                'masarExample0004',  # ChannelName 6
                                'masarExampleCharArray',  # ChannelName 7
                                'masarExampleShortArray',  # ChannelName 8
                                'masarExampleLongArray',  # ChannelName 9
                                'masarExampleStringArray',  # ChannelName 10
                                'masarExampleFloatArray',  # ChannelName 11
                                'masarExampleDoubleArray',  # ChannelName 12
                                'masarExampleMbboUninitTest'),  # ChannelName 13
                                (10,  # 0000 Value
                                'string value',  # 0001 Value
                                0,  # BoUninit Value
                                1,  # MbboUninit Value
                                'zero',  # 0002 Value
                                'one',  # 0003 Value
                                1.9,  # 0004 Value
                                (),  # CharArray Value
                                (),  # ShortArray Value
                                (),  # LongArray Value
                                (),  # StringArray Value
                                (),  # FloatArrayValue
                                (),  # DoubleArray Value
                                1),  # MbboUninitTest Value
                                (5, 0, 0, 5, 0, 0, 6, 4, 1, 5, 0, 2, 6, 5),  # DBR type
                                (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),  # isConnected
                                (631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000),  # SecondsPastEpoch
                                (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  # NanoSeconds
                                (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  # UserTag
                                (0, 0, 3, 0, 3, 0, 0, 3, 3, 3, 3, 3, 3, 0),  # Severity
                                (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),  # Status
                                ('UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM'))  # Message
        self.assertSequenceEqual(result, expected_result)

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
        expected_result = (('masarExample0000',  # ChannelName 0
                               'masarExample0001',  # ChannelName 1
                               'masarExampleBoUninit',  # ChannelName 2
                               'masarExampleMbboUninit',  # ChannelName 3
                               'masarExample0002',  # ChannelName 4
                               'masarExample0003',  # ChannelName 5
                               'masarExample0004',  # ChannelName 6
                               'masarExampleCharArray',  # ChannelName 7
                               'masarExampleShortArray',  # ChannelName 8
                               'masarExampleLongArray',  # ChannelName 9
                               'masarExampleStringArray',  # ChannelName 10
                               'masarExampleFloatArray',  # ChannelName 11
                               'masarExampleDoubleArray',  # ChannelName 12
                               'masarExampleMbboUninitTest'),  # ChannelName 13
                           (10,  # 0000 Value
                            'string value',  # 0001 Value
                            '0',  # BoUninit Value
                            1,  # MbboUninit Value
                            'zero',  # 0002 Value
                            'one',  # 0003 Value
                            1.9,  # 0004 Value
                            (),  # CharArray Value
                            (),  # ShortArray Value
                            (),  # LongArray Value
                            (),  # StringArray Value
                            (),  # FloatArrayValue
                            (),  # DoubleArray Value
                            1),  # MbboUninitTest Value
                           (5, 0, 0, 5, 0, 0, 6, 4, 1, 5, 0, 2, 6, 5),  # DBR type
                           (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),  # isConnected
                           (631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000,
                            631152000, 631152000, 631152000, 631152000, 631152000, 631152000),  # SecondsPastEpoch
                           (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  # NanoSeconds
                           (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  # UserTag
                           (0, 0, 3, 0, 3, 0, 0, 3, 3, 3, 3, 3, 3, 0),  # Severity
                           (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),  # Status
                           ('UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM',
                            'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM',
                            'UDF_ALARM'))  # Message
        self.assertSequenceEqual(result, expected_result)

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
        expected_result = (('masarExampleCharArray',  # ChannelName 0
                             'masarExample0004',  # ChannelName 1
                             'masarExampleDoubleArray',  # ChannelName 2
                             'masarExample0002',  # ChannelName 3
                             'masarExample0003',  # ChannelName 4
                             'masarExample0000',  # ChannelName 5
                             'masarExample0001',  # ChannelName 6
                             'masarExampleStringArray',  # ChannelName 7
                             'masarExampleLongArray',  # ChannelName 8
                             'masarExampleShortArray',  # ChannelName 9
                             'masarExampleMbboUninitTest',  # ChannelName 10
                             'masarExampleMbboUninit',  # ChannelName 10
                             'masarExampleFloatArray',  # ChannelName 11
                             'masarExampleBoUninit'),  # ChannelName 12
                             ((),  # CharArray Value
                             1.9,  # 0004 Value
                             (),  # DoubleArray Value
                             'zero',  # 0002 Value
                             'one',  # 0003 Value
                             10,  # 0000 Value
                             'string value',  # 0001 Value
                             (),  # StringArray Value
                             (),  # LongArray Value
                             (),  # ShortArray Value
                             1,  # MbboUninitTest Value
                             1,  # MbboUninit Value
                             (),  # FloatArray Value
                             0),  # BoUninit Value
                             (4, 6, 6, 0, 0, 5, 0, 0, 5, 1, 5, 5, 2, 0),  # DBR type
                             (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),  # isConnected
                             (631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000),  # SecondsPastEpoch
                             (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  # NanoSeconds
                             (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  # UserTag
                             (3, 0, 3, 3, 0, 0, 0, 3, 3, 3, 0, 0, 3, 3),  # Severity
                             (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),  # Status
                             ('UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM'))  # Message
        self.assertSequenceEqual(result, expected_result)

    def testMultiGroup(self):
        # DB SETUP
        __sqlitedb__ = os.environ["MASAR_SQLITE_DB"]
        try:
            conn = sqlite3.connect(__sqlitedb__)
            pvgname1 = 'masarpvgroup1'
            pvgdesc1 = 'this is my new pv group for masar service with same group name'
            pvs1 = ["masarExample0000",
                    "masarExample0001",
                    "masarExampleBoUninit",
                    "masarExampleMbboUninit",
                    "masarExample0002",
                    "masarExample0003",
                    "masarExampleFloatArray",
                    "masarExample0004"]
            res1 = savePvGroup(conn, pvgname1, func=pvgdesc1)
            res1 = saveGroupPvs(conn, pvgname1, pvs1)
            pvgname2 = 'masarpvgroup2'
            pvgdesc2 = 'this is my new pv group for masar service with same group name'
            pvs2 = ["masarExample0000",
                    "masarExample0001",
                    "masarExample0002",
                    "masarExample0004",
                    "masarExampleCharArray",
                    "masarExampleShortArray",
                    "masarExampleLongArray",
                    "masarExampleStringArray",
                    "masarExampleFloatArray",
                    "masarExampleDoubleArray",
                    "masarExampleMbboUninitTest"]
            res2 = savePvGroup(conn, pvgname2, func=pvgdesc2)
            res2 = saveGroupPvs(conn, pvgname2, pvs2)
            pvgroups = retrievePvGroups(conn)
            self.assertEqual(pvgroups[0][1], "masarpvgroup")
            self.assertEqual(pvgroups[1][1], "masarpvgroup1")
            self.assertEqual(pvgroups[2][1], "masarpvgroup2")
            pvgroups = retrieveGroupPvs(conn, 2)
            self.assertEqual(pvgroups[0][0], "masarExample0000")
            self.assertEqual(pvgroups[1][0], "masarExample0001")
            self.assertEqual(pvgroups[2][0], "masarExampleBoUninit")
            self.assertEqual(pvgroups[3][0], "masarExampleMbboUninit")
            self.assertEqual(pvgroups[4][0], "masarExample0002")
            self.assertEqual(pvgroups[5][0], "masarExample0003")
            self.assertEqual(pvgroups[6][0], "masarExample0004")
            self.assertEqual(pvgroups[7][0], "masarExampleFloatArray")
            pvgroups = retrieveGroupPvs(conn, 3)
            self.assertEqual(pvgroups[0][0], "masarExample0000")
            self.assertEqual(pvgroups[1][0], "masarExample0001")
            self.assertEqual(pvgroups[2][0], "masarExample0002")
            self.assertEqual(pvgroups[3][0], "masarExample0004")
            self.assertEqual(pvgroups[4][0], "masarExampleCharArray")
            self.assertEqual(pvgroups[5][0], "masarExampleShortArray")
            self.assertEqual(pvgroups[6][0], "masarExampleLongArray")
            self.assertEqual(pvgroups[7][0], "masarExampleStringArray")
            self.assertEqual(pvgroups[8][0], "masarExampleFloatArray")
            self.assertEqual(pvgroups[9][0], "masarExampleDoubleArray")
            self.assertEqual(pvgroups[10][0], "masarExampleMbboUninitTest")
            servicename = "masar"
            masarconf = "testconf"
            saveService(conn, servicename, desc='test desc')
            saveServiceConfig(conn, servicename, masarconf, system='SR', status='active',
                              configversion=20140420, configdesc='test desc')

            res = saveServicePvGroup(conn, masarconf, [pvgname1, pvgname2])
            conn.commit()
            conn.close()
        except:
            raise
        save_params = {'configname': 'testconf',
                       'servicename': 'masar'}
        res1 = self.mc.saveSnapshot(save_params)
        self.assertNotEqual(res1, None)
        self.assertNotEqual(res1, False)
        event_id = res1[0]
        retrieve_params = {'eventid': str(event_id)}
        result = self.mc.retrieveSnapshot(retrieve_params)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)

        expected_results = (('masarExample0000',  # ChannelName 0
                            'masarExample0001',  # ChannelName 1
                            'masarExampleBoUninit',  # ChannelName 2
                            'masarExampleMbboUninit',  # ChannelName 3
                            'masarExample0002',  # ChannelName 4
                            'masarExample0003',  # ChannelName 5
                            'masarExample0004',  # ChannelName 6
                            'masarExampleCharArray',  # ChannelName 7
                            'masarExampleShortArray',  # ChannelName 8
                            'masarExampleLongArray',  # ChannelName 9
                            'masarExampleStringArray',  # ChannelName 10
                            'masarExampleFloatArray',  # ChannelName 11
                            'masarExampleDoubleArray',  # ChannelName 12
                            'masarExampleMbboUninitTest'),  # ChannelName 13
                            (10,  # 0000 Value
                            'string value',  # 0001 Value
                            '0',  # BoUninit Value (appropriately returned as string,
                            1,  # MbboUninit Value
                            'zero',  # 0002 Value
                            'one',  # 0003 Value
                            1.9,  # 0004 Value
                            (),  # CharArray Value
                            (),  # ShortArray Value
                            (),  # LongArray Value
                            (),  # StringArray Value
                            (),  # FloatArrayValue
                            (),  # DoubleArray Value
                            1),  # MbboUninitTest Value
                            (5, 0, 0, 5, 0, 0, 6, 4, 1, 5, 0, 2, 6, 5),  # DBR type
                            (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),  # isConnected
                            (631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000,
                            631152000, 631152000, 631152000, 631152000),  # SecondsPastEpoch
                            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  # NanoSeconds
                            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  # UserTag
                            (0, 0, 3, 0, 3, 0, 0, 3, 3, 3, 3, 3, 3, 0),  # Severity
                            (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),  # Status
                            ('UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM',
                             'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM'))  # Message
        self.assertSequenceEqual(result, expected_results)

    if __name__ == '__main__':
        unittest.main()
