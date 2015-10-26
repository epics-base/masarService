# ntnameValue.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author : Guobao Shen   2012.01
#          Marty Kraimer 2011.07

import ntnameValuePy

class NTNameValue(object) :
    """Create a NTNameValue

    """
    def __init__(self,function,dictionary) :
        """Constructor
         Creates a C++ NTNameValue and a python wrapper for the NTNameValue.

        function A string that specifies a function name.
        dictionary A python dictionary that is a sequence of name,value pairs"""
        self.cppPvt = ntnameValuePy._init(function,dictionary)
    def __del__(self) :
        """Destructor Destroy the C++ NTNameValue"""
        ntnameValuePy._destroy(self.cppPvt)
    def __str__(self) :
        """Get a string value for the NTNameValue."""
        return ntnameValuePy._str(self.cppPvt)
    def getNTNameValue(self) :
        """Get a python object that can be passed to
        another python method that is a wrapper to a C++ method
        that expects a PVStructure object."""
        return ntnameValuePy._getNTNameValuePy(self.cppPvt);
    def getPVStructure(self) :
        """The data is saved as a PVStructure Get it.
        returns the PVStructure"""
        return ntnameValuePy._getPVStructure(self.cppPvt)
    def getTimeStamp(self,timeStamp) :
        """Get the timeStamp from the NTTable
        timeStamp must be timeStamp.getTimeStampPy()
        """
        return ntnameValuePy._getTimeStamp(self.cppPvt,timeStamp);
    def getAlarm(self,alarm) :
        """Get the alarm from the NTTable
        alarm must be alarm.getAlarmPy()
        """
        return ntnameValuePy._getAlarm(self.cppPvt,alarm);
    def getName(self) :
        """get the names"""
        return ntnameValuePy._getName(self.cppPvt);
    def getValue(self) :
        """get the values"""
        return ntnameValuePy._getValue(self.cppPvt);
