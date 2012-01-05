# alarm.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author Marty Kraimer 2011.07

class Alarm(object) :
    """an alarm has a severity and a message."""
    alarmSeverityNames = ("none","minor","major","invalid")
    alarmSeverity = (0,1,2,3)
    def __init__(self,severity = 0,message = "") :
        """constructor

        severity  The initial severity. The default is 0, i.e. noAlarm.
        message   The initial message. The default is an empty string."""
        if not isinstance(severity,int) :
            raise TypeError("severity is not an integer")
            return
        if (severity<0) or (severity>3) :
            raise ValueError("severity " + severity + "is out of range")
            return
        if not isinstance(message,str) :
            raise TypeError("message is not a str")
            return
        self.severity = severity
        self.message = message
    def __del__(self) :
        """destructor"""
        pass
    def __str__(self) :
        """Return a string that shows the message and severity"""
        return Alarm.alarmSeverityNames[self.severity] + " " + self.message;
    def getMessage(self) :
        """Get the message"""
        return self.message
    def setMessage(self,message) :
        """Set the message

        message The message. It must be a string."""
        if not isinstance(message,str) :
            raise TypeError("message is not a str")
            return
        self.message = message
    def getSeverity(self) :
        """Get the severity"""
        return self.severity
    def setSeverity(self,severity) :
        """Set the severity.

        severity The severity. It must be an integer between 0 and 3."""
        if not isinstance(severity,int) :
            raise TypeError("severity is not an integer")
            return
        if (severity<0) or (severity>3) :
            raise ValueError("severity " + severity + "is out of range")
            return
        self.severity = severity
