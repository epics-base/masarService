import unittest
from types import *

from masarclient.gatherV3Data import GatherV3Data as GatherV3Data
from masarclient.ntmultiChannel import NTMultiChannel as NTMultiChannel
from masarclient.alarm import Alarm as Alarm
from masarclient.timeStamp import TimeStamp as TimeStamp


'''

Unittests for masarService/python/masarclient/alarm.py

'''


class TestGatherV3Data(unittest.TestCase):

    '''
    These names are meant to be used with the test database in its present state and may need to be changed.
    '''
    def setUp(self):
        self.connected = False
        self.names = (
            'masarExampleBoUninit',
            'masarExampleMbboUninit',
            'masarExample0002',
            'masarExample0003',
            'masarExample0000',
            'masarExample0001',
            'masarExample0004',
            'masarExampleCharArray',
            'masarExampleStringArray',
            'masarExampleShortArray',
            'masarExampleLongArray',
            'masarExampleFloatArray',
            'masarExampleDoubleArray',
        )
        self.gatherv3data = GatherV3Data(self.names)
        self.connected = self.gatherv3data.connect(2.0)
        self.assertTrue(self.connected, "Failed to connect to any channel")

    '''
    Attempts gatherV3Data client disconnect
    '''
    def tearDown(self):
        pass  # TODO: Disconnect gatherV3Data

    '''
    Tests the connection to see that it was established and allows data to be accessed
    '''
    def testConnection(self):
        result = self.gatherv3data.get()
        self.assertTrue(result, "Connection failed with message:  " + self.gatherv3data.getMessage())

    def testGetPVStructure(self):
        result = self.gatherv3data.get()
        self.assertTrue(result, "Connection failed with message:  " + self.gatherv3data.getMessage())

        pvstructure = self.gatherv3data.getPVStructure()
        self.assertNotEqual(pvstructure, None, "No PVStructure returned")

    '''
    Tests all values in NTMultiChannel. Condensed test to reduce connection overhead of multiple tests.

    Note: These tests check for specific values that are present in the masarTestDB.db and will fail if that DB is not loaded
    '''
    def testNTMultiChannel(self):
        result = self.gatherv3data.get()
        self.assertTrue(result, "Connection failed with message:  " + self.gatherv3data.getMessage())
        pvstructure = self.gatherv3data.getPVStructure()
        ntmultichannel = NTMultiChannel(pvstructure)

        alarm = Alarm()
        ntmultichannel.getAlarm(alarm)
        self.assertIn(alarm.getStatus(), alarm.getStatusChoices())
        self.assertIn(alarm.getSeverity(), alarm.getSeverityChoices())

        time_stamp = TimeStamp()
        ntmultichannel.getTimeStamp(time_stamp)
        self.assertEqual(3, len(str(time_stamp).split(':')))  # Time stamp format test

        channel_count = ntmultichannel.getNumberChannel()

        self.assertEqual(channel_count, len(self.names))

        test_val_list = (0, 1, 'zero', 'one', 10, 'string value', 1.9, (), (), (), (), (), ())
        self.assertEqual(ntmultichannel.getValue(), test_val_list)

        self.assertEqual(ntmultichannel.getChannelName(), self.names)

        test_connected_list = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
        self.assertEqual(ntmultichannel.getIsConnected(), test_connected_list)

        test_severity_list = (3, 0, 3, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3)
        self.assertEqual(ntmultichannel.getSeverity(), test_severity_list)

        test_status_list = (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3)
        self.assertEqual(ntmultichannel.getStatus(), test_status_list)

        test_message_list = ('UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM')
        self.assertEqual(ntmultichannel.getMessage(), test_message_list)

        test_dbrtype_list = (0, 5, 0, 0, 5, 0, 6, 4, 0, 1, 5, 2, 6)
        self.assertEqual(ntmultichannel.getDbrType(), test_dbrtype_list)

        test_secondspastepoch_list = (631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000)
        self.assertEqual(ntmultichannel.getSecondsPastEpoch(), test_secondspastepoch_list)

        test_nanoseconds_list = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.assertEqual(ntmultichannel.getNanoseconds(), test_nanoseconds_list)

        test_usertag_list = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.assertEqual(ntmultichannel.getUserTag(), test_usertag_list)

        self.assertEqual(type(ntmultichannel.getDescriptor()), StringType)

    if __name__ == '__main__':
        unittest.main()
