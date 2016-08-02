# display.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author : Guobao Shen   2012.01
#          Marty Kraimer 2011.07

import displayPy

class Display(object) :
    """a display has limitLow, limitHigh, description, format, and units"""
    def __init__(self,limitLow  = 0.0,limitHigh = 0.0, description = "" , displayFormat = "", units = "") :
        """constructor
        limitLow      The default is 0.0;
        limitHigh     The default is 0.0.
        description   The default is "".
        displayFormat The default is "".
        units         The default is ""."""
        self.cppPvt = displayPy._init()
        if(limitLow!=0.0) :
            displayPy._setLimitLow(self.cppPvt,limitLow)
        if(limitHigh!=0.0) :
            displayPy._setLimitHigh(self.cppPvt,limitHigh)
        displayPy._setDescription(self.cppPvt,description)
        displayPy._setFormat(self.cppPvt,displayFormat)
        displayPy._setUnits(self.cppPvt,units)
    def __del__(self) :
        """destructor"""
        displayPy._destroy(self.cppPvt)
    def __str__(self) :
        """Return a string that shows the current values """
        return displayPy._str(self.cppPvt)
    def getDisplayPy(self) :
        """Return an object for another extension module"""
        return displayPy._getDisplayPy(self.cppPvt)
    def getLimitLow(self) :
        """Get the severity"""
        return displayPy._getLimitLow(self.cppPvt)
    def setLimitLow(self,severity) :
        """Set the severity.

        severity The severity."""
        displayPy._setLimitLow(self.cppPvt,severity)
    def getLimitHigh(self) :
        """Get the status"""
        return displayPy._getLimitHigh(self.cppPvt)
    def setLimitHigh(self,status) :
        """Set the status.

        status The status."""
        displayPy._setLimitHigh(self.cppPvt,status)
    def getDescription(self) :
        """Get the description"""
        return displayPy._getDescription(self.cppPvt)
    def setDescription(self,description) :
        """Set the description

        description The description. It must be a string."""
        if not isinstance(description,str) :
            raise TypeError("description is not a str")
            return
        displayPy._setDescription(self.cppPvt,description)
    def getFormat(self) :
        """Get the description"""
        return displayPy._getFormat(self.cppPvt)
    def setFormat(self,description) :
        """Set the description

        description The description. It must be a string."""
        if not isinstance(description,str) :
            raise TypeError("description is not a str")
            return
        displayPy._setFormat(self.cppPvt,description)
    def getUnits(self) :
        """Get the description"""
        return displayPy._getUnits(self.cppPvt)
    def setUnits(self,description) :
        """Set the description

        description The description. It must be a string."""
        if not isinstance(description,str) :
            raise TypeError("description is not a str")
            return
        displayPy._setUnits(self.cppPvt,description)

