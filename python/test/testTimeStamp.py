# testTimeStamp.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author Marty Kraimer 2011.07
import time
from timeStamp import TimeStamp as TimeStamp

timeStamp = TimeStamp()
timeStamp.getCurrent()
print "secondsPastEpoch ",timeStamp.getSecondsPastEpoch()
print "epicsSecondsPastEpoch ",timeStamp.getEpicsSecondsPastEpoch()
print "nanoSeconds ",timeStamp.getNanoSeconds()
print "seconds ",timeStamp.toSeconds()
print "toString",timeStamp
tm = timeStamp.toSeconds()
tupletime = time.localtime(tm)
string = time.strftime("%Y %b %d %H:%M:%S",tupletime)
print string
string = time.strftime("%x",tupletime)
print string
string = time.strftime("%X",tupletime)
print string
string = time.strftime("%c %Z",tupletime)
print string
another = TimeStamp(timeStamp.getSecondsPastEpoch(),timeStamp.getNanoSeconds())
print "seconds ",another.toSeconds()
if not timeStamp==another :
    print "timeStamp==another failed"
print "seconds ",another.toSeconds()
another.add(1.1)
print " after += 1.1 seconds ",another.toSeconds()
if timeStamp==another :
    print "timeStamp==another failed"
if not timeStamp<another :
    print "timeStamp==another failed"
if not timeStamp<=another :
    print "timeStamp<=another failed"
if timeStamp>another :
    print "timeStamp>another failed"
if timeStamp>=another :
    print "timeStamp>=another failed"
diff = another.toSeconds() - timeStamp.toSeconds()
print "diff",diff
another.sub(.1)
diff = another.toSeconds() - timeStamp.toSeconds()
print "diff",diff
milli = timeStamp.getMilliseconds()
print "timeStamp milli ",milli
another.putMilliseconds(milli)
print "another milli ",another.getMilliseconds()
diff = another.toSeconds() - timeStamp.toSeconds()
print "diff",diff



print "all done"

