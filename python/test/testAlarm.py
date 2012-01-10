# testAlarm.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author Marty Kraimer 2011.07
from alarm import Alarm as Alarm

alarm = Alarm()
print alarm

statusChoices = alarm.getStatusChoices()
severityChoices = alarm.getSeverityChoices()
print "statusChoices"
print statusChoices
print "severityChoices"
print severityChoices
alarm.setStatus(statusChoices[7])
alarm.setSeverity(severityChoices[3])
alarm.setMessage("test message")
print "alarm"
print "message " + alarm.getMessage()
print "status " + alarm.getStatus()
print "severity " + alarm.getSeverity()
print alarm


print "all done"

