import unittest
import sys
import traceback

from masarclient.channelRPC import ChannelRPC as ChannelRPC
from masarclient.channelRPC import epicsExit
from masarclient.ntscalar import NTScalar
from masarclient.ntnameValue import NTNameValue
from masarclient.ntmultiChannel import NTMultiChannel
from masarclient.nttable import NTTable
from masarclient.alarm import Alarm
from masarclient.timeStamp import TimeStamp

'''

Unittests for masarService/python/masarclient/channelRPC.py

'''


class unittestchannelRPC(unittest.TestCase):

    '''
    Tests initial connection to channelRPC
    '''
    def testGetLimitLow(self):
        channelRPC = ChannelRPC("masarService")
        channelRPC.issueConnect()
        if not channelRPC.waitConnect(1.0):
            print "error when waiting connection.", channelRPC.getMessage()
            exit(1)

    if __name__ == '__main__':
        unittest.main()
