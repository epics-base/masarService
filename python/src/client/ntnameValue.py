# ntnameValue.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author Marty Kraimer 2011.07

import ntnameValuePy

class NTNameValue(object) :
    """Create a NTNameValue

    """
    def __init__(self,function,dictionary) :
        """Constructor

        channelName The pvName of the ntnameValue record for the service.
        request  A string to turn into a pvRequest"""
        self.cppPvt = ntnameValuePy._init(self,function,dictionary)
    def __del__(self) :
        """Destructor Destroy the connection to the server"""
        ntnameValuePy._destroy(self.cppPvt)
    def __str__(self) :
        return ntnameValuePy.__str__(self.cppPvt)
    def getNTNameValue(self) :
        return ntnameValuePy._getNTNameValuePy(self.cppPvt);
