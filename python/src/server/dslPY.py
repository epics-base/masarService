# dsl.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# This code is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author: Guobao Shen   2012.01
#         Marty Kraimer 2011.11

import re

from nttable import NTTable
import pymasar

class DSL(object) :
    """Implements an IRMIS request."""
    def __init__(self) :
        """constructor"""
        self.__servicename = 'masar'
        #define    DBF_STRING  0
        #define    DBF_INT     1
        #define    DBF_SHORT   1
        #define    DBF_FLOAT   2
        #define    DBF_ENUM    3
        #define    DBF_CHAR    4
        #define    DBF_LONG    5
        #define    DBF_DOUBLE  6
        self.epicsInt    = [1, 4, 5]
        self.epicsString = [0, 3]
        self.epicsDouble = [2, 6]
        self.epicsNoAccess = [7]
        
    def __del__(self) :
        """destructor"""
        print ('close SQLite3 connection.')
#        pymasar.utils.close(conn)
    
    def dispatch(self, fname, fargs):
        actions = (("retrieveServiceConfigProps", self.retrieveServiceConfigProps),
                   ("retrieveServiceConfigs", self.retrieveServiceConfigs),
                   ("retrieveServiceEvents", self.retrieveServiceEvents),
                   ("retrieveSnapshot", self.retrieveSnapshot),
                   ("saveSnapshot", self.saveSnapshot),
                   ('updateSnapshotEvent', self.updateSnapshotEvent))
        for (params, func) in actions:
            if re.match(params, fname):
                return func(fargs)

    def request(self, *argument):
        """issue request"""
        if len(argument) == 1:
            argument = argument[0]
            func = argument['function']
            result = self.dispatch(func, argument)
        else:
            func = argument[1]
            func = func['function']
            result = self.dispatch(func, argument)
        return (result, )

    def _parseParams(self, params, key):
        results = []
        if len(key) == 0:
            return results
        for k in key:
            try:
                results.append(params[k])
            except:
                results.append(None)
        return results
    
    def retrieveServiceConfigProps(self, params):
        key = ['propname', 'servicename', 'configname']
        name, service, config = self._parseParams(params, key)
        if not service:
            service = self.__servicename
        conn = pymasar.utils.connect()
        result = pymasar.service.retrieveServiceConfigProps(conn, propname=name, servicename=service, configname=config)
        pymasar.utils.close(conn)
        return result
    
    def retrieveServiceConfigs(self, params):
        key = ['servicename', 'configname', 'configversion', 'system']
        service, config, version, system = self._parseParams(params, key)
        if not service:
            service = self.__servicename
        if system == 'all':
            system = None
        conn = pymasar.utils.connect()
        result = pymasar.service.retrieveServiceConfigs(conn, servicename=service, configname=config, configversion=version, system=system)
        pymasar.utils.close(conn)
        return result
    
    def retrieveServiceEvents(self, params):
        key = ['configid', 'start', 'end', 'comment', 'user']
        cid, start, end, comment, user = self._parseParams(params, key)
        conn = pymasar.utils.connect()
        result = pymasar.service.retrieveServiceEvents(conn, configid=cid,start=start, end=end, comment=comment, user=user)
        pymasar.utils.close(conn)
        return result

    def retrieveSnapshot(self, params): 
        key = ['eventid', 'start', 'end', 'comment']
        eid, start, end, comment = self._parseParams(params, key)
        conn = pymasar.utils.connect()
        result = pymasar.masardata.retrieveSnapshot(conn, eventid=eid,start=start,end=end,comment=comment)
        pymasar.utils.close(conn)
        return result
    
    def saveSnapshot(self, params):
        key = ['servicename','configname','comment']
        service, config, comment = self._parseParams(params[1], key)
        if not service:
            service = self.__servicename
        
        rawdata = params[0]
        nttable = NTTable(rawdata)
        numberValueCount = nttable.getNumberValues()
        
        # values format: the value is raw data from IOC 
        # [(channel name,), (string value,),(double value,),(long value,),(dbr type),(is connected),
        #  (second past epoch,),(nano seconds,),(time stamp tag,),(alarm severity,),(alarm status,),(alarm message,), (is_array), (array_value)]
        values = []

        # data format: the data is prepared to save into rdb
        # rawdata format
        # [('channel name', 'string value', 'double value', 'long value', 'dbr type', 'is connected', 
        #  'seconds past epoch', 'nano seconds', 'time stamp tag', 'alarm severity', 'alarm status', 'alarm message', 'is_array', 'array_value'),
        #  ...
        # ]
        datas = []
        dataLen = len(nttable.getValue(0))
        
        dbrtype = nttable.getValue(4)
        is_array = nttable.getValue(12)
        # get IOC raw data
        for i in range(numberValueCount):
            if i == 13:
                raw_array_value = nttable.getValue(i)
                array_value = []
                for j in range(len(is_array)):
                    if dbrtype[j] in self.epicsDouble:
                        array_value.append(raw_array_value[j][1])
                    elif dbrtype[j] in self.epicsInt:
                        array_value.append(raw_array_value[j][2])
                    elif dbrtype[j] in self.epicsString:
                        array_value.append(raw_array_value[j][0])
                    elif dbrtype[j] in self.epicsNoAccess:
                        array_value.append(raw_array_value[j][0])
                values.append(array_value)
            else:
                values.append(list(nttable.getValue(i)))
        # problem when a negative value is passed from C++
        #define DBF_FLOAT   2
        #define DBF_DOUBLE  6
        for i in range(len(values[2])):
            if values[4][i] in [2, 6] and values[2][i] < 0:
                values[3][i] = int(values[2][i])

        # initialize data for rdb
        for j in range(dataLen):
            datas.append(())
        
        # convert data format values ==> datas
        for i in range(numberValueCount):
            for j in range(dataLen):
                datas[j] = datas[j] + (values[i][j],)
        
        # save into database
        try:
            conn = pymasar.utils.connect()
            eid, result = pymasar.masardata.saveSnapshot(conn, datas, servicename=service, configname=config, comment=comment)
            pymasar.utils.save(conn)
            pymasar.utils.close(conn)
            result.insert(0, eid)
            return result
        except:
            # keep the same format with a normal operation
            return [-1]
    
    def retrieveChannelNames(self, params):
        #key = ['servicename','configname','comment']
        key = ['servicename','configname']
        service, config = self._parseParams(params, key)
        if not service:
            service = self.__servicename
        
        conn = pymasar.utils.connect()
        result = pymasar.service.retrieveServiceConfigPVs(conn, config, servicename=service)
        pymasar.utils.close(conn)
        return result
    
    def updateSnapshotEvent(self, params):
        #key = ['eventid', 'user', 'desc', 'configname']
        key = ['eventid', 'user', 'desc']
        eid, user, desc = self._parseParams(params, key)
        try:
            conn = pymasar.utils.connect()
            result = pymasar.service.serviceevent.updateServiceEvent(conn, int(eid), comment=str(desc), approval=True, username=str(user))
            pymasar.utils.save(conn)
            pymasar.utils.close(conn)
            if result:
                return [0, eid]
            else:
                return [-1, eid]
        except:
            return [-2, eid]
