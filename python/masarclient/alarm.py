# alarm.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author Marty Kraimer 2011.07

import alarmPy

class Alarm(object) :
    """an alarm has a severity, status, and  message."""
    def __init__(self,severity = "", status = "" ,message = "") :
        """constructor

        severity  The initial severity. The default is "".
        status    The initial status. The default is "".
        message   The initial message. The default is an empty string."""
        self.cppPvt = alarmPy._init()
        alarmPy._setMessage(self.cppPvt,message)
        if severity!="" :
            alarmPy._setSeverity(self.cppPvt,severity)
        if status!="" :
            alarmPy._setStatus(self.cppPvt,status)
    def __del__(self) :
        """destructor"""
        alarmPy._destroy(self.cppPvt)
    def __str__(self) :
        """Return a string that shows the message and severity"""
        return alarmPy._str(self.cppPvt)
    def getAlarmPy(self) :
        """Return an object for another extension module"""
        return alarmPy._getAlarmPy(self.cppPvt)
    def getMessage(self) :
        """Get the message"""
        return alarmPy._getMessage(self.cppPvt)
    def setMessage(self,message) :
        """Set the message

        message The message. It must be a string."""
        if not isinstance(message,str) :
            raise TypeError("message is not a str")
            return
        alarmPy._setMessage(self.cppPvt,message)
    def getSeverity(self) :
        """Get the severity"""
        return alarmPy._getSeverity(self.cppPvt)
    def setSeverity(self,severity) :
        """Set the severity.

        severity The severity."""
        alarmPy._setSeverity(self.cppPvt,severity)
    def getStatus(self) :
        """Get the status"""
        return alarmPy._getStatus(self.cppPvt)
    def setStatus(self,status) :
        """Set the status.

        status The status."""
        alarmPy._setStatus(self.cppPvt,status)
    def getStatusChoices(self) :
        """Get the statusChoices"""
        return alarmPy._getStatusChoices(self.cppPvt)
    def getSeverityChoices(self) :
        """Get the severityChoices"""
        return alarmPy._getSeverityChoices(self.cppPvt)
