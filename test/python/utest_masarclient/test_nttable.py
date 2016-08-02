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
    Tests getter for TimeStamp

    PLANNING: Not sure what to be testing for here, for now I'll just make sure a TimeStamp is returned
    that has the correct default value and leave the testing of TimeStamp itself to test_timeStamp.py
    '''
    def testGetTimeStamp(self):
        test_timestamp = TimeStamp()
        self.test_nttable.getTimeStamp(test_timestamp)
        test_stamp = TimeStamp()
        self.assertGreaterEqual(test_timestamp._diffInt(test_stamp), 0, "Unexpected time stamp value, "
                                                                        "given time stamp is earlier than default time")
        test_stamp.getCurrent()
        self.assertLess(test_timestamp._diffInt(test_stamp), 0, "Unexpected time stamp value, "
                                                                  "given time stamp is in the future")
    '''
    Tests getter for Alarm

    PLANNING: Not sure what to be testing for here, for now I'll just make sure the correct alarm is returned
    '''
    def testGetAlarm(self):
        test_alarm = Alarm()
        test_message = "test message"
        test_alarm.setMessage(test_message)
        self.test_nttable.getAlarm(test_alarm)
        self.assertEqual(test_alarm.getMessage(), test_message, "Alarm.message returned an unexpected value: " + str(test_alarm.getMessage()) + " expected " + str(test_message))
        self.assertEqual(test_alarm.getSeverity(), "NONE", "Alarm.severity returned an unexpected value: " + str(test_alarm.getSeverity()) + " expected NONE ")
        self.assertEqual(test_alarm.getStatus(), "NONE", "Alarm.status returned an unexpected value: " + str(test_alarm.getStatus()) + " expected NONE ")

    '''
    Tests getter for Labels
    '''
    def testGetLabels(self):
        labels = self.test_nttable.getLabels()
        test_nttable_keys = self.parameters.keys()
        for i in range(len(labels)):
            self.assertEqual(test_nttable_keys[i], labels[i], "Labels do not match given keys:  " + str(test_nttable_keys[i]) + " != " + str(labels[i]))

    '''
    This was a bad test, it assumed that the second value in each argument was meant to
    be the data, when in fact it was a type declaration. No data is entered and no data is returned.

    The test has been modified to check for the expected output given no data being input.
    There should be a new test to add data and make sure it is returned correctly.
    '''
    def testGetColumn(self):
        labels = self.test_nttable.getLabels()
        test_nttable_keys = self.parameters.keys()
        for i in range(len(labels)):
            test_column = self.test_nttable.getColumn(labels[i])
            self.assertEqual((), test_column)
    if __name__ == '__main__':
        unittest.main()
