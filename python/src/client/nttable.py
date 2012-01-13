# nttable.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author Marty Kraimer 2011.07

import nttablePy

class NTTable(object) :
    """Create an NTTable
    Given a object that is a python wrapper for a PVStructure
    that is a valid NTTable. This class can retrieve data from th
    NTTable and return the data as python objects.

    NOTE: THIS CLASS NEEDS MORE METHODS.

    """
    def __init__(self,capsule) :
        """Constructor

        capsule Must be a pvStructure capsule
        This is created by other code that wraps a C++ method the
        returns a capsule.
        """
        self.cppPvt = nttablePy._init(capsule)
    def __del__(self) :
        """Destructor destroy the connection to the C++ data."""
        nttablePy._destroy(self.cppPvt)
    def __str__(self) :
        """Get a string value for the NTTable"""
        return nttablePy._str(self.cppPvt);
    def getNTTable(self) :
        """Get a python object that can be passed to
        another python method that is a wrapper to a C++ method
        that expects a PVStructure object."""
        return ntnameValuePy._getNTTablePy(self.cppPvt);
    def getTimeStamp(self,timeStamp) :
        """Get the timeStamp from the NTTable
        timeStamp must be timeStamp.getTimeStampPy()
        """
        return nttablePy._getTimeStamp(self.cppPvt,timeStamp);
    def getAlarm(self,alarm) :
        """Get the alarm from the NTTable
        alarm must be alarm.getAlarmPy()
        """
        return nttablePy._getAlarm(self.cppPvt,alarm);
    def getNumberValues(self) :
        """get the number of value fields"""
        return nttablePy._getNumberValues(self.cppPvt);
    def getLabel(self) :
        """get the label"""
        return nttablePy._getLabel(self.cppPvt);
    def getValue(self,index) :
        """get the value for the specified index"""
        return nttablePy._getValue(self.cppPvt,index);
