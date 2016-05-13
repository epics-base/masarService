import unittest

from masarclient.nttable import NTTable as NTTable
from masarclient.alarm import Alarm as Alarm
from masarclient.timeStamp import TimeStamp as TimeStamp


'''
Unittests for masarService/python/masarclient/nttable.py
'''


class TestNTTable(unittest.TestCase):

    '''
    Sets up new NTTable for each test with same initial parameters
    '''
    def setUp(self):
        self.parameters = {'column_one': 'string',
                       'column_two': 'double'}
        self.test_nttable = NTTable(self.parameters)

    '''
    Ensures global NTTable value is clear after each test
    '''
    def tearDown(self):
        self.test_nttable = 0

    '''
    Tests getter for TimeStamp

    PLANNING: Not sure what to be testing for here, for now I'll just make sure a TimeStamp is returned
    that has the correct default value and leave the testing of TimeStamp itself to test_timeStamp.py
    '''
    def testGetTimeStamp(self):
        test_timestamp = TimeStamp()
        self.test_nttable.getTimeStamp(test_timestamp)
        self.assertEqual(str(test_timestamp), "1969.12.31 16:00:00.000", "TimeStamp returned an unexpected value")

    '''
    Tests getter for Alarm

    PLANNING: Not sure what to be testing for here, for now I'll just make sure the correct alarm is returned
    '''
    def testGetAlarm(self):
        test_alarm = Alarm()
        test_message = "test message"
        test_alarm.setMessage(test_message)
        self.test_nttable.getAlarm(test_alarm)
        self.assertEqual(test_alarm.getMessage(), test_message, "Alarm.message returned an unexpected value")
        self.assertEqual(test_alarm.getSeverity(), "NONE", "Alarm.severity returned an unexpected value")
        self.assertEqual(test_alarm.getStatus(), "NONE", "Alarm.status returned an unexpected value")

    '''
    Tests getter for Labels
    '''
    def testGetLabels(self):
        labels = self.test_nttable.getLabels()
        test_nttable_keys = self.parameters.keys()
        for i in range(len(labels)):
            self.assertEqual(test_nttable_keys[i], labels[i], "Labels do not match given keys")

    '''
    Tests function for retrieving columns based on a label
    NOTE: Currently failing this test
    '''
    def testGetColumn(self):
        labels = self.test_nttable.getLabels()
        test_nttable_keys = self.parameters.keys()
        for i in range(len(labels)):
            print str(self.parameters[test_nttable_keys[i]])
            test_column = self.test_nttable.getColumn(labels[i])
            print str(test_column)
            self.assertEqual(self.parameters[test_nttable_keys[i]], test_column,
                             "Columns do not match given test names")

    if __name__ == '__main__':
        unittest.main()
