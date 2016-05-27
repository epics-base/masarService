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

    '''
    Tests the connection to see that it was established and allows data to be accessed
    '''
    def testConnection(self):
        gatherv3data = GatherV3Data(self.names)
        gatherv3data.connect(2.0)
        result = gatherv3data.get()
        self.assertTrue(result, "Connection failed with message:  "+gatherv3data.getMessage())

    def testGetPVStructure(self):
        gatherv3data = GatherV3Data(self.names)
        gatherv3data.connect(2.0)
        gatherv3data.get()
        pvstructure = gatherv3data.getPVStructure()
        self.assertTrue(pvstructure is not None, "No PVStructure returned")

    '''
    Tests all values in NTMultiChannel. Condensed test to reduce connection overhead of multiple tests.

    Note: These tests only confirm that the correct number of each thing are returned,
          but it would be simple to add tests for types, or specific values or ranges
    '''
    def testNTMultiChannel(self):
        gatherv3data = GatherV3Data(self.names)
        gatherv3data.connect(2.0)
        gatherv3data.get()
        pvstructure = gatherv3data.getPVStructure()
        ntmultichannel = NTMultiChannel(pvstructure)

        alarm = Alarm()
        ntmultichannel.getAlarm(alarm)
        self.assertTrue(alarm.getStatus() in alarm.getStatusChoices(), "Invalid alarm status detected")
        self.assertTrue(alarm.getSeverity() in alarm.getSeverityChoices(), "Invalid alarm severity detected")

        time_stamp = TimeStamp()
        test_stamp = TimeStamp()
        ntmultichannel.getTimeStamp(time_stamp)
        self.assertTrue(time_stamp._diffInt(test_stamp) >= 0, "Unexpected time stamp value, "
                                                              "given time stamp is earlier than default time")
        test_stamp.getCurrent()
        self.assertTrue(time_stamp._diffInt(test_stamp) <= 0, "Unexpected time stamp value, "
                                                              "given time stamp is in the future")

        channel_count = ntmultichannel.getNumberChannel()
        self.assertTrue(channel_count > 0, "Channel count of %r returned" % channel_count)
        self.assertTrue(len(ntmultichannel.getValue()) == channel_count,
                        "Channel count does not match number of values")
        self.assertTrue(len(ntmultichannel.getChannelName()) == channel_count,
                        "Channel count does not match number of channel names")
        self.assertTrue(len(ntmultichannel.getIsConnected()) == channel_count,
                        "Channel count does not match number of monitered connections")
        self.assertTrue(len(ntmultichannel.getSeverity()) == channel_count,
                        "Channel count does not match number of severities")
        self.assertTrue(len(ntmultichannel.getStatus()) == channel_count,
                        "Channel count does not match number of statuses")
        self.assertTrue(len(ntmultichannel.getMessage()) == channel_count,
                        "Channel count does not match number of messages")
        self.assertTrue(len(ntmultichannel.getDbrType()) == channel_count,
                        "Channel count does not match number of dbr types")
        self.assertTrue(len(ntmultichannel.getSecondsPastEpoch()) == channel_count,
                        "Channel count does not match number of times (seconds)")
        self.assertTrue(len(ntmultichannel.getNanoseconds()) == channel_count,
                        "Channel count does not match number of times (nanoseconds)")
        self.assertTrue(len(ntmultichannel.getUserTag()) == channel_count,
                        "Channel count does not match number of user tags")

        assert type(ntmultichannel.getDescriptor()) is StringType, "Non-String descriptor found"

    if __name__ == '__main__':
        unittest.main()
