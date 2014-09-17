# testtable.py
#

import time

from masarclient.nttable import NTTable as NTTable
from masarclient.alarm import Alarm as Alarm
from masarclient.timeStamp import TimeStamp as TimeStamp

timeStamp = TimeStamp()
alarm = Alarm()

params = {'column1': 'string',
          'column2': 'double'}

nttable = NTTable(params)
print nttable

newnttable = nttable.getNTTable()
print newnttable
print "getTimeStamp"
nttable.getTimeStamp(timeStamp)
print timeStamp
print "getAlarm"
nttable.getAlarm(alarm)
print alarm;
labels = nttable.getLabels()
print labels
n = len(labels)
for label in labels :
    column = nttable.getColumn(label)
    print column
