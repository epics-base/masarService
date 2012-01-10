# timeStamp.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author Marty Kraimer 2011.07

import time
import timeStampPy

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
        self.cppPvt = timeStampPy._init(self)
        timeStampPy._setSeconds(self.cppPvt,secondsPastEpoch)
        timeStampPy._setNano(self.cppPvt,nanoSeconds)
        self.normalize()
    def __del__(self) :
        """destructor"""
        timeStampPy._destroy(self.cppPvt)
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
        milliSeconds = int(self.getNanoSeconds()/TimeStamp.microSecPerSec)
        string += ".%03i" % milliSeconds
        return string
    def getTimeStampPy(self) :
        """Return an object for another extension module"""
        return timeStampPy._getTimeStampPy(self.cppPvt)
    def _diffInt(self,right) :
        """private method."""
        sdiff = self.getSecondsPastEpoch() - right.getSecondsPastEpoch()
        sdiff *= TimeStamp.nanoSecPerSec
        sdiff += self.getNanoSeconds() - right.getNanoSeconds()
        return long(sdiff)
    def normalize(self) :
        """Adjust secondsPastEpoch and nanoSeconds so that
            0<=nanoSeconds<nanoSecPerSec."""
        nano = self.getNanoSeconds()
        if nano>=0 and nano<TimeStamp.nanoSecPerSec :
            return
        secs = self.getSecondsPastEpoch()
        while nano>=TimeStamp.nanoSecPerSec :
           nano -= TimeStamp.nanoSecPerSec
           secs += 1
        while nano<0 :
           nano += TimeStamp.nanoSecPerSec
           secs -= 1
        timeStampPy._setSeconds(self.cppPvt,secs)
        timeStampPy._setNano(self.cppPvt,nano)
    def fromTime(self,secondsPastEpoch) :
        """Set timeStamp

        secondsPastEpoch The number of seconds since the epoch.
                         This can be a float.
                         The value returned by time.time() is a valid time.
        """
        seconds = long(secondsPastEpoch)
        nano = (secondsPastEpoch - seconds) * TimeStamp.nanoSecPerSec
        self.put(seconds,nano)
    def getSecondsPastEpoch(self) :
        """Return the secondsPastEpoch as a long."""
        return timeStampPy._getSeconds(self.cppPvt)
    def getEpicsSecondsPastEpoch(self) :
        """Return the seconds since the EPICS Epoch as a long.

        The EPICS Epoch is 1990.1.1 00:00:00 UTC."""
        return timeStampPy._getSeconds(self.cppPvt) - TimeStamp.posixEpochAtEpicsEpoch
    def getNanoSeconds(self) :
        """Get the number of nanoSeconds within the second as an int."""
        return timeStampPy._getNano(self.cppPvt)
    def put(self,secondsPastEpoch,nanoSeconds = 0) :
        """Set the time.

        secondsPastEpoch The number of seconds since the Epoch.
        nanoSeconds      The number of nano seconds within the second."""
        
        timeStampPy._setSeconds(self.cppPvt,long(secondsPastEpoch))
        timeStampPy._setNano(self.cppPvt,int(nanoSeconds))
        self.normalize()
    def putMilliseconds(self,milliSeconds) :
        """Set the time given the number of milliseconds since the Epoch.

        milliSeconds The number of milli seconds past the Epoch."""
        timeStampPy._setSeconds(self.cppPvt,long(milliSeconds/1000))
        nano = (milliSeconds%1000)*1000000
        timeStampPy._setNano(self.cppPvt,int(nano))
    def getCurrent(self) :
        """Set the time to the current time."""
        current = time.time()
        self.fromTime(current)
    def toSeconds(self) :
        """Return a float that is the number of seconds past the Epoch."""
        value = float(timeStampPy._getSeconds(self.cppPvt))
        nano = float(timeStampPy._getNano(self.cppPvt))
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
        newsecs = self.getSecondsPastEpoch()
        newnano = self.getNanoSeconds()
        if isinstance(seconds,int) or isinstance(seconds,long) :
            newsecs += seconds
        else :
            secs = long(seconds)
            nano = long((seconds - secs)*1e9)
            newnano = int(newnano + nano)
            if newnano >TimeStamp.nanoSecPerSec :
                newnano -= TimeStamp.nanoSecPerSec
                newsecs += 1
            elif newnano< -TimeStamp.nanoSecPerSec :
                newnano += TimeStamp.nanoSecPerSec
                newsecs -= 1
            newsecs += secs
        self.put(newsecs,newnano)
        return self
    def sub(self,other) :
        """subtract from time.

        seconds The number of seconds to subtract."""
        return self.add(-other)
    def getMilliseconds(self) :
        """Get the number of milli seconds since the epoch as a long."""
        return long(self.getSecondsPastEpoch()*1000 + self.getNanoSeconds()/1000000)
