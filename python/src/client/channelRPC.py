# channelRPC.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author Marty Kraimer 2011.07

import channelRPCPy

class ChannelRPC(object) :
    """Create a ChannelRPC

    Typical usage is:
    #Following done once
    channelRPC = ChannelRPC(channelName,request)
    status = channelRPC.connect(timeOut)
    if not status :
        #take some action
    status = channelRPC.waitConnect(2.0)
    if not status.:
        #take some action
    
    #Following done for each channelRPC request
    status = channelRPC.sendRequest(argument,lastRequest)
    if not  :
        #take some action
    status = channelRPC.waitRequest()
    if not :
        #take some action
    """
    def __init__(self,channelName,request) :
        """Constructor

        channelName The pvName of the channelRPC record for the service.
        request  A string to turn into a pvRequest"""
        self.cppPvt = channelRPCPy._init(self,channelName,request)
    def __del__(self) :
        """Destructor Destroy the connection to the server"""
        channelRPCPy._destroy(self.cppPvt)
    def connect(self,timeout) :
        """Connect to the channelRPC service"""
        result = channelRPCPy._connect(self.cppPvt,timeout);
        if result==None :
             return True
        return False
    def issueConnect(self) :
        """Connect to the channelRPC service"""
        channelRPCPy._issueConnect(self.cppPvt);
        return
    def waitConnect(self,timeout) :
        """Wait until connect or timeout

        timeOut The timeout in seconds

        returns Status"""
        result = channelRPCPy._waitConnect(self.cppPvt,timeout);
        if result==None :
             return True
        return False
    def request(self,argument,lastRequest) :
        """Send a channelRPC request

        argument     An object that has a method that returns a PyCapsule
                     that returns the address of  a PVStructure::shared_pointer.
        lastRequest  Either True or False"""
        result = channelRPCPy._request(self.cppPvt,argument,lastRequest)
        if result==None :
             return True
        return False
    def issueRequest(self,argument,lastRequest) :
        """Send a channelRPC request

        argument     An object that has a method that returns a PyCapsule
                     that returns the address of  a PVStructure::shared_pointer.
        lastRequest  Either True or False"""
        channelRPCPy._issueRequest(self.cppPvt,argument,lastRequest)
        return True
    def waitRequest(self) :
        """Wait for the request to finish"""
        result = channelRPCPy._waitRequest(self.cppPvt)
        if result==None :
             return True
        return False
    def getMessage(self) :
        return channelRPCPy._getMessage(self.cppPvt);
    def getResponse(self) :
        """Get the response from the last sendRequest"""
        return channelRPCPy._getResponse(self.cppPvt)
