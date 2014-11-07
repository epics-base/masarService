# ntmultiChannel.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author : Guobao Shen   2012.01
#          Marty Kraimer 2011.07

import ntmultiChannelPy


class NTMultiChannel(object):
    """Create an NTMultiChannel
    Given a object that is a python wrapper for a PVStructure
    that is a valid NTMultiChannel. This class can retrieve data from th
    NTMultiChannel and return the data as python objects.

    NOTE: THIS CLASS NEEDS MORE METHODS.

    """
    def __init__(self, capsule):
        """Constructor

        capsule Must be a pvStructure capsule
        This is created by other code that wraps a C++ method the
        returns a capsule.
        """
        self.cppPvt = ntmultiChannelPy._init(capsule)

    def __del__(self):
        """Destructor destroy the connection to the C++ data."""
        ntmultiChannelPy._destroy(self.cppPvt)

    def __str__(self):
        """Get a string value for the NTMultiChannel"""
        return ntmultiChannelPy._str(self.cppPvt)

    def getNTMultiChannel(self):
        """Get a python object that can be passed to
        another python method that is a wrapper to a C++ method
        that expects a PVStructure object."""
        return ntmultiChannelPy._getNTMultiChannelPy(self.cppPvt)

    def getPVStructure(self):
        """The data is saved as a PVStructure Get it.
        returns the PVStructure"""
        return ntmultiChannelPy._getPVStructure(self.cppPvt)

    def getTimeStamp(self, timeStamp):
        """Get the timeStamp from the NTMultiChannel
        timeStamp must be timeStamp.getTimeStampPy()
        """
        return ntmultiChannelPy._getTimeStamp(self.cppPvt, timeStamp.getTimeStampPy())

    def getAlarm(self, alarm) :
        """Get the alarm from the NTMultiChannel
        alarm must be alarm.getAlarmPy()
        """
        return ntmultiChannelPy._getAlarm(self.cppPvt, alarm.getAlarmPy())

    def getNumberChannel(self):
        """Get the alarm from the NTMultiChannel
        """
        return ntmultiChannelPy._getNumberChannel(self.cppPvt)

    def getValue(self):
        """get value """
        return ntmultiChannelPy._getValue(self.cppPvt)

    def getChannelValue(self,index):
        """get channelValue """
        return ntmultiChannelPy._getChannelValue(self.cppPvt,index)

    def getChannelName(self):
        """get channelName"""
        return ntmultiChannelPy._getChannelName(self.cppPvt)

    def getIsConnected(self):
        """get isConnected"""
        return ntmultiChannelPy._getIsConnected(self.cppPvt)

    def getSeverity(self):
        """get severity"""
        return ntmultiChannelPy._getSeverity(self.cppPvt)

    def getStatus(self):
        """get status"""
        return ntmultiChannelPy._getStatus(self.cppPvt)

    def getMessage(self):
        """get message"""
        return ntmultiChannelPy._getMessage(self.cppPvt)

    def getSecondsPastEpoch(self):
        """get secondsPastEpoch"""
        return ntmultiChannelPy._getSecondsPastEpoch(self.cppPvt)

    def getNanoseconds(self):
        """get nanoseconds"""
        return ntmultiChannelPy._getNanoseconds(self.cppPvt)

    def getUserTag(self):
        """get userTag"""
        return ntmultiChannelPy._getUserTag(self.cppPvt)

    def getDescriptor(self):
        """get descriptor"""
        return ntmultiChannelPy._getDescriptor(self.cppPvt)

