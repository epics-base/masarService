# testnameValue.py
#

import time

from masarclient.ntnameValue import NTNameValue as NTNameValue
from masarclient.alarm import Alarm as Alarm
from masarclient.timeStamp import TimeStamp as TimeStamp

timeStamp = TimeStamp()
alarm = Alarm()

function = 'saveSnapshot'
params = {'configname': 'sr_test',
          'servicename': 'masar'}

ntnv = NTNameValue(function,params)
print ntnv

newntnv = ntnv.getNTNameValue()
print newntnv
print ntnv.getNames()
print ntnv.getValues()

print ntnv.getTimeStamp(timeStamp)
print ntnv.getAlarm(alarm)
