# timeStamp.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author Marty Kraimer 2011.07

import time

class TimeStamp(object) :
    """A timeStamp has secondsPastEpoch and nanoSeconds within the second.

    The Epoch is the posix Epoch, i. e. 1970.1.1 00:00:00 UTC.
    """
    milliSecPerSec = 1000
    microSecPerSec = milliSecPerSec*milliSecPerSec
    nanoSecPerSec = milliSecPerSec*microSecPerSec
    posixEpochAtEpicsEpoch = 631152000
    def __init__(self,secondsPastEpoch = 0,nanoSeconds = 0) :
        """constructor

        secondsPastEpoch The number of seconds since
                         Jan 1, 1970 00:00:00 UTC.
        nanoSeconds      The number of nanoSeconds within current second."""
        if (not isinstance(secondsPastEpoch,int)) and (not isinstance(secondsPastEpoch,long)) :
            raise TypeError("secondsPastEpoch is not an integer")
            return
        if (not isinstance(nanoSeconds,int)) and (not isinstance(nanoSeconds,long)) :
            raise TypeError("nanoSeconds is not an integer")
            return
        self.secondsPastEpoch = long(secondsPastEpoch)
        self.nanoSeconds = int(nanoSeconds)
        self.normalize()
    def __del__(self) :
        """destructor"""
        pass
    def __str__(self) :
        """returns a string that shows the time.

        The value is accurate to milli seconds.
        Note that by calling:
            tm = timeStamp.toSeconds()
            tupletime = time.localtime(tm)
        You can then call:
            string = time.strftime("xxx",tupletime)
        where xxx is a format specifying how you want the time displayed."""
        tm = self.toSeconds()
        tupletime = time.localtime(tm)
        string = time.strftime("%Y.%m.%d %H:%M:%S",tupletime)
        milliSeconds = int(self.nanoSeconds/TimeStamp.microSecPerSec)
        string += ".%03i" % milliSeconds
        return string
    def _diffInt(self,right) :
        """private method."""
        sdiff = self.secondsPastEpoch - right.secondsPastEpoch
        sdiff *= TimeStamp.nanoSecPerSec
        sdiff += self.nanoSeconds - right.nanoSeconds
        return long(sdiff)
    def normalize(self) :
        """Adjust secondsPastEpoch and nanoSeconds so that
            0<=nanoSeconds<nanoSecPerSec."""
        if self.nanoSeconds>=0 and self.nanoSeconds<TimeStamp.nanoSecPerSec :
            return
        while self.nanoSeconds>=TimeStamp.nanoSecPerSec :
           self.nanoSeconds -= TimeStamp.nanoSecPerSec
           self.secondsPastEpoch += 1
        while self.nanoSeconds<0 :
           self.nanoSeconds += TimeStamp.nanoSecPerSec
           self.secondsPastEpoch -= 1
    def fromTime(self,secondsPastEpoch) :
        """Set timeStamp

        secondsPastEpoch The number of seconds since the epoch.
                         This can be a float.
                         The value returned by time.time() is a valid time.
        """
        seconds = long(secondsPastEpoch)
        nano = (secondsPastEpoch - seconds) * TimeStamp.nanoSecPerSec
        self.secondsPastEpoch = seconds;
        self.nanoSeconds = int(nano)
    def getSecondsPastEpoch(self) :
        """Return the secondsPastEpoch as a long."""
        return self.secondsPastEpoch
    def getEpicsSecondsPastEpoch(self) :
        """Return the seconds since the EPICS Epoch as a long.

        The EPICS Epoch is 1990.1.1 00:00:00 UTC."""
        return self.secondsPastEpoch - TimeStamp.posixEpochAtEpicsEpoch
    def getNanoSeconds(self) :
        """Get the number of nanoSeconds within the second as an int."""
        return self.nanoSeconds
    def put(self,secondsPastEpoch,nanoSeconds = 0) :
        """Set the time.

        secondsPastEpoch The number of seconds since the Epoch.
        nanoSeconds      The number of nano seconds within the second."""
        self.secondsPastEpoch = long(secondsPastEpoch)
        self.nanoSeconds = int(nanoSeconds)
        self.normalize()
    def putMilliseconds(self,milliSeconds) :
        """Set the time given the number of milliseconds since the Epoch.

        milliSeconds The number of milli seconds past the Epoch."""
        self.secondsPastEpoch = long(milliSeconds/1000)
        nano = (milliSeconds%1000)*1000000
        self.nanoSeconds = int(nano)
    def getCurrent(self) :
        """Set the time to the current time."""
        current = time.time()
        self.fromTime(current)
    def toSeconds(self) :
        """Return a float that is the number of seconds past the Epoch."""
        value = float(self.secondsPastEpoch)
        nano = float(self.nanoSeconds)
        value += nano/1e9
        return value
    def __eq__(self,other) :
        """operator =="""
        sdiff = self._diffInt(other)
        if sdiff==0 :
             return True
        return False
    def __ne__(self,other) :
        """operator !="""
        sdiff = self._diffInt(other)
        if sdiff!=0 :
             return True
        return False
    def __le__(self,other) :
        """operator <="""
        sdiff = self._diffInt(other)
        if sdiff<=0 :
             return True
        return False
    def __lt__(self,other) :
        """operator <"""
        sdiff = self._diffInt(other)
        if sdiff<0 :
             return True
        return False
    def __ge__(self,other) :
        """operator >="""
        sdiff = self._diffInt(other)
        if sdiff>=0 :
             return True
        return False
    def __gt__(self,other) :
        """operator >"""
        sdiff = self._diffInt(other)
        if sdiff>0 :
             return True
        return False
    def add(self,seconds) :
        """add to time.

        seconds The number of seconds to add."""
        if isinstance(seconds,int) or isinstance(seconds,long) :
            self.secondsPastEpoch += seconds
            return
        if isinstance(seconds,float) :
            secs = long(seconds)
            nano = long((seconds - secs)*1e9)
            self.nanoSeconds = int(self.nanoSeconds + nano)
            if self.nanoSeconds>TimeStamp.nanoSecPerSec :
                self.nanoSeconds -= TimeStamp.nanoSecPerSec
                self.secondsPastEpoch += 1
            elif self.nanoSeconds< -TimeStamp.nanoSecPerSec :
                self.nanoSeconds += TimeStamp.nanoSecPerSec
                self.secondsPastEpoch -= 1
            self.secondsPastEpoch += secs
        return self
    def sub(self,other) :
        """subtract from time.

        seconds The number of seconds to subtract."""
        return self.add(-other)
    def getMilliseconds(self) :
        """Get the number of milli seconds since the epoch as a long."""
        return long(self.secondsPastEpoch*1000 + self.nanoSeconds/1000000)
