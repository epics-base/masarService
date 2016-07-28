import unittest

from masarclient.channelRPC import ChannelRPC as ChannelRPC
from masarclient.ntnameValue import NTNameValue
from masarclient.ntmultiChannel import NTMultiChannel
from masarclient.nttable import NTTable
from masarclient.alarm import Alarm
from masarclient.timeStamp import TimeStamp

'''

Unittests for masarService/python/masarclient/channelRPC.py

'''


class TestChannelRPC(unittest.TestCase):

    '''
    Tests initial connection to channelRPC and establishes connections for each test
    '''
    def setUp(self):
        self.channelRPC = ChannelRPC("sqliteMasarTestService")
        self.channelRPC.issueConnect()
        if not self.channelRPC.waitConnect(2.0):
            print "error when waiting connection.", self.channelRPC.getMessage()
            # AttributeError: 'module' object has no attribute '_getMessage'
            raise AttributeError()

    '''
    Tests retrieveSnapshot function, makes assertion for successful request and for correct results
    '''
    def testRetrieveSnapshot(self):
        function = "retrieveSnapshot"
        params = {'eventid': '365'}
        self.ntnv_asserts(function,params)

    '''
    Tests saveSnapshot function, makes assertion for successful request and for correct results
    '''
    def testSaveSnapshot(self):
        function = "saveSnapshot"
        params = {'configname': 'wf_test',
                  'servicename': 'masar'}
        self.ntnv_asserts(function, params)

    def ntnv_asserts(self, function, params):

        alarm = Alarm()
        time_stamp = TimeStamp()
        ntnv = NTNameValue(function, params)
        self.channelRPC.issueRequest(ntnv.getNTNameValue(), False)
        response = self.channelRPC.waitResponse()
        self.assertNotEqual(response, None, "ChannelRPC connection failure.")
        result = NTMultiChannel(response)
        result.getAlarm(alarm)
        result.getTimeStamp(time_stamp)
        self.assertEqual(3, len(str(time_stamp).split(":")))  # Timestamp string format test

        self.assertIn(alarm.getStatus(), alarm.getStatusChoices())
        self.assertIn(alarm.getSeverity(), alarm.getSeverityChoices())

    '''
    Tests retrieveServiceEvents function, makes assertion for successful request and for correct results
    '''
    def testRetrieveServiceEvents(self):
        function = "retrieveServiceEvents"
        params = {'configid': '1'}
        self.nttable_asserts(function, params)

    '''
    Tests retrieveServiceConfigProps function, makes assertion for successful request and for correct results
    '''
    def testRetrieveServiceConfigProps(self):
        function = "retrieveServiceConfigProps"
        params = {'propname': 'system',
                  'configname': 'SR_All_SCR_20140421'}
        self.nttable_asserts(function, params)

    '''
    Tests retrieveServiceConfigs function, makes assertion for successful request and for correct results
    '''
    def testRetrieveServiceConfigs(self):
        function = "retrieveServiceConfigs"
        params = {'system': 'all'}
        self.nttable_asserts(function, params)

    def nttable_asserts(self, function, params):
        alarm = Alarm()
        time_stamp = TimeStamp()
        ntnv = NTNameValue(function, params)
        self.channelRPC.issueRequest(ntnv.getNTNameValue(), False)
        response = self.channelRPC.waitResponse()
        self.assertNotEqual(response, None, "ChannelRPC connection failure.")
        result = NTTable(response)
        label = result.getLabels()
        self.assertNotEqual(label, None, "Labels returned improper value: None")
        result.getAlarm(alarm)
        result.getTimeStamp(time_stamp)
        self.assertEqual(3, len(str(time_stamp).split(":")))  # Timestamp string format test

        self.assertIn(alarm.getStatus(), alarm.getStatusChoices())
        self.assertIn(alarm.getSeverity(), alarm.getSeverityChoices())

    if __name__ == '__main__':
        unittest.main()
