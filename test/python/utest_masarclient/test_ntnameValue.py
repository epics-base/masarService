import unittest

from masarclient.ntnameValue import NTNameValue as NTNameValue
from masarclient.alarm import Alarm as Alarm
from masarclient.timeStamp import TimeStamp as TimeStamp

'''

Unittests for masarService/python/masarclient/ntnameValue.py

'''


class TestNTNameValue(unittest.TestCase):

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
        self.test_ntnv = None

    '''
    This test just confirms that a PVStructure is returned and is not equal to none
    '''
    def testGetPVStructure(self):
        self.assertNotEqual(self.test_ntnv.getPVStructure(), None)


    '''
    Tests getter for service and config name, also tests default value assignment
    '''
    def testGetName(self):
        test_ntnv_servicename = self.test_ntnv.getName()[0]
        test_ntnv_configname = self.test_ntnv.getName()[1]
        self.assertEqual(test_ntnv_servicename, "servicename", "servicename returned incorrect default value:  " + str(test_ntnv_servicename))
        self.assertEqual(test_ntnv_configname, "configname", "configname returned incorrect default value:  " + str(test_ntnv_configname))

    '''
    Tests getter for values, also tests default value assignment
    '''
    def testGetValue(self):
        test_ntnv_value_one = self.test_ntnv.getValue()[0]
        test_ntnv_value_two = self.test_ntnv.getValue()[1]
        self.assertEqual(test_ntnv_value_one, "masar", "ntnv value one returned incorrect default value:  " + str(test_ntnv_value_one))
        self.assertEqual(test_ntnv_value_two, "sr_test", "ntnv value two returned incorrect default value:  " + str(test_ntnv_value_two))

    '''
    NOTE: These are commented out because their responses "None" "None" appear to be incorrect

    Tests getter for TimeStamp, uses default TimeStamp

    def testGetTimeStamp(self):
        timeStamp = TimeStamp()
        print self.test_ntnv.getTimeStamp(timeStamp)


    #Tests getter for Alarm, uses default alarm
    def testGetAlarm(self):
        alarm = Alarm()
        print self.test_ntnv.getAlarm(alarm)
    '''
if __name__ == '__main__':
    unittest.main()
