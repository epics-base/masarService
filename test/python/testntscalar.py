# testnameValue.py
#

import time

from masarclient.ntscalar import NTScalar as NTScalar
from masarclient.alarm import Alarm as Alarm
from masarclient.timeStamp import TimeStamp as TimeStamp
from masarclient.control import Control as Control
from masarclient.display import Display as Display

timeStamp = TimeStamp()
alarm = Alarm()
control = Control()
display = Display()

scalar = NTScalar("double")
print scalar

newscalar = scalar.getNTScalar()
print newscalar
print "getTimeStamp"
scalar.getTimeStamp(timeStamp)
print timeStamp
print "getAlarm"
scalar.getAlarm(alarm)
print alarm
print "getControl"
scalar.getControl(control)
print control
print "getDisplay"
scalar.getDisplay(display)
print display
