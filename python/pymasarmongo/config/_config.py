'''
Created on Jul 28, 2014

@author: shengb
'''
import os.path
import ConfigParser


def __loadmasarconfig():
    cf = ConfigParser.SafeConfigParser()
    read = cf.read([
        os.path.expanduser('~/.masarservice.conf'),
        '/etc/masarservice.conf',
        'masarservice.conf',
        "%s/masarservice.conf" % os.path.abspath(os.path.dirname(__file__))
    ])
    print 'Read config files', read
    return cf


masarconfig = __loadmasarconfig()
