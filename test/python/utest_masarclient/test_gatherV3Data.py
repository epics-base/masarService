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
        self.names = (
            'masarExampleBoUninit',
            'masarExampleMbboUninit',
            'masarExample0002',
            'masarExample0003',
            'masarExample0000',
            'masarExample0001',
            'masarExample0004',
            'masarExampleCharArray',
            'masarExampleUCharArray',
            'masarExampleStringArray',
            'masarExampleShortArray',
            'masarExampleLongArray',
            'masarExampleFloatArray',
            'masarExampleDoubleArray',
        )
        self.gatherv3data = GatherV3Data(self.names)
        self.gatherv3data.connect(2.0)

    '''
    Attempts gatherV3Data client disconnect
    '''
    def tearDown(self):
        self.gatherv3data.__del__()

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
        self.assertTrue(pvstructure is not None, "No PVStructure returned")

    '''
    Tests all values in NTMultiChannel. Condensed test to reduce connection overhead of multiple tests.

    Note: These tests only confirm that the correct number of each thing are returned,
          but it would be simple to add tests for types, or specific values or ranges
    '''
    def testNTMultiChannel(self):
        result = self.gatherv3data.get()
        self.assertTrue(result, "Connection failed with message:  " + self.gatherv3data.getMessage())
        pvstructure = self.gatherv3data.getPVStructure()
        ntmultichannel = NTMultiChannel(pvstructure)

        alarm = Alarm()
        ntmultichannel.getAlarm(alarm)
        self.assertTrue(alarm.getStatus() in alarm.getStatusChoices(), "Invalid alarm status detected")
        self.assertTrue(alarm.getSeverity() in alarm.getSeverityChoices(), "Invalid alarm severity detected")

        time_stamp = TimeStamp()
        test_stamp = TimeStamp()
        ntmultichannel.getTimeStamp(time_stamp)
        self.assertGreaterEqual(time_stamp._diffInt(test_stamp), 0, "Unexpected time stamp value, "
                                                                    "given time stamp is earlier than default time")
        test_stamp.getCurrent()
        self.assertLessEqual(time_stamp._diffInt(test_stamp), 0, "Unexpected time stamp value, "
                                                                 "given time stamp is in the future")

        channel_count = ntmultichannel.getNumberChannel()
        self.assertTrue(channel_count > 0, "Channel count of %r returned" % channel_count)
        self.assertEqual(len(ntmultichannel.getValue()), channel_count,
                         "Channel count does not match number of values")
        self.assertEqual(len(ntmultichannel.getChannelName()), channel_count,
                         "Channel count does not match number of channel names")
        self.assertEqual(len(ntmultichannel.getIsConnected()), channel_count,
                         "Channel count does not match number of monitered connections")
        self.assertEqual(len(ntmultichannel.getSeverity()), channel_count,
                         "Channel count does not match number of severities")
        self.assertEqual(len(ntmultichannel.getStatus()), channel_count,
                         "Channel count does not match number of statuses")
        self.assertEqual(len(ntmultichannel.getMessage()), channel_count,
                         "Channel count does not match number of messages")
        self.assertEqual(len(ntmultichannel.getDbrType()), channel_count,
                         "Channel count does not match number of dbr types")
        self.assertEqual(len(ntmultichannel.getSecondsPastEpoch()), channel_count,
                         "Channel count does not match number of times (seconds)")
        self.assertEqual(len(ntmultichannel.getNanoseconds()), channel_count,
                         "Channel count does not match number of times (nanoseconds)")
        self.assertEqual(len(ntmultichannel.getUserTag()), channel_count,
                         "Channel count does not match number of user tags")
        self.assertEqual(type(ntmultichannel.getDescriptor()), StringType, "Non-String descriptor found:  %r" % ntmultichannel.getDescriptor() + " is of type %r" % type(ntmultichannel.getDescriptor()))

    if __name__ == '__main__':
        unittest.main()
