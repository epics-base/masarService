# control.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author : Guobao Shen   2012.01
#          Marty Kraimer 2011.07

import controlPy

class Control(object) :
    """a control has limitLow, limitHigh, and minStep"""
    def __init__(self,limitLow  = 0.0, limitHigh = 0.0, minStep = 0.0) :
        """constructor
        limitLow  The default is 0.0;
        limitHigh The default is 0.0.
        minStep   The default is 0.0. """
        self.cppPvt = controlPy._init()
        if(limitLow!=0.0) :
            controlPy._setLimitLow(self.cppPvt,limitLow)
        if(limitHigh!=0.0) :
            controlPy._setLimitHigh(self.cppPvt,limitHigh)
        if(minStep!=0.0) :
            controlPy._setMinStep(self.cppPvt,minStep)
    def __del__(self) :
        """destructor"""
        controlPy._destroy(self.cppPvt)
    def __str__(self) :
        """Return a string that shows the current values """
        return controlPy._str(self.cppPvt)
    def getControlPy(self) :
        """Return an object for another extension module"""
        return controlPy._getControlPy(self.cppPvt)
    def getLimitLow(self) :
        """Get the severity"""
        return controlPy._getLimitLow(self.cppPvt)
    def setLimitLow(self,severity) :
        """Set the severity.

        severity The severity."""
        controlPy._setLimitLow(self.cppPvt,severity)
    def getLimitHigh(self) :
        """Get the status"""
        return controlPy._getLimitHigh(self.cppPvt)
    def setLimitHigh(self,status) :
        """Set the status.

        status The status."""
        controlPy._setLimitHigh(self.cppPvt,status)
    def getMinStep(self) :
        """Get the status"""
        return controlPy._getMinStep(self.cppPvt)
    def setMinStep(self,status) :
        """Set the status.

        status The status."""
        controlPy._setMinStep(self.cppPvt,status)
