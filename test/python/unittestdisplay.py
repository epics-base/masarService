import unittest
from masarclient.display import Display as Display


'''

Unittests for masarService/python/masarclient/display.py

'''


class unittestDisplay(unittest.TestCase):

    '''
    Tests getter for Units, also tests default value assignment
    '''
    def testGetLimitLow(self):
        test_display = Display()
        self.assertEqual(test_display.getLimitLow(), 0.0, "LimitLow returned incorrect default value")

    '''
    Tests getter for Units, also tests default value assignment
    '''
    def testGetLimitHigh(self):
        test_display = Display()
        self.assertEqual(test_display.getLimitHigh(), 0.0, "LimitHigh returned incorrect default value")

    '''
    Tests getter for Units, also tests default value assignment
    '''
    def testGetLimitLow(self):
        test_display = Display()
        self.assertEqual(test_display.getDescription(), "", "Description returned incorrect default value")

    '''
    Tests getter for Units, also tests default value assignment
    '''
    def testGetFormat(self):
        test_display = Display()
        self.assertEqual(test_display.getFormat(), "", "Format returned incorrect default value")

    '''
    Tests getter for Units, also tests default value assignment
    '''
    def testGetUnits(self):
        test_display = Display()
        self.assertEqual(test_display.getUnits(), "", "Units returned incorrect default value")

    '''
    Tests setter for LimitLow, requires getLimitLow
    '''
    def testSetLimitLow(self):
        test_display = Display()
        test_limit_low = -10.0
        test_display.setLimitLow(test_limit_low)
        self.assertEqual(test_display.getLimitLow(), test_limit_low, "LimitLow does not match test input")

    '''
    Tests setter for LimitHigh, requires getLimitHigh
    '''
    def testSetLimitHigh(self):
        test_display = Display()
        test_limit_high = 10.0
        test_display.setLimitHigh(test_limit_high)
        self.assertEqual(test_display.getLimitHigh(), test_limit_high, "LimitHigh does not match test input")

    '''
    Tests setter for Description, requires getDescription
    '''
    def testSetLimitLow(self):
        test_display = Display()
        test_description = "test description"
        test_display.setDescription(test_description)
        self.assertEqual(test_display.getDescription(), test_description, "Description does not match test input")

    '''
    Tests setter for Format, requires getFormat
    '''
    def testSetFormat(self):
        test_display = Display()
        test_format = "%f"
        test_display.setFormat(test_format)
        self.assertEqual(test_display.getFormat(), test_format, "Format does not match test input")

    '''
    Tests setter for Units, requires getUnits
    '''
    def testSetUnits(self):
        test_display = Display()
        test_units = "volts"
        test_display.setUnits(test_units)
        self.assertEqual(test_display.getUnits(), test_units, "Units do not match test input")


    if __name__ == '__main__':
        unittest.main()
