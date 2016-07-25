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

    '''
    Attempts gatherV3Data client disconnect
    '''
    def tearDown(self):
        self.gatherv3data = None

    '''
    Tests the connection to see that it was established and allows data to be accessed
    '''
    def testConnection(self):
        self.assertTrue(self.connected, "Failed to connect to any channel")
        result = self.gatherv3data.get()
        self.assertTrue(result, "Connection failed with message:  " + self.gatherv3data.getMessage())

    def testGetPVStructure(self):
        self.assertTrue(self.connected, "Failed to connect to any channel")
        result = self.gatherv3data.get()
        self.assertTrue(result, "Connection failed with message:  " + self.gatherv3data.getMessage())

        pvstructure = self.gatherv3data.getPVStructure()
        self.assertNotEqual(pvstructure, None, "No PVStructure returned")

    '''
    Tests all values in NTMultiChannel. Condensed test to reduce connection overhead of multiple tests.

    Note: These tests check for specific values that are present in the masarTestDB.db and will fail if that DB is not loaded
    '''
    def testNTMultiChannel(self):
        self.assertTrue(self.connected, "Failed to connect to any channel")
        result = self.gatherv3data.get()
        self.assertTrue(result, "Connection failed with message:  " + self.gatherv3data.getMessage())
        pvstructure = self.gatherv3data.getPVStructure()
        ntmultichannel = NTMultiChannel(pvstructure)

        alarm = Alarm()
        ntmultichannel.getAlarm(alarm)
        self.assertTrue(alarm.getStatus() in alarm.getStatusChoices(),
                        "Invalid alarm status detected, status " + str(alarm.getStatus()) +
                        " not found in choices " + str(alarm.getStatusChoices()))
        self.assertTrue(alarm.getSeverity() in alarm.getSeverityChoices(),
                        "Invalid alarm severity detected, severity " + str(alarm.getSeverity()) +
                        " not found in choices " + str(alarm.getSeverityChoices()))

        time_stamp = TimeStamp()
        test_stamp = TimeStamp()
        ntmultichannel.getTimeStamp(time_stamp)
        self.assertGreaterEqual(time_stamp._diffInt(test_stamp), 0, "Unexpected time stamp value, "
                                                                    "given time stamp is earlier than default time")
        test_stamp.getCurrent()
        self.assertLessEqual(time_stamp._diffInt(test_stamp), 0, "Unexpected time stamp value, "
                                                                 "given time stamp is in the future")

        channel_count = ntmultichannel.getNumberChannel()

        self.assertEqual(channel_count, 13, "Channel count of %r returned, expected 13" % channel_count)
        test_val_list = (0, 1, 'zero', 'one', 10, 'string value', 1.9, (), (), (), (), (), ())

        self.assertEqual(ntmultichannel.getValue(), test_val_list,
                         "es do not match known test DB, received:  " + str(ntmultichannel.getValue()) +
                         "  EXPECTED: " + str(test_val_list))

        self.assertEqual(ntmultichannel.getChannelName(), self.names,
                         "Names do not match known test DB, received:  " + str(ntmultichannel.getChannelName()) +
                         "  EXPECTED: " + str(self.names))

        test_connected_list = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
        self.assertEqual(ntmultichannel.getIsConnected(), test_connected_list,
                         "es do not match known test DB, received:  " + str(ntmultichannel.getIsConnected()) +
                         "  EXPECTED: " + str(test_connected_list))

        test_severity_list = (3, 0, 3, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3)
        self.assertEqual(ntmultichannel.getSeverity(), test_severity_list,
                         "es do not match known test DB, received:  " + str(ntmultichannel.getSeverity()) +
                         "  EXPECTED: " + str(test_severity_list))

        test_status_list = (3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3)
        self.assertEqual(ntmultichannel.getStatus(), test_status_list,
                         "es do not match known test DB, received:  " + str(ntmultichannel.getStatus()) +
                         "  EXPECTED: " + str(test_status_list))

        test_message_list = ('UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM', 'UDF_ALARM')
        self.assertEqual(ntmultichannel.getMessage(), test_message_list,
                         "es do not match known test DB, received:  " + str(ntmultichannel.getMessage()) +
                         "  EXPECTED: " + str(test_message_list))

        test_dbrtype_list = (0, 5, 0, 0, 5, 0, 6, 4, 0, 1, 5, 2, 6)
        self.assertEqual(ntmultichannel.getDbrType(), test_dbrtype_list,
                         "es do not match known test DB, received:  " + str(ntmultichannel.getDbrType()) +
                         "  EXPECTED: " + str(test_dbrtype_list))

        test_secondspastepoch_list = (631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000, 631152000)
        self.assertEqual(ntmultichannel.getSecondsPastEpoch(), test_secondspastepoch_list,
                         "es do not match known test DB, received:  " + str(ntmultichannel.getSecondsPastEpoch()) +
                         "  EXPECTED: " + str(test_secondspastepoch_list))

        test_nanoseconds_list = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.assertEqual(ntmultichannel.getNanoseconds(), test_nanoseconds_list,
                         "es do not match known test DB, received:  " + str(ntmultichannel.getNanoseconds()) +
                         "  EXPECTED: " + str(test_nanoseconds_list))

        test_usertag_list = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.assertEqual(ntmultichannel.getUserTag(), test_usertag_list,
                         "es do not match known test DB, received:  " + str(ntmultichannel.getUserTag()) +
                         "  EXPECTED: " + str(test_usertag_list))

        self.assertEqual(type(ntmultichannel.getDescriptor()), StringType, "Non-String descriptor found:  " + str(ntmultichannel.getDescriptor()) + " is of type " + str(type(ntmultichannel.getDescriptor())))

    if __name__ == '__main__':
        unittest.main()
