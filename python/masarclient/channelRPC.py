# channelRPC.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author : Guobao Shen   2012.01
#          Marty Kraimer 2011.07
from _epicsexit import (epicsExit, epicsExitCallAtExits)

import channelRPCPy

class ChannelRPC(object) :
    """Create a ChannelRPC

    Typical usage is:

    Following done once
    channelRPC = ChannelRPC(channelName)
    result = channelRPC.connect(timeOut)
    if not result :
        #take some action

    Following done for each channelRPC request
    result = channelRPC.request(argument,lastRequest)
    if result==None
        #take some action
    """
    def __init__(self,channelName) :
        """Constructor

        channelName The pvName of the channelRPC record for the service.
        request  A string to turn into a pvRequest"""
        self.cppPvt = channelRPCPy._init(channelName)

    def __del__(self) :
        """Destructor Destroys the connection to the server"""

    def connect(self,timeout=5.0) :
        """Connect to the channelRPC service

          timeout is in seconds."""
        result = channelRPCPy._connect(self.cppPvt,timeout);
        if result==None :
            return True
        return False

    def issueConnect(self) :
        """issueConnect to the channelRPC servicei.i
          This does not block.
          waitConnect must be called to complete the request"""
        channelRPCPy._issueConnect(self.cppPvt)
        return

    def waitConnect(self,timeout=5.0) :
        """Wait until connect or timeout

        timeOut The timeout in seconds

        returns true or false"""
        result = channelRPCPy._waitConnect(self.cppPvt,timeout)
        if result==None :
            return True
        return False

    def request(self,argument,lastRequest) :
        """Send a channelRPC request

        argument     An object that has a method that returns a PyCapsule
                     that returns the address of  a PVStructure::shared_pointer.
        lastRequest  Either True or False
        returns the result on None if the request failed"""
        return channelRPCPy._request(self.cppPvt,argument,lastRequest)

    def issueRequest(self,argument,lastRequest) :
        """issue a channelRPC request.
        This does not block.
        waitRequest must be called to complete the request.

        argument     An object that has a method that returns a PyCapsule
                     that returns the address of  a PVStructure::shared_pointer.
        lastRequest  Either True or False"""
        channelRPCPy._issueRequest(self.cppPvt,argument,lastRequest)
        return True

    def waitResponse(self, timeout=5.0) :
        """Wait for the request to finish

        timeOut The timeout in seconds

        """
        return channelRPCPy._waitResponse(self.cppPvt, timeout)

    def getMessage(self) :
        """Get a message for a connect or request failure"""
        return channelRPCPy._getMessage(self.cppPvt)
