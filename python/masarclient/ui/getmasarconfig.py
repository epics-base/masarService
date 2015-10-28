#!/usr/bin/env python2.7

'''Get masar configuration information from a server.
 
Created on Apr 28, 2014

@author: shengb
'''

import os
import platform
import ConfigParser

def getmasarconfig():
    '''Get configuration file for MASAR service which enables service integration for Olog and channel finder for example.

    [LDAP]
    url = ldap://your.own.ldap.server:port
    info = username==uid=%s,ou=people,dc=yourdomain,dc=yourdomain,dc=yourdomain

    [Olog]
    url = https://your.own.olog.server:port/[Olog Server Resource]
    logbookname = logbook1,logbook1
    logbook4invisible = logbook3

    [ChannelFinder]
    url = http://your.own.channelfinder.server:port/[ChannelFinder Server Resource]

    '''
    system = platform.system()

    config = ConfigParser.ConfigParser()
    if system == 'Windows':
        raise RuntimeError("Does not support Windows platform yet.")

    try:
        # try system config
        config.readfp(open('/etc/masar/masar.cfg'))
    except IOError:
        pass
    try:
        # whether current working directory or user home directory
        config.read([os.path.join(os.path.dirname(__file__), 'masar.cfg'), 
                    'masar.cfg', 
                    os.path.expanduser('~/.masar.cfg')])
    except IOError:
        pass

    masarconfig = {}
    sections = config.sections()

    for section in sections:
        masarconfig[section] = dict(config.items(section))

    return masarconfig

if __name__ == "__main__":
    print getmasarconfig()
