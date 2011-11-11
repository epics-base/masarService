# maser.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author Marty Kraimer 2011.07

import numpy

from alarm import Alarm as Alarm
from timeStamp import TimeStamp as TimeStamp

import maserPy

class Maser(object) :
    """Constuctor"""
    def __init__(self) :
        """constructor"""
        self.cppPvt = maserPy._init(self)
    def __del__(self) :
        """destructor"""
        maserPy._destroy(self.cppPvt)
    def getAlarm(self,alarm) :
        """Update alarm from the C++ alarm

        alarm The python alarm"""
        return maserPy._getAlarm(self.cppPvt,alarm)
    def getTimeStamp(self,timeStamp) :
        """Update timeStamp from the C++ timeStamp

        timeStamp The python timeStamp"""
        return maserPy._getTimeStamp(self.cppPvt,timeStamp)
    def getNumberChannels(self) :
        """Get the number of V3 channels"""
        return maserPy._getNumberChannels(self.cppPvt)
    def anyBad(self) :
        """Returns (False,True) if any of the V3 channels (are not,are) bad"""
        if maserPy._anyBad(self.cppPvt) :
            return True
        return False
    def isBad(self,index) :
        """is the V3 channel bad

        index Index of the channel"""
        if maserPy._isBad(self.cppPvt,index) :
            return True
        return False
    def badChange(self) :
        """Has the bad value of any V3 channel changed since the last call?

        Note the calling resets the value to False"""
        if maserPy._badChange(self.cppPvt) :
            return True
        return False
    def allConnected(self) :
        """Are all V3 channels connected?"""
        if maserPy._allConnected(self.cppPvt) :
            return True
        return False
    def isConnected(self,index) :
        """Is the V3 channel connected?

        index The channel index"""
        if maserPy._isConnected(self.cppPvt,index) :
            return True
        return False
    def connectionChange(self) :
        """Has the connection state of any V3 channel changed?

        Note that the value is reset to False"""
        if maserPy._connectionChange(self.cppPvt) :
            return True
        return False
    def getSeverity(self,index) :
        """Get the alarm severity of the V3 channel.

        index The channel index"""
        return maserPy._getSeverity(self.cppPvt,index)
    def severityChange(self) :
        """Has the severity of any V3 channel changed?

        Note that the value is reset to False"""
        if maserPy._severityChange(self.cppPvt) :
            return True
        return False
class MaserScalar(Maser) :
    """constructor for each V3 channel being a scalar double."""
    def __init__(self,cppPvt) :
        """Called by implementation code."""
        Maser.__init__(self,cppPvt)
        self.cppPvt = cppPvt
    def getValue(self) :
        """Get the array of scalar values.

        A numpy double array is returned."""
        return maserPy._getScalarValue(self.cppPvt)
    def setValue(self,doubleArray) :
        """Set the array of scalar values.

        doubleArray Must be a numpy one dimensional array of double"""
        return maserPy._setScalarValue(self.cppPvt,doubleArray)
class MaserArray(Maser) :
    """constructor for each V3 channel being an array of double"""
    def __init__(self) :
        """Called by implementation code."""
        Maser.__init__(self)
        raise NotImplementedError("MaserArray not implemented")
    def getValue(self,index) :
        raise NotImplementedError("MaserArray not implemented")
    def setValue(self,value,index) :
        raise NotImplementedError("MaserArray not implemented")
