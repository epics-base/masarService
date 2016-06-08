import unittest
from masarclient.display import Display as Display


'''

Unittests for masarService/python/masarclient/display.py

'''


class TestDisplay(unittest.TestCase):

    '''
    Sets up test values for each test.
    '''
    def setUp(self):
        self.test_display = Display()

    '''
    Ensures test_display is cleared after each test.
    '''
    def tearDown(self):
        self.test_display = 0

    '''
    Tests getter for Units, also tests default value assignment
    '''
    def testGetLimitLow(self):
        self.assertEqual(self.test_display.getLimitLow(), 0.0, "LimitLow returned incorrect default value:  " + str(self.test_display.getLimitLow()))

    '''
    Tests getter for Units, also tests default value assignment
    '''
    def testGetLimitHigh(self):
        self.assertEqual(self.test_display.getLimitHigh(), 0.0, "LimitHigh returned incorrect default value:  " + str(self.test_display.getLimitHigh()))

    '''
    Tests getter for Units, also tests default value assignment
    '''
    def testGetLimitLow(self):
        self.assertEqual(self.test_display.getDescription(), "", "Description returned incorrect default value:  " + str(self.test_display.getDescription()))

    '''
    Tests getter for Units, also tests default value assignment
    '''
    def testGetFormat(self):
        self.assertEqual(self.test_display.getFormat(), "", "Format returned incorrect default value:  " + str(self.test_display.getFormat()))

    '''
    Tests getter for Units, also tests default value assignment
    '''
    def testGetUnits(self):
        self.assertEqual(self.test_display.getUnits(), "", "Units returned incorrect default value:  " + str(self.test_display.getUnits()))

    '''
    Tests setter for LimitLow, requires getLimitLow
    '''
    def testSetLimitLow(self):
        test_limit_low = -10.0
        self.test_display.setLimitLow(test_limit_low)
        self.assertEqual(self.test_display.getLimitLow(), test_limit_low, "LimitLow does not match test input:  " + str(self.test_display.getLimitLow()) + " != " + str(test_limit_low))

    '''
    Tests setter for LimitHigh, requires getLimitHigh
    '''
    def testSetLimitHigh(self):
        test_limit_high = 10.0
        self.test_display.setLimitHigh(test_limit_high)
        self.assertEqual(self.test_display.getLimitHigh(), test_limit_high, "LimitHigh does not match test input:  " + str(self.test_display.getLimitHigh()) + " != " + str(test_limit_high))

    '''
    Tests setter for Description, requires getDescription
    '''
    def testSetLimitLow(self):
        test_description = "test description"
        self.test_display.setDescription(test_description)
        self.assertEqual(self.test_display.getDescription(), test_description, "Description does not match test input:  " + str(self.test_display.getDescription()) + " != " + str(test_description))

    '''
    Tests setter for Format, requires getFormat
    '''
    def testSetFormat(self):
        test_format = "%f"
        self.test_display.setFormat(test_format)
        self.assertEqual(self.test_display.getFormat(), test_format, "Format does not match test input:  " + str(self.test_display.getFormat()) + " != " + str(test_format))

    '''
    Tests setter for Units, requires getUnits
    '''
    def testSetUnits(self):
        test_units = "volts"
        self.test_display.setUnits(test_units)
        self.assertEqual(self.test_display.getUnits(), test_units, "Units do not match test input:  " + str(self.test_display.getUnits()) + " != " + str(test_units))


    '''
    Tests non-default constructor. Full use test.
    '''
    def testNonDefaultConstructor(self):
        test_limit_low = -10.0
        test_limit_high = 10.0
        test_description = "test description"
        test_format = "%f"
        test_units = "volts"
        self.test_display = Display(test_limit_low,
                                    test_limit_high,
                                    test_description,
                                    test_format,
                                    test_units)
        self.assertEqual(self.test_display.getLimitLow(), test_limit_low, "test_limit_low did not return given value:  " + str(self.test_display.getLimitLow()) + " != " + str(test_limit_low))
        self.assertEqual(self.test_display.getLimitHigh(), test_limit_high, "test_limit_high did not return given value:  " + str(self.test_display.getLimitHigh()) + " != " + str(test_limit_high))
        self.assertEqual(self.test_display.getDescription(), test_description, "test_description did not return given value:  " + str(self.test_display.getDescription()) + " != " + str(test_description))
        self.assertEqual(self.test_display.getFormat(), test_format, "test_format did not return given value:  " + str(self.test_display.getFormat()) + " != " + str(test_format))
        self.assertEqual(self.test_display.getUnits(), test_units, "test_units did not return given value:  " + str(self.test_display.getUnits()) + " != " + str(test_units))

    if __name__ == '__main__':
        unittest.main()
