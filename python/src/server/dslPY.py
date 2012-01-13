# dsl.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# This code is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author Marty Kraimer 2011.11

import re

import pymasar

class DSL(object) :
    """Implements an IRMIS request."""
    def __init__(self) :
        """constructor"""
        self.__servicename = 'masar'
        
    def __del__(self) :
        """destructor"""
        print ('close SQLite3 connection.')
#        pymasar.utils.close(conn)
    
    def dispatch(self, fname, fargs):
        actions = (("retrieveServiceConfigProps", self.retrieveServiceConfigProps),
                   ("retrieveServiceConfigs", self.retrieveServiceConfigs),
                   ("retrieveServiceEvents", self.retrieveServiceEvents),
                   ("retrieveMasar", self.retrieveMasar),
                   ("saveMasar", self.saveMasar))
        for (params, func) in actions:
            if re.match(params, fname):
                return func(fargs)

    def request(self, argument):
        """issue request"""
        func = argument['function']
        result = self.dispatch(func, argument)
        return (result, )

    def toString(self) :
        """Return a string that shows the message and severity"""
#        return Alarm.alarmSeverityNames[self.severity] + " " + self.message;
        pass

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
#        print (name, service, config)
        conn = pymasar.utils.connect()
        result = pymasar.service.retrieveServiceConfigProps(conn, propname=name, servicename=service, configname=config)
        pymasar.utils.close(conn)
        return result
#        return 'retrieveServiceConfigProps'
    
    def retrieveServiceConfigs(self, params):
        key = ['servicename', 'configname', 'configversion', 'system']
        service, config, version, system = self._parseParams(params, key)
        if not service:
            service = self.__servicename
#        print (service, config, version, system)
        conn = pymasar.utils.connect()
        result = pymasar.service.retrieveServiceConfigs(conn, servicename=service, configname=config, configversion=version, system=system)
        pymasar.utils.close(conn)
        return result
#        return 'retrieveServiceConfigs'
    
    def retrieveServiceEvents(self, params):
        key = ['configid', 'start', 'end', 'comment']
        cid, start, end, comment = self._parseParams(params, key)
#        print (cid, start, end, comment)
        conn = pymasar.utils.connect()
        result = pymasar.service.retrieveServiceEvents(conn, configid=cid,start=start, end=end, comment=comment)
        pymasar.utils.close(conn)
        return result
#        return 'retrieveServiceEvents'

    def retrieveMasar(self, params): 
        key = ['eventid', 'start', 'end', 'comment']
        eid, start, end, comment = self._parseParams(params, key)
#        print (eid, start, end, comment)
        conn = pymasar.utils.connect()
        result = pymasar.masardata.retrieveMasar(conn, eventid=eid,start=start,end=end,comment=comment)
        pymasar.utils.close(conn)

        return result
#        return 'retrieveMasar'
    
    def saveMasar(self, params):
        key = ['data','servicename','configname','comment']

        data, service, config, comment = self._parseParams(params, key)
        if not service:
            service = self.__servicename
        
#        print (data, service, config, comment)
#        conn = pymasar.utils.connect()
        #result = pymasar.masardata.saveMasar(conn, data, servicename=service, configname=config, comment=comment)
#        pymasar.utils.close(conn)
#        return result
        return 'saveMasar'
