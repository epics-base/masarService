import unittest
import time
from types import *

from masarclient.timeStamp import TimeStamp as TimeStamp

timeStamp = TimeStamp()

'''

Unittests for masarService/python/masarclient/timeStamp.py

'''


class TestTimeStamp(unittest.TestCase):

    '''
    Sets up test variable for each test.
    '''
    def setUp(self):
        self.test_time_stamp = TimeStamp()
        #self.test_time_stamp.getCurrent()

    '''
    Ensures test_time_stamp is cleared after each test
    '''
    def tearDown(self):
        self.test_time_stamp = 0

    '''
    Tests getter for time at the point of request
    '''
    def testGetCurrent(self):
        self.test_time_stamp.getCurrent()
        self.assertGreater(self.test_time_stamp.toSeconds(), 0.0, "Unexpected time returned")
        test_stamp_two = TimeStamp()
        test_stamp_two.getCurrent()
        self.assertGreaterEqual(test_stamp_two, self.test_time_stamp, "Unexpected error in time continuity")

    '''
    This test can not confirm time frame, so it will just ensure the function doesn't crash
    '''
    def testGetSecondsPastEpoch(self):
        self.test_time_stamp.getCurrent()
        self.assertGreater(self.test_time_stamp.getSecondsPastEpoch(), 0.0,
                           "TimeStamp returned unexpected value")

    '''
    This test can not confirm time frame, so it will just ensure the function doesn't crash
    '''
    def testGetEpicsSecondsPastEpoch(self):
        self.test_time_stamp.getCurrent()
        self.assertGreater(self.test_time_stamp.getEpicsSecondsPastEpoch(), 0.0,
                           "TimeStamp returned unexpected value")

    '''
    Test confirms operation of timeStamp.getNanoseconds() and performs logical test to ensure a reasonable result.
    Impossible to confirm actual time in nanoseconds.
    '''
    def testGetNanoseconds(self):
        test_stamp_nanoseconds = self.test_time_stamp.getNanoseconds()
        self.test_time_stamp.getCurrent()
        self.assertGreater(self.test_time_stamp.getNanoseconds(), test_stamp_nanoseconds,
                           "TimeStamp returned unexpected value")

    '''
    Test confirms operation of timeStamp.toSeconds() and performs logical test to ensure a reasonable result.
    '''
    def testToSeconds(self):
        test_stamp_seconds = self.test_time_stamp.toSeconds()
        self.test_time_stamp.getCurrent()
        self.assertGreaterEqual(self.test_time_stamp.toSeconds(), test_stamp_seconds,
                                "TimeStamp returned unexpected value")

    '''
    Ensures toString does not fail and properly returns a string
    '''
    def testToString(self):
        self.assertEqual(type(self.test_time_stamp.__str__()), StringType)

    '''
    This may be a bad test. This could result could be unintended.
    '''
    def testUserTag(self):
        self.assertEqual(type(self.test_time_stamp.getUserTag()), int)

    '''
    Tests method to set current time. Test could be expanded but would cause delays in run time.
    '''
    def testPut(self):
        for test_value_seconds in range(0, 100):
            for test_value_nanoseconds in range(0, 100):
                self.test_time_stamp.put(test_value_seconds, test_value_nanoseconds)
                self.assertTrue(self.test_time_stamp.getNanoseconds() == test_value_nanoseconds,
                                "TimeStamp.getNanoseconds returned an unexpected value")
                # Some variance is applied to the following test
                # it appears this variance does not typically exceed +/- .00000001
                self.assertTrue(self.test_time_stamp.toSeconds()+.1 >= test_value_seconds >= self.test_time_stamp.toSeconds()-.1,
                                "Timestamp.toSeconds returned an unexpected value")

    '''
    Tests method to set current time in milliseconds, test range was chosen arbitrarily
    '''
    def testPutMilliseconds(self):
        for test_value_milliseconds in range(0, 1000):
            self.test_time_stamp.putMilliseconds(test_value_milliseconds)
            self.assertTrue(test_value_milliseconds == self.test_time_stamp.getMilliseconds(),
                            "TimeStamp.getMilliseconds returned an unexpected value")

    '''
    Tests non-default constructor. Test ranges chosen arbitrarily, increasing scale slows test significantly
    '''
    def testNonDefaultConstructor(self):
        for test_value_seconds in range(0, 100):
            for test_value_nanoseconds in range(0, 100):
                self.test_time_stamp = TimeStamp(test_value_seconds, test_value_nanoseconds)
                self.assertTrue(self.test_time_stamp.getNanoseconds() == test_value_nanoseconds,
                                "TimeStamp.getNanoseconds returned an unexpected value")
                self.assertTrue(self.test_time_stamp.toSeconds()+.1 >= test_value_seconds >= self.test_time_stamp.toSeconds()-.1,
                                "Timestamp.toSeconds returned an unexpected value")

    if __name__ == '__main__':
        unittest.main()
