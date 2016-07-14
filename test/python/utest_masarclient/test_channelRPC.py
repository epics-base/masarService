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
            exit(1)

    '''
    Clears connection after each test
    '''
    def tearDown(self):
        self.channelRPC.__del__()

    '''
    Tests retrieveSnapshot function, makes assertion for successful request and for correct results
    '''
    def testRetrieveSnapshot(self):
        function = "retrieveSnapshot"
        params = {'eventid': '365'}
        alarm = Alarm()
        time_stamp = TimeStamp()
        ntnv = NTNameValue(function, params)
        self.channelRPC.issueRequest(ntnv.getNTNameValue(), False)
        response = self.channelRPC.waitResponse()
        self.assertNotEqual(response, None, "ChannelRPC connection failure.")
        result = NTMultiChannel(response)
        result.getAlarm(alarm)
        result.getTimeStamp(time_stamp)
        test_stamp = TimeStamp()
        self.assertGreaterEqual(time_stamp._diffInt(test_stamp), 0, "Unexpected time stamp value, "
                                                                    "given time stamp is earlier than default time")
        test_stamp.getCurrent()
        self.assertLessEqual(time_stamp._diffInt(test_stamp), 0, "Unexpected time stamp value, "
                                                                 "given time stamp is in the future")

        self.assertTrue(alarm.getStatus() in alarm.getStatusChoices(),
                        "Invalid alarm status, status not in StatusChoices:  " + str(
                            alarm.getStatus()) + " not in " + str(alarm.getStatusChoices()))
        self.assertTrue(alarm.getSeverity() in alarm.getSeverityChoices(),
                        "Invalid alarm severity, severity not in SeverityChoices:  " + str(
                            alarm.getSeverity()) + " not in " + str(alarm.getSeverityChoices()))

    '''
    Tests saveSnapshot function, makes assertion for successful request and for correct results
    '''
    def testSaveSnapshot(self):
        function = "saveSnapshot"
        params = {'configname': 'wf_test',
                  'servicename': 'masar'}
        alarm = Alarm()
        time_stamp = TimeStamp()
        ntnv = NTNameValue(function, params)
        self.channelRPC.issueRequest(ntnv.getNTNameValue(), False)
        response = self.channelRPC.waitResponse()
        self.assertNotEqual(response, None, "ChannelRPC connection failure.")
        result = NTMultiChannel(response)
        result.getAlarm(alarm)
        result.getTimeStamp(time_stamp)
        test_stamp = TimeStamp()
        self.assertGreaterEqual(time_stamp._diffInt(test_stamp), 0, "Unexpected time stamp value, "
                                                                    "given time stamp is earlier than default time")
        test_stamp.getCurrent()
        self.assertLessEqual(time_stamp._diffInt(test_stamp), 0, "Unexpected time stamp value, "
                                                                 "given time stamp is in the future")

        self.assertTrue(alarm.getStatus() in alarm.getStatusChoices(),
                        "Invalid alarm status, status not in StatusChoices:  " + str(
                            alarm.getStatus()) + " not in " + str(alarm.getStatusChoices()))
        self.assertTrue(alarm.getSeverity() in alarm.getSeverityChoices(),
                        "Invalid alarm severity, severity not in SeverityChoices:  " + str(
                            alarm.getSeverity()) + " not in " + str(alarm.getSeverityChoices()))

    '''
    Tests retrieveServiceEvents function, makes assertion for successful request and for correct results
    '''
    def testRetrieveServiceEvents(self):
        function = "retrieveServiceEvents"
        params = {'configid': '1'}
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
        test_stamp = TimeStamp()
        self.assertGreaterEqual(time_stamp._diffInt(test_stamp), 0, "Unexpected time stamp value, "
                                                                    "given time stamp is earlier than default time")

        test_stamp.getCurrent()
        self.assertLessEqual(time_stamp._diffInt(test_stamp), 0, "Unexpected time stamp value, "
                                                             "given time stamp is in the future")

        self.assertTrue(alarm.getStatus() in alarm.getStatusChoices(),
                        "Invalid alarm status, status not in StatusChoices:  " + str(
                            alarm.getStatus()) + " not in " + str(alarm.getStatusChoices()))
        self.assertTrue(alarm.getSeverity() in alarm.getSeverityChoices(),
                        "Invalid alarm severity, severity not in SeverityChoices:  " + str(
                            alarm.getSeverity()) + " not in " + str(alarm.getSeverityChoices()))

    '''
    Tests retrieveServiceConfigProps function, makes assertion for successful request and for correct results
    '''
    def testRetrieveServiceConfigProps(self):
        function = "retrieveServiceConfigProps"
        params = {'propname': 'system',
                  'configname': 'SR_All_SCR_20140421'}
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
        test_stamp = TimeStamp()
        self.assertGreaterEqual(time_stamp._diffInt(test_stamp), 0, "Unexpected time stamp value, "
                                                                    "given time stamp is earlier than default time")

        test_stamp.getCurrent()
        self.assertLessEqual(time_stamp._diffInt(test_stamp), 0, "Unexpected time stamp value, "
                                                                 "given time stamp is in the future")

        self.assertTrue(alarm.getStatus() in alarm.getStatusChoices(),
                        "Invalid alarm status, status not in StatusChoices:  " + str(
                            alarm.getStatus()) + " not in " + str(alarm.getStatusChoices()))
        self.assertTrue(alarm.getSeverity() in alarm.getSeverityChoices(),
                        "Invalid alarm severity, severity not in SeverityChoices:  " + str(
                            alarm.getSeverity()) + " not in " + str(alarm.getSeverityChoices()))

    '''
    Tests retrieveServiceConfigs function, makes assertion for successful request and for correct results
    '''
    def testRetrieveServiceConfigs(self):
        function = "retrieveServiceConfigs"
        params = {'system': 'all'}
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
        test_stamp = TimeStamp()
        self.assertGreaterEqual(time_stamp._diffInt(test_stamp), 0, "Unexpected time stamp value, "
                                                                    "given time stamp is earlier than default time")

        test_stamp.getCurrent()
        self.assertLessEqual(time_stamp._diffInt(test_stamp), 0, "Unexpected time stamp value, "
                                                                 "given time stamp is in the future")

        self.assertTrue(alarm.getStatus() in alarm.getStatusChoices(),
                        "Invalid alarm status, status not in StatusChoices:  " + str(
                            alarm.getStatus()) + " not in " + str(alarm.getStatusChoices()))
        self.assertTrue(alarm.getSeverity() in alarm.getSeverityChoices(),
                        "Invalid alarm severity, severity not in SeverityChoices:  " + str(
                            alarm.getSeverity()) + " not in " + str(alarm.getSeverityChoices()))

    if __name__ == '__main__':
        unittest.main()
