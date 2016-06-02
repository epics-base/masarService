from masarclient.alarm import Alarm as Alarm
import unittest
from types import *


'''

Unittests for masarService/python/masarclient/alarm.py

'''


class TestAlarm(unittest.TestCase):

    '''
    Create test values for each test. Uses default constructor values.
    '''
    def setUp(self):
        self.test_alarm = Alarm()

    '''
    Ensures test_alarm value is cleared after each test
    '''
    def tearDown(self):
        self.test_alarm = None

    '''
    Test to confirm all of the status choices are of the string type.
    '''
    def testStatusChoices(self):
        status_choices = self.test_alarm.getStatusChoices()
        for status in status_choices:
            self.assertEqual(type(status), StringType, "non-string status found: %r" % status)

    '''
    Test to confirm all of the severity choices are of the string type
    '''
    def testSeverityChoices(self):
        severity_choices = self.test_alarm.getSeverityChoices()
        for severity in severity_choices:
            self.assertEqual(type(severity), StringType, "non-string severity found: %r" % severity)

    '''
    Tests both default value assignment and getter operation for Status
    '''
    def testGetStatus(self):
        self.assertEqual(self.test_alarm.getStatus(), "NONE", "Default status did not return 'NONE' instead returned: " + repr(self.test_alarm.getStatus()))

    '''
    Tests both default value assignment and getter operation for Severity
    '''
    def testGetSeverity(self):
        self.assertEqual(self.test_alarm.getSeverity(), "NONE", "Default severity did not return 'NONE' instead returned: " + repr(self.test_alarm.getSeverity()))

    '''
    Tests both default value assignment and getter operation for Message
    '''
    def testGetMessage(self):
        self.assertEqual(self.test_alarm.getMessage(), "", "Default message did not return empty string instead returned: " + repr(self.test_alarm.getMessage()))

    '''
    Tests setter for status, also requires at least 1 status returned by getStatusChoices
    '''
    def testSetStatus(self):
        status_choices = self.test_alarm.getStatusChoices()
        status_index = len(status_choices)-1  # Test status will be the last in the list
        self.assertGreaterEqual(status_index, 0, "No status choices available to perform test.")
        self.test_alarm.setStatus(status_choices[status_index])  # Index may need to be changed if choices change
        self.assertEqual(self.test_alarm.getStatus(),  status_choices[status_index], "Status does not match test input:  " + repr(self.test_alarm.getStatus()) + " != " + repr(status_choices[status_index]))

    '''
    Tests setter for severity, also requires at least 1 severity returned by getSeverityChoices
    '''
    def testSetSeverity(self):
        severity_choices = self.test_alarm.getSeverityChoices()
        severity_index = len(severity_choices)-1  # Test severity will be the last in the list
        self.assertGreaterEqual(severity_index, 0, "No severity choices available to perform test: " + repr(severity_index))
        self.test_alarm.setSeverity(severity_choices[severity_index])  # Index may need to be changed if choices change
        self.assertEqual(self.test_alarm.getSeverity(), severity_choices[severity_index], "Severity does not match test input:  " + repr(self.test_alarm.getSeverity()) + " != " + repr(severity_choices[severity_index]))

    '''
    Tests setter for message, requires getMessage
    '''
    def testSetMessage(self):
        test_message = "test message"
        self.test_alarm.setMessage(test_message)
        self.assertEqual(self.test_alarm.getMessage(), test_message, "Message does not match test input:  " + repr(self.test_alarm.getMessage()) + " != " + test_message)

    '''
    Test non-default constructor value assignment. Full use test.
    '''
    def testNonDefaultConstructor(self):
        severity_choices = self.test_alarm.getSeverityChoices()
        test_severity = ""
        status_choices = self.test_alarm.getStatusChoices()
        test_status = ""
        test_message = "test message"
        if len(severity_choices) > 0:
            test_severity = severity_choices[len(severity_choices)%3]
        if len(status_choices) > 0:
            test_status = status_choices[len(status_choices)%3]
        self.test_alarm = Alarm(test_severity, test_status, test_message)
        self.assertEqual(self.test_alarm.getMessage(), test_message, "test_message did not match assigned value:  " + repr(self.test_alarm.getMessage()) + " != " + repr(test_message))
        self.assertEqual(self.test_alarm.getStatus(), test_status, "test_status did not match assigned value" + repr(self.test_alarm.getStatus()) + " != " + repr(test_status))
        self.assertEqual(self.test_alarm.getSeverity(), test_severity, "test_severity did not match assigned value" + repr(self.test_alarm.getSeverity()) + " != " + repr(test_severity))

    if __name__ == '__main__':
        unittest.main()
