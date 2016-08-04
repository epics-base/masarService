import sys
import unittest

from masarclient import masarClient
from pymasarmongo.db import utils
from pymasarmongo.config._config import masarconfig

from unittest_utils import MONGODB_TEST_SETUP
'''

Unittests for masarService/python/masarclient/masarClient.py

'''


class TestMasarClientMongo(unittest.TestCase):

    def setUp(self):
        channel = 'mongoMasarTestService'
        self.mc = masarClient.client(channelname=channel)
        # DB SETUP
        self.conn = MONGODB_TEST_SETUP(self)


    def tearDown(self):
        self.conn.drop_database(masarconfig.get('mongodb', 'database'))
        utils.close(self.conn)

    def testRetrieveSystemList(self):
        result = self.mc.retrieveSystemList()
        self.assertIsInstance(result, (list, tuple))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 'SR')  # Expected Output

    def testRetrieveServiceConfigs(self):
        params = {'system': 'SR'}
        result = self.mc.retrieveServiceConfigs(params)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)
        self.assertEqual(len(result), 6)
        # Expected Output
        self.assertEqual(result[0], (1,))
        self.assertEqual(result[1], ('SR_All_20140421',))
        self.assertEqual(result[2], ('SR daily SCR setpoint without IS kick and septum: SR and RF',))
        self.assertNotEqual(result[3], ('',))  # Can't hardcode time comparison
        self.assertEqual(result[4], ('',))
        self.assertEqual(result[5], ('active',))

    def testRetrieveServiceEvents(self):
        params = {'configid': '1'}
        result = self.mc.retrieveServiceEvents(params)
        self.assertIsInstance(result, (list, tuple))

    def testSaveSnapshot(self):
        params = {"configname": "SR_All_20140421",
                  "system": "SR"}
        result = self.mc.saveSnapshot(params)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)
        # The following tests are for expected outputs
        expected_result = (1,
            ('masarExample0000', 'masarExample0001', 'masarExampleMbboUninit', 'masarExample0002',
             'masarExample0003', 'masarExample0004', 'masarExampleCharArray', 'masarExampleShortArray',
             'masarExampleLongArray', 'masarExampleStringArray', 'masarExampleFloatArray',
             'masarExampleDoubleArray', 'masarExampleMbboUninitTest'),
            (10, 'string value', 1, 'zero', 'one', 1.9, (), (), (), (), (), (), 1),
            (5, 0, 5, 0, 0, 6, 4, 1, 5, 0, 2, 6, 5),
            (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
            (631152000, 631152000, 631152000, 631152000, 631152000,
             631152000, 631152000, 631152000, 631152000,
            631152000, 631152000, 631152000, 631152000),
            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0),
            (0, 0, 0, 3, 0, 0, 3, 3, 3, 3, 3, 3, 0),
            (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
            ('UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM',
             'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM',
             'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM'))
        self.assertSequenceEqual(result, expected_result)

    def testRetrieveSnapshot(self):
        save_params = {"configname": "SR_All_20140421",
                  "system": "SR"}
        res1 = self.mc.saveSnapshot(save_params)
        self.assertNotEqual(res1, None)
        self.assertNotEqual(res1, False)
        event_id = res1[0]
        retrieve_params = {'eventid': str(event_id)}
        result = self.mc.retrieveSnapshot(retrieve_params)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)
        # The following tests are for expected outputs
        expected_result = (('masarExample0000', 'masarExample0001', 'masarExampleMbboUninit', 'masarExample0002',
                            'masarExample0003', 'masarExample0004', 'masarExampleCharArray', 'masarExampleShortArray',
                            'masarExampleLongArray', 'masarExampleStringArray', 'masarExampleFloatArray',
                            'masarExampleDoubleArray', 'masarExampleMbboUninitTest'),
                           (10, 'string value', 1, 'zero', 'one', 1.9, (), (), (), (), (), (), 1),
                           (5, 0, 5, 0, 0, 6, 4, 1, 5, 0, 2, 6, 5),
                           (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
                           (631152000, 631152000, 631152000, 631152000, 631152000,
                            631152000, 631152000, 631152000, 631152000,
                            631152000, 631152000, 631152000, 631152000),
                           (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
                           (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
                           (0, 0, 0, 3, 0, 0, 3, 3, 3, 3, 3, 3, 0),
                           (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
                           ('UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM',
                            'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM',
                            'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM'))
        self.assertSequenceEqual(expected_result, result)

    def testUpdateSnapshotEvent(self):
        save_params = {"configname": "SR_All_20140421",
                  "system": "SR"}

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
        self.assertEqual(result, True)  # Expected output, may wish to RetrieveSnapshot and confirm changes

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
        expected_result = (('masarExampleCharArray', 'masarExample0004', 'masarExampleDoubleArray', 'masarExample0002', 'masarExample0003',
                            'masarExample0000', 'masarExample0001', 'masarExampleStringArray', 'masarExampleLongArray',
                            'masarExampleShortArray', 'masarExampleMbboUninitTest', 'masarExampleMbboUninit', 'masarExampleFloatArray',
                            'masarExampleBoUninit'),  # ChannelName
                            ((), 1.9, (), 'zero', 'one', 10, 'string value', (), (), (), 1, 1, (), 0),  # Value
                            (4, 6, 6, 0, 0, 5, 0, 0, 5, 1, 5, 5, 2, 0),  # DBR type
                            (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),  # isConnected
                            (631152000, 631152000, 631152000, 631152000, 631152000,
                             631152000, 631152000, 631152000, 631152000, 631152000,
                            631152000, 631152000, 631152000, 631152000),  # SecondsPastEpoch
                            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  # NanoSeconds
                            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  # UserTag
                            (3, 0, 3, 3, 0, 0, 0, 3, 3, 3, 0, 0, 3, 3),  # Severity
                            (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3),  # Status
                            ('UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM',
                             'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM'))  # Message
        self.assertSequenceEqual(expected_result, result)

    if __name__ == '__main__':
        unittest.main()
