# ntscalar.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author : Guobao Shen   2012.01
#          Marty Kraimer 2011.07

import ntscalarPy

class NTScalar(object) :
    """Create an NTScalar
    Given a object that is a python wrapper for a PVStructure
    that is a valid NTScalar. This class can retrieve data from th
    NTScalar and return the data as python objects.

    NOTE: THIS CLASS NEEDS MORE METHODS.

    """
    def __init__(self,arg) :
        """Constructor

        arg must be a scalarType or a pvStructure capsule
        A capsule is created by other code that wraps a C++ method the
        returns a capsule.
        """
        if isinstance(arg,str) :
            self.cppPvt = ntscalarPy._create(arg)
        else :
            self.cppPvt = ntscalarPy._init(arg)
    def __del__(self) :
        """Destructor destroy the connection to the C++ data."""
        ntscalarPy._destroy(self.cppPvt)
    def __str__(self) :
        """Get a string value for the NTScalar"""
        return ntscalarPy._str(self.cppPvt);
    def getNTScalar(self) :
        """Get a python object that can be passed to
        another python method that is a wrapper to a C++ method
        that expects a PVStructure object."""
        return ntscalarPy._getNTScalarPy(self.cppPvt);
    def getPVStructure(self) :
        """The data is saved as a PVStructure Get it.
        returns the PVStructure"""
        return ntscalarPy._getPVStructure(self.cppPvt)
    def getValue(self) :
        """get value """
        return ntscalarPy._getValue(self.cppPvt);
    def getTimeStamp(self,timeStamp) :
        """Get the timeStamp from the NTScalar
        timeStamp must be timeStamp.getTimeStampPy()
        """
        return ntscalarPy._getTimeStamp(self.cppPvt,timeStamp.getTimeStampPy());
    def getAlarm(self,alarm) :
        """Get the alarm from the NTScalar
        alarm must be alarm.getAlarmPy()
        """
        return ntscalarPy._getAlarm(self.cppPvt,alarm.getAlarmPy());
    def getDisplay(self,display) :
        """Get the display from the NTScalar
        display must be display.getDisplayPy()
        """
        return ntscalarPy._getDisplay(self.cppPvt,display.getDisplayPy());
    def getControl(self,control) :
        """Get the control from the NTScalar
        control must be control.getControlPy()
        """
        return ntscalarPy._getControl(self.cppPvt,control.getControlPy());
    def getDescriptor(self) :
        """get descriptor"""
        return ntscalarPy._getDescriptor(self.cppPvt);

