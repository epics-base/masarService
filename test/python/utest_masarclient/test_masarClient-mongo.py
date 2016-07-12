import sys
import unittest

from masarclient import masarClient
from masarclient.channelRPC import epicsExit
from pymasarmongo.db import utils
from pymasarmongo.config._config import masarconfig

from pymasarmongo.pymasarmongo.pymasar import saveconfig
from pymasarmongo.pymasarmongo.pymasar import retrieveconfig
from pymasarmongo.pymasarmongo.pymasar import updateconfig
from pymasarmongo.pymasarmongo.pymasar import saveevent
from pymasarmongo.pymasarmongo.pymasar import retrieveevents
from pymasarmongo.pymasarmongo.pymasar import updateevent
from pymasarmongo.pymasarmongo.pymasar import retrievesnapshot

'''

Unittests for masarService/python/masarclient/masarClient.py

'''


class TestMasarClient(unittest.TestCase):

    def setUp(self):
        channel = 'masarService'
        self.mc = masarClient.client(channelname=channel)
        # DB SETUP
        self.conn, collection = utils.conn(host=masarconfig.get('mongodb', 'host'), port=masarconfig.get('mongodb', 'port'),
                                      db=masarconfig.get('mongodb', 'database'))

        self.conn.drop_database(masarconfig.get('mongodb', 'database'))
        name = "SR_All_20140421"
        params = {"desc": "SR daily SCR setpoint without IS kick and septum: SR and RF",
                  "system": "SR",
                  "status": "active",
                  "version": 20140421,
                  }
        newid = saveconfig(self.conn, collection, name, **params)
        #res0 = retrieveconfig(self.conn, collection, name)
        pvs = ["masarExample0000",
               "masarExample0001",
               #"masarExampleBoUninit",
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
        #res3 = retrieveconfig(self.conn, collection, name, withpvs=True)

    def tearDown(self):
        self.conn.drop_database(masarconfig.get('mongodb', 'database'))
        utils.close(self.conn)

    def testRetrieveSystemList(self):
        result = self.mc.retrieveSystemList()
        self.assertNotEqual(result, None)  # Can not be assertTrue because there is no case where it returns True
        self.assertNotEqual(result, False)  # Instead asserting both not None and not False
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
        print "retrieveServiceEvents"
        params = {'configid': '1'}
        result = self.mc.retrieveServiceEvents(params)
        print "result2 " +str(result)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)

    def testSaveSnapshot(self):
        params = {"configname": "SR_All_20140421",
                  "system": "SR"}
        result = self.mc.saveSnapshot(params)
        self.assertNotEqual(result, None)
        self.assertNotEqual(result, False)
        # The following tests are for expected outputs
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], ('masarExample0000', 'masarExample0001', 'masarExampleMbboUninit', 'masarExample0002', 'masarExample0003', 'masarExample0004', 'masarExampleCharArray', 'masarExampleShortArray', 'masarExampleLongArray', 'masarExampleStringArray', 'masarExampleFloatArray', 'masarExampleDoubleArray', 'masarExampleMbboUninitTest'))  # ChannelName
        self.assertEqual(result[2], (10, 'string value', 1, 'zero', 'one', 1.9, (), (), (), (), (), (), 1))  # Value
        self.assertEqual(result[3], (5, 0, 5, 0, 0, 6, 4, 1, 5, 0, 2, 6, 5))  # DBR type
        self.assertEqual(result[4], (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1))  # isConnected
        self.assertEqual(result[5], (
        631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000,
        631152000, 631152000, 631152000, 631152000))  # SecondsPastEpoch
        self.assertEqual(result[6], (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))  # NanoSeconds
        self.assertEqual(result[7], (0, 0, 0, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0))  # UserTag
        self.assertEqual(result[8], (0, 0, 0, 3, 0, 0, 3, 3, 3, 3, 3, 3, 0))  # Severity
        self.assertEqual(result[9], (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3))  # Status
        self.assertEqual(result[10], (
        'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM',
        'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM'))  # Message

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
        self.assertEqual(result[0], (
        'masarExample0000', 'masarExample0001', 'masarExampleMbboUninit', 'masarExample0002', 'masarExample0003',
        'masarExample0004', 'masarExampleCharArray', 'masarExampleShortArray', 'masarExampleLongArray',
        'masarExampleStringArray', 'masarExampleFloatArray', 'masarExampleDoubleArray',
        'masarExampleMbboUninitTest'))  # ChannelName
        self.assertEqual(result[1], (10, 'string value', 1, 'zero', 'one', 1.9, (), (), (), (), (), (), 1))  # Value
        self.assertEqual(result[2], (5, 0, 5, 0, 0, 6, 4, 1, 5, 0, 2, 6, 5))  # DBR type
        self.assertEqual(result[3], (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1))  # isConnected
        self.assertEqual(result[4], (
            631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000,
            631152000, 631152000, 631152000, 631152000))  # SecondsPastEpoch
        self.assertEqual(result[5], (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))  # NanoSeconds
        self.assertEqual(result[6], (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))  # UserTag
        self.assertEqual(result[7], (0, 0, 0, 3, 0, 0, 3, 3, 3, 3, 3, 3, 0))  # Severity
        self.assertEqual(result[8], (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3))  # Status
        self.assertEqual(result[9], (
            'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM',
            'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM'))  # Message

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
        self.assertEqual(result[0], (
        'masarExampleCharArray', 'masarExample0004', 'masarExampleDoubleArray', 'masarExample0002', 'masarExample0003',
        'masarExample0000', 'masarExample0001', 'masarExampleStringArray', 'masarExampleLongArray',
        'masarExampleShortArray', 'masarExampleMbboUninitTest', 'masarExampleMbboUninit', 'masarExampleFloatArray',
        'masarExampleBoUninit'))  # ChannelName
        self.assertEqual(result[1], ((), 1.9, (), 'zero', 'one', 10, 'string value', (), (), (), 1, 1, (), 0))  # Value
        self.assertEqual(result[2], (4, 6, 6, 0, 0, 5, 0, 0, 5, 1, 5, 5, 2, 0))  # DBR type
        self.assertEqual(result[3], (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1))  # isConnected
        self.assertEqual(result[4], (
        631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000,
        631152000, 631152000, 631152000, 631152000))  # SecondsPastEpoch
        self.assertEqual(result[5], (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))  # NanoSeconds
        self.assertEqual(result[6], (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))  # UserTag
        self.assertEqual(result[7], (3, 0, 3, 3, 0, 0, 0, 3, 3, 3, 0, 0, 3, 3))  # Severity
        self.assertEqual(result[8], (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3))  # Status
        self.assertEqual(result[9], (
        'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM',
        'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM'))  # Message

    if __name__ == '__main__':
        unittest.main()
