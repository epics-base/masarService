# testnameValue.py
#
import unittest
import time
from masarclient.ntscalar import NTScalar as NTScalar
from masarclient.alarm import Alarm as Alarm
from masarclient.display import Display as Display
from masarclient.timeStamp import TimeStamp as TimeStamp
from masarclient.control import Control as Control

'''
Unittests for masarService/python/masarclient/ntscalar.py
'''


class TestNTScalar(unittest.TestCase):

    '''
    Ensures that getNTScalar returns properly
    '''
    def testGetNTScalar(self):
        scalar = NTScalar("double")
        newscalar = scalar.getNTScalar()
        self.assertNotEqual(newscalar, None)

    '''
    Tests getter for TimeStamp

    PLANNING: Not sure what to be testing for here, for now I'll just make sure a TimeStamp is returned
    within an appropriate range of values
    '''
    def testGetTimeStamp(self):
        test_timestamp = TimeStamp()
        test_ntscalar = NTScalar("double")
        test_ntscalar.getTimeStamp(test_timestamp)
        self.assertEqual(3, len(str(test_timestamp).split(":")))  # Timestamp string format test

    '''
    Tests getter for Alarm

    PLANNING: Not sure what to be testing for here, for now I'll just make sure the correct alarm is returned
    '''
    def testGetAlarm(self):
        test_alarm = Alarm()
        test_message = "test message"
        test_alarm.setMessage(test_message)
        test_ntscalar = NTScalar("double")
        test_ntscalar.getAlarm(test_alarm)
        self.assertEqual(test_alarm.getMessage(), test_message)
        self.assertEqual(test_alarm.getSeverity(), "NONE")
        self.assertEqual(test_alarm.getStatus(), "NONE")

    '''
    Tests getter for Control

    PLANNING: Not sure what to be testing for here, for now I'll just make sure the correct control is returned
    '''
    def testGetControl(self):
        test_min_step = 1  # these are the same default values used in the Control.py test
        test_limit_high = 10.0
        test_limit_low = -10.0
        test_control = Control(test_limit_low,
                               test_limit_high,
                               test_min_step)
        test_ntscalar = NTScalar("double")
        test_ntscalar.getControl(test_control)
        self.assertEqual(test_control.getMinStep(), test_min_step)
        self.assertEqual(test_control.getLimitLow(), test_limit_low)
        self.assertEqual(test_control.getLimitHigh(), test_limit_high)

    '''
    Tests getter for Display

    PLANNING: Not sure what to be testing for here,
              for now I'll just make sure the same display is returned
    '''
    def testGetDisplay(self):
        test_description = "test description"  # these are the same default values used in the Display.py test
        test_limit_high = 10.0
        test_limit_low = -10.0
        test_format = "%f"
        test_units = "voltage"
        test_display = Display(test_limit_low,
                               test_limit_high,
                               test_description,
                               test_format,
                               test_units)
        test_ntscalar = NTScalar("double")
        test_ntscalar.getDisplay(test_display)
        self.assertEqual(test_display.getDescription(), test_description)
        self.assertEqual(test_display.getLimitLow(), test_limit_low)
        self.assertEqual(test_display.getLimitHigh(), test_limit_high)
        self.assertEqual(test_display.getFormat(), test_format)
        self.assertEqual(test_display.getUnits(), test_units)

    '''
    Tests getter for Value, also tests default value assignment
    '''
    def testGetValue(self):
        test_ntscalar = NTScalar("double")
        self.assertEqual(test_ntscalar.getValue(), 0.0)

    '''
    Tests getter for Descriptor, also tests default value assignment
    '''
    def testGetDescriptor(self):
        test_ntscalar = NTScalar("double")
        self.assertEqual(test_ntscalar.getDescriptor(), "")

    if __name__ == '__main__':
        unittest.main()
