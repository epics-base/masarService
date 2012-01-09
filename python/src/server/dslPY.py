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
        pass
        
    def __del__(self) :
        """destructor"""
        pass
    
    def dispatch(self, fname, **fargs):
        actions = (("retrieveServiceConfigProps", self.retrieveServiceConfigProps),
                   ("retrieveServiceConfigs", self.retrieveServiceConfigs),
                   ("retrieveServiceEvents", self.retrieveServiceEvents),
                   ("retrieveMasar", self.retrieveMasar),
                   ("saveMasar", self.saveMasar))
        for (params, func) in actions:
            if re.match(params, fname):
                return func(**fargs)

    def request(self, argument) :
        """issue request"""
        print "argument: " + argument
        result = self.dispatch(argument, args = argument)
        return result
    
    def toString(self) :
        """Return a string that shows the message and severity"""
#        return Alarm.alarmSeverityNames[self.severity] + " " + self.message;
        pass

    def retrieveServiceConfigProps(self, **params):
        print (help(pymasar.service.retrieveServiceConfigProps))
        return 'retrieveServiceConfigProps'
    
    def retrieveServiceConfigs(self, **params):
#        system=system
        print (help(pymasar.service.retrieveServiceConfigs))
        return 'retrieveServiceConfigs'
    def retrieveServiceEvents(self, **params):
#        configid=cid, start=start, end=end
        print (help(pymasar.service.retrieveServiceEvents))
        return 'retrieveServiceEvents'
    def retrieveMasar(self, **params): 
#        eventid=eventid
        print (help(pymasar.masardata.retrieveMasar))
        return 'retrieveMasar'
    def saveMasar(self, **params):
#        data, servicename=None, configname=None, comment=None
#        data has the format: [(pv_name, value, status, severity, ioc_timestamp, ioc_timestamp_nano)]
        print (help(pymasar.masardata.saveMasar))
        return 'saveMasar'
