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
        self.conn = pymasar.utils.connect()
        
    def __del__(self) :
        """destructor"""
        print ('close SQLite3 connection.')
        pymasar.utils.close(self.conn)
    
    def dispatch(self, fname, fargs):
        actions = (("retrieveServiceConfigProps", self.retrieveServiceConfigProps),
                   ("retrieveServiceConfigs", self.retrieveServiceConfigs),
                   ("retrieveServiceEvents", self.retrieveServiceEvents),
                   ("retrieveMasar", self.retrieveMasar),
                   ("saveMasar", self.saveMasar))
        for (params, func) in actions:
            if re.match(params, fname):
                return func(fargs)

    def request(self, func, argument) :
        """issue request"""
#        print ("func: ", func)
        result = self.dispatch(func, argument)
        return result
    
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
        print pymasar.service.retrieveServiceConfigProps(self.conn, propname=name, servicename=service, configname=config)

        return 'retrieveServiceConfigProps'
    
    def retrieveServiceConfigs(self, params):
        key = ['servicename', 'configname', 'configversion', 'system']
        service, config, version, system = self._parseParams(params, key)
        if not service:
            service = self.__servicename
#        print (service, config, version, system)
        print pymasar.service.retrieveServiceConfigs(self.conn, servicename=service, configname=config, configversion=version, system=system)

        return 'retrieveServiceConfigs'
    
    def retrieveServiceEvents(self, params):
        key = ['configid', 'start', 'end', 'comment']
        cid, start, end, comment = self._parseParams(params, key)
#        print (cid, start, end, comment)
        print pymasar.service.retrieveServiceEvents(self.conn, configid=cid,start=start, end=end, comment=comment)
        
        return 'retrieveServiceEvents'

    def retrieveMasar(self, params): 
        key = ['eventid', 'start', 'end', 'comment']
        eid, start, end, comment = self._parseParams(params, key)
#        print (eid, start, end, comment)
        print pymasar.masardata.retrieveMasar(self.conn, eventid=eid,start=start,end=end,comment=comment)

        return 'retrieveMasar'
    
    def saveMasar(self, params):
        key = ['data','servicename','configname','comment']

        data, service, config, comment = self._parseParams(params, key)
        if not service:
            service = self.__servicename
        
#        print (data, service, config, comment)
        #pymasar.masardata.saveMasar(self.conn, data, servicename=service, configname=config, comment=comment)
        return 'saveMasar'
