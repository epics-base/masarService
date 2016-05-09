import unittest

from masarclient.ntnameValue import NTNameValue as NTNameValue
from masarclient.alarm import Alarm as Alarm
from masarclient.timeStamp import TimeStamp as TimeStamp

'''

Unittests for masarService/python/masarclient/ntnameValue.py

'''


class unittestNTNameValue(unittest.TestCase):

    '''
    Sets up default NTNameValue object to be used in each test
    '''
    def setUp(self):
        function = 'saveSnapshot'
        params = {'configname': 'sr_test',
                  'servicename': 'masar'}
        self.test_ntnv = NTNameValue(function, params)

    '''
    Cleans up test_ntnv variable after each test
    '''
    def tearDown(self):
        self.test_ntnv = 0

    '''
    This tests is commented out because I need to confirm what result should be tested for
    
    def testGetPVStructure(self):
        print str(self.test_ntnv.getPVStructure().)
    '''

    '''
    Tests getter for service and config name, also tests default value assignment
    '''
    def testGetName(self):
        test_ntnv_servicename = self.test_ntnv.getName()[0]
        test_ntnv_configname = self.test_ntnv.getName()[1]
        self.assertEqual(test_ntnv_servicename, "servicename", "servicename returned incorrect default value")
        self.assertEqual(test_ntnv_configname, "configname", "configname returned incorrect default value")

    '''
    Tests getter for values, also tests default value assignment
    '''
    def testGetValue(self):
        test_ntnv_value_one = self.test_ntnv.getValue()[0]
        test_ntnv_value_two = self.test_ntnv.getValue()[1]
        self.assertEqual(test_ntnv_value_one, "masar", "ntnv value one returned incorrect default value")
        self.assertEqual(test_ntnv_value_two, "sr_test", "ntnv value two returned incorrect default value")

    '''
    NOTE: These are commented out because their responses "None" "None" appear to be incorrect

    Tests getter for TimeStamp, uses default TimeStamp

    def testGetTimeStamp(self):
        timeStamp = TimeStamp()
        print self.test_ntnv.getTimeStamp(timeStamp.getTimeStampPy())


    #Tests getter for Alarm, uses default alarm
    def testGetAlarm(self):
        alarm = Alarm()
        print self.test_ntnv.getAlarm(alarm.getAlarmPy())
    '''
if __name__ == '__main__':
    unittest.main()
