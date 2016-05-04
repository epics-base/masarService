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
timeStamp = TimeStamp()
alarm = Alarm()
control = Control()
display = Display()

print "getTimeStamp"
scalar.getTimeStamp(timeStamp)
print timeStamp
print "getAlarm"
scalar.getAlarm(alarm)
print alarm
print "getControl"
scalar.getControl(control)
print control
print "getDisplay"
scalar.getDisplay(display)
print display
'''

'''
Unittests for masarService/python/masarclient/ntscalar.py
'''


class unittestntscalar(unittest.TestCase):

    '''
    Receiving unexpected results from this test, "pvStructure" object

    def testGetLimitLow(self):
        scalar = NTScalar("double")
        print scalar
        newscalar = scalar.getNTScalar()
        print "new%%%%%%%%%%%%%%%%%"
        print str(newscalar)
    '''

    '''
    Tests getter for TimeStamp

    PLANNING: Not sure what to be testing for here, for now I'll just make sure a TimeStamp is returned
    that has the correct default value and leave the testing of TimeStamp itself to unittestTimeStamp.py
    '''
    def testGetTimeStamp(self):
        test_timestamp = TimeStamp()
        test_ntscalar = NTScalar("double")
        test_ntscalar.getTimeStamp(test_timestamp)
        self.assertEqual(str(test_timestamp), "1969.12.31 16:00:00.000", "TimeStamp returned an unexpected value")

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
        self.assertEqual(test_alarm.getMessage(), test_message, "Alarm.message returned an unexpected value")
        self.assertEqual(test_alarm.getSeverity(), "NONE", "Alarm.severity returned an unexpected value")
        self.assertEqual(test_alarm.getStatus(), "NONE", "Alarm.status returned an unexpected value")

    '''
    Tests getter for Control

    PLANNING: Not sure what to be testing for here, for now I'll just make sure the correct alarm is returned
    '''
    def testGetControl(self):
        test_control = Control()
        test_min_step = 1
        test_limit_high = 10.0
        test_limit_low = -10.0
        test_control.setMinStep(test_min_step)
        test_control.setLimitHigh(test_limit_high)
        test_control.setLimitLow(test_limit_low)
        test_ntscalar = NTScalar("double")
        test_ntscalar.getControl(test_control)
        self.assertEqual(test_control.getMinStep(), test_min_step, "Control.minStep returned an unexpected value")
        self.assertEqual(test_control.getLimitLow(), test_limit_low, "Control.limitLow returned an unexpected value")
        self.assertEqual(test_control.getLimitHigh(), test_limit_high, "Control.limitHigh returned an unexpected value")

    '''
    Tests getter for Display

    PLANNING: Not sure what to be testing for here, for now I'll just make sure the correct alarm is returned
    '''
    def testGetDisplay(self):
        test_display = Display()
        test_description = "test description"
        test_limit_high = 10.0
        test_limit_low = -10.0
        test_display.setDescription(test_description)
        test_display.setLimitHigh(test_limit_high)
        test_display.setLimitLow(test_limit_low)
        test_ntscalar = NTScalar("double")
        test_ntscalar.getDisplay(test_display)
        self.assertEqual(test_display.getDescription(), test_description, "Display.description returned an unexpected value")
        self.assertEqual(test_display.getLimitLow(), test_limit_low, "Display.limitLow returned an unexpected value")
        self.assertEqual(test_display.getLimitHigh(), test_limit_high, "Display.limitHigh returned an unexpected value")

    '''
    Tests getter for Value, also tests default value assignment
    '''
    def testGetValue(self):
        test_ntscalar = NTScalar("double")
        self.assertEqual(test_ntscalar.getValue(), 0.0, "Value returned an unexpected value")

    '''
    Tests getter for Descriptor, also tests default value assignment
    '''
    def testGetDescriptor(self):
        test_ntscalar = NTScalar("double")
        self.assertEqual(test_ntscalar.getDescriptor(), "", "Descriptor returned an unexpected value")

    if __name__ == '__main__':
        unittest.main()
