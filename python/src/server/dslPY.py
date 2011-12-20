# dsl.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# This code is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author Marty Kraimer 2011.11

class DSL(object) :
    """Implements an IRMIS request."""
    def __init__(self) :
        """constructor"""
    def __del__(self) :
        """destructor"""
        pass
    def request(self,argument) :
        """issue request"""
        print "argument " + argument
        return argument
    def toString(self) :
        """Return a string that shows the message and severity"""
#        return Alarm.alarmSeverityNames[self.severity] + " " + self.message;
        pass
