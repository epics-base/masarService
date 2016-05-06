import unittest
from masarclient.gatherV3Data import GatherV3Data as GatherV3Data
from masarclient.ntmultiChannel import NTMultiChannel as NTMultiChannel
from masarclient.alarm import Alarm as Alarm
from masarclient.timeStamp import TimeStamp as TimeStamp


'''

Unittests for masarService/python/masarclient/alarm.py

'''


class unittestgatherV3Data(unittest.TestCase):

    def testConnect(self):
        names = (
            'masarExampleBoUninit',
            'masarExampleMbboUninit',
            'masarExample0002',
            'masarExample0003',
            'masarExample0000',
            'masarExample0001',
            'masarExample0004',
            'masarExampleCharArray',
            'masarExampleUCharArray',
            'masarExampleStringArray',
            'masarExampleShortArray',
            'masarExampleLongArray',
            'masarExampleFloatArray',
            'masarExampleDoubleArray',
            )
        gatherV3Data = GatherV3Data(names)
        gatherV3Data.connect(2.0)

    if __name__ == '__main__':
        unittest.main()
