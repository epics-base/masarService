# nttable.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# EPICS pvService is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author Marty Kraimer 2011.07

import nttablePy

class NTTable(object) :
    """Create a NTTable

    """
    def __init__(self,capsule) :
        """Constructor

        capsule Must be a pvStructure capsule"""
        self.cppPvt = nttablePy._init(self,capsule)
    def __del__(self) :
        """Destructor Destroy the connection to the server"""
        nttablePy._destroy(self.cppPvt)
    def __str__(self) :
        return nttablePy.__str__(self.cppPvt);
