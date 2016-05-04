import unittest
from types import *
from masarclient.control import Control as Control


'''

Unittests for masarService/python/masarclient/control.py

'''
class unittestcontrol(unittest.TestCase):


    '''
    Tests both default value assignment and getter operation for LimitLow
    '''
    def testGetLimitLow(self):
        control = Control()
        self.assertEqual(0.0, control.getLimitLow(), "Default LimitLow did not return 0.0 ")

    '''
    Tests both default value assignment and getter operation for LimitHigh
    '''
    def testGetLimitHigh(self):
        control = Control()
        self.assertEqual(0.0, control.getLimitHigh(), "Default LimitHigh did not return 0.0 ")

    '''
    Tests both default value assignment and getter operation for MinStep
    '''
    def testGetMinStep(self):
        control = Control()
        self.assertEqual(0.0, control.getMinStep(), "Default MinStep did not return 0.0 ")

    '''
    Tests setter for LimitLow, requires getLimitLow
    '''
    def testSetLimitLow(self):
        control = Control()
        limitLowTestValue = -10.0  # Default test value can be changed here
        control.setLimitLow(limitLowTestValue)
        self.assertEqual(control.getLimitLow(), limitLowTestValue, "LimitLow does not match test input")

    '''
    Tests setter for LimitHigh, requires getLimitHigh
    '''
    def testSetLimitHigh(self):
        control = Control()
        limitHighTestValue = 10.0  # Default test value can be changed here
        control.setLimitHigh(limitHighTestValue)
        self.assertEqual(control.getLimitHigh(), limitHighTestValue, "LimitHigh does not match test input")

    '''
    Tests setter for MinStep, requires getMinStep
    '''
    def testSetMinStep(self):
        control = Control()
        minStepTestValue = 1.0  # Default test value can be changed here
        control.setMinStep(minStepTestValue)
        self.assertEqual(control.getMinStep(), minStepTestValue, "MinStep does not match test input")

    '''
    Tests GetControlPy and Control constructor, checks for consistency, tests all values
    '''
   # def testGetControlPy(self):
       # limitLowTestValue = -10.0  # Default test values may need to be changed
       # limitHighTestValue = 10.0
       # minStepTestValue = 1.0
       # control = Control(limitLowTestValue, limitHighTestValue, minStepTestValue)
       # print control
       # control2 = control.getControlPy()
       # print control2
       # self.assertEqual(control2.getLimitLow(), limitLowTestValue, "LimitLow does not match test input")
       # self.assertEqual(control2.getLimitHigh(), limitHighTestValue, "LimitHigh does not match test input")
       # self.assertEqual(control2.getMinStep(), minStepTestValue, "MinStep does not match test input")

    if __name__ == '__main__':
        unittest.main()
