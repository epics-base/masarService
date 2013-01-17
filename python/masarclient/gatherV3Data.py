# gatherV3Data.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author : Guobao Shen   2012.01
#          Marty Kraimer 2011.07

import gatherV3DataPy
from nttable import NTTable as NTTable

class GatherV3Data(object) :
    """Create a GatherV3Data

    Typical usage is:

    Following done once
    gatherV3Data = GatherV3Data(channelNames)
    result = gatherV3Data.connect(timeOut)
    if not result :
        #take some action

    Following done for each gatherV3Data get
    result = gatherV3Data.get(argument,lastRequest)
    if not result :
        #take some action
    """
    def __init__(self,channelNames) :
        """Constructor

        channelNames A sequence of V3 channel names."""
        self.cppPvt = gatherV3DataPy._init(channelNames)
        self.ntTable = None
    def __del__(self) :
        """Destructor Destroys the connection to the server"""
        gatherV3DataPy._destroy(self.cppPvt)
        self.ntTable = None
    def connect(self,timeout) :
        """Connect to the V3 channels

        timeout is in seconds.
        returns (false,true) If (not connected, is connected) to all channels.
        If not connected to all channels getMessage can be called to find out why.
        isConnected shows the status of each channel.
        Connect can not be called again until disconnect is called. 
        """
        result = gatherV3DataPy._connect(self.cppPvt,timeout);
        if result==None :
            return True
        return False
    def disconnect(self) :
        """Disconnect from the V3 channels"""
        result = gatherV3DataPy._disconnect(self.cppPvt);
        return result
    def get(self) :
        """get the current values of the V3 channels.

        returns true if (all, not all) gets were successful.
        If false getMessage can be called to get the reason.
        If any channel is disconnected then false is returned.
        The data is in the NTTable returned by getNTTable.
        """
        return gatherV3DataPy._get(self.cppPvt)
    def put(self) :
        """put new values to the V3 channels.

        returns true if (all, not all) gets were successful.
        If false getMessage can be called to get the reason.
        If any channel is disconnected then false is returned.
        The data must be put into the NTTable returned by getNTTable.
        """
        return gatherV3DataPy._put(self.cppPvt)
    def getMessage(self) :
        """Get a message for a connect or request failure"""
        return gatherV3DataPy._getMessage(self.cppPvt);
    def getNTTable(self) :
        """The data is saved as an NTTable with alarm and timeStamp. Get it.
        returns the NTTable"""
        if self.ntTable != None :
            return self.ntTable
        self.xxx = gatherV3DataPy._getNTTable(self.cppPvt)
        self.ntTable = NTTable(self.xxx,True)
        return self.ntTable
