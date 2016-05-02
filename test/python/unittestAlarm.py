from masarclient.alarm import Alarm as Alarm
import unittest
from types import *


'''

Unittests for masarService/python/masarclient/alarm.py

'''
class unittestAlarm(unittest.TestCase):

    '''
    Test to confirm all of the status choices are of the string type.
    '''
    def testStatusChoices(self):
        test_alarm = Alarm()
        statusChoices = test_alarm.getStatusChoices()
        for status in statusChoices:
            assert type(status) is StringType, "non-string status found: %r" % status

    '''
    Test to confirm all of the severity choices are of the string type
    '''
    def testSeverityChoices(self):
        test_alarm = Alarm()
        severityChoices = test_alarm.getSeverityChoices()
        for severity in severityChoices:
            assert type(severity) is StringType, "non-string severity found: %r" % severity

    '''
    Tests both default value assignment and getter operation for Status
    '''
    def testGetStatus(self):
        test_alarm = Alarm()
        self.assertEqual(test_alarm.getStatus(), "NONE", "Default status did not return 'NONE'")

    '''
    Tests both default value assignment and getter operation for Severity
    '''
    def testGetSeverity(self):
        test_alarm = Alarm()
        self.assertEqual(test_alarm.getSeverity(), "NONE", "Default severity did not return 'NONE'")

    '''
    Tests both default value assignment and getter operation for Message
    '''
    def testGetMessage(self):
        test_alarm = Alarm()
        self.assertEqual(test_alarm.getMessage(), "", "Default message did not return empty string")

    '''
    Tests setter for status, also requires at least 1 status returned by getStatusChoices
    '''
    def testSetStatus(self):
        test_alarm = Alarm()
        statusChoices = test_alarm.getStatusChoices()
        status_index = len(statusChoices)-1 # Test status will be the last in the list
        self.assertTrue(status_index >= 0, "No status choices available to perform test.")
        test_alarm.setStatus(statusChoices[status_index]) # Index may need to be changed if choices change
        self.assertEqual(test_alarm.getStatus(),statusChoices[status_index], "Status does not match test input")

    '''
    Tests setter for severity, also requires at least 1 severity returned by getSeverityChoices
    '''
    def testSetSeverity(self):
        test_alarm = Alarm()
        severityChoices = test_alarm.getSeverityChoices()
        severity_index = len(severityChoices)-1 # Test severity will be the last in the list
        self.assertTrue(severity_index >= 0, "No severity choices available to perform test.")
        test_alarm.setSeverity(severityChoices[severity_index]) # Index may need to be changed if choices change
        self.assertEqual(test_alarm.getSeverity(),severityChoices[severity_index], "Severity does not match test input")

    '''
    Tests setter for message, requires getMessage
    '''
    def testSetMessage(self):
        test_alarm = Alarm()
        test_message = "test message"
        test_alarm.setMessage(test_message)
        self.assertEqual(test_alarm.getMessage(),test_message, "Message does not match test input")
    
    if __name__ == '__main__':
        unittest.main()