import unittest
from types import *
from masarclient.control import Control as Control


'''

Unittests for masarService/python/masarclient/control.py

'''


class TestControl(unittest.TestCase):

    def setUp(self):
        self.control = Control()

    def tearDown(self):
        self.control = None
    '''
    Tests both default value assignment and getter operation for LimitLow
    '''
    def testGetLimitLow(self):
        self.assertEqual(0.0, self.control.getLimitLow(), "Default LimitLow did not return 0.0 instead returned:  " + str(self.control.getLimitLow()))

    '''
    Tests both default value assignment and getter operation for LimitHigh
    '''
    def testGetLimitHigh(self):
        self.assertEqual(0.0, self.control.getLimitHigh(), "Default LimitHigh did not return 0.0 instead returned:  " + str(self.control.getLimitHigh()))

    '''
    Tests both default value assignment and getter operation for MinStep
    '''
    def testGetMinStep(self):
        self.assertEqual(0.0, self.control.getMinStep(), "Default MinStep did not return 0.0 instead returned: " + str(self.control.getMinStep()))

    '''
    Tests setter for LimitLow, requires getLimitLow
    '''
    def testSetLimitLow(self):
        limitLowTestValue = -10.0  # Default test value can be changed here
        self.control.setLimitLow(limitLowTestValue)
        self.assertEqual(self.control.getLimitLow(), limitLowTestValue, "LimitLow does not match test input:  " + str(self.control.getLimitLow()) + " != " + str(limitLowTestValue))

    '''
    Tests setter for LimitHigh, requires getLimitHigh
    '''
    def testSetLimitHigh(self):
        limitHighTestValue = 10.0  # Default test value can be changed here
        self.control.setLimitHigh(limitHighTestValue)
        self.assertEqual(self.control.getLimitHigh(), limitHighTestValue, "LimitHigh does not match test input:  " + str(self.control.getLimitHigh()) + " != " + str(limitHighTestValue))

    '''
    Tests setter for MinStep, requires getMinStep
    '''
    def testSetMinStep(self):
        minStepTestValue = 1.0  # Default test value can be changed here
        self.control.setMinStep(minStepTestValue)
        self.assertEqual(self.control.getMinStep(), minStepTestValue, "MinStep does not match test input:  " + str(self.control.getMinStep()) + " != " + str(minStepTestValue))

    '''
    Tests Control's non-default constructor. Full use test.
    '''
    def testNonDefaultConstructor(self):
        limitLowTestValue = -10.0  # Default test values may need to be changed
        limitHighTestValue = 10.0
        minStepTestValue = 1.0
        control = Control(limitLowTestValue, limitHighTestValue, minStepTestValue)
        self.assertEqual(control.getLimitLow(), limitLowTestValue, "LimitLow does not match test input:  " + str(self.control.getLimitLow()) + " != " + str(limitLowTestValue))
        self.assertEqual(control.getLimitHigh(), limitHighTestValue, "LimitHigh does not match test input:  " + str(self.control.getLimitHigh()) + " != " + str(limitLowTestValue))
        self.assertEqual(control.getMinStep(), minStepTestValue, "MinStep does not match test input:  " + str(self.control.getMinStep()) + " != " + str(minStepTestValue))

    if __name__ == '__main__':
        unittest.main()
