'''
Created on 1 Feb 2018

@author: georgweiss
'''
import abc

import logging, time
from calendar import timegm
from numpy.f2py.crackfortran import parameterpattern
_log = logging.getLogger(__name__)

try:
    from itertools import izip_longest, izip, repeat
except ImportError:
    from itertools import (zip_longest as izip_longest, repeat)
    izip = zip
from operator import itemgetter

import numpy

from p4p.rpc import RemoteError, rpc
from p4p.nt import NTScalar, NTMultiChannel, NTTable
from p4p.wrapper import Value

multiType = NTMultiChannel.buildType('av', extra=[
    ('dbrType', 'ai'),
    ('readonly', 'a?'),
    ('groupName', 'as'),
    ('tags', 'as'),
])

configType = NTTable([
    ('channelName', 's'),
    ('readonly', '?'),
    ('groupName', 's'),
    ('tags', 's'),
])


configTable = NTTable([
        ('config_idx','i'),
        ('config_name','s'),
        ('config_desc','s'),
        ('config_create_date','s'),
        ('config_version','s'),
        ('status','s'),
        ('system', 's'),
    ])


def normtime(tstr):
    'Normalize user provided time string'
    T = time.strptime(tstr, '%Y-%m-%d %H:%M:%S')
    return time.strftime('%Y-%m-%d %H:%M:%S', T)

def timestr2tuple(tstr):
    'time string to PVD time tuple'
    T = time.strptime(tstr, '%Y-%m-%d %H:%M:%S')
    S, NS = divmod(timegm(T), 1.0)
    return int(S), int(NS*1e9)


class ServiceBase():
    
    __metaclass__ = abc.ABCMeta
       
    
    def __init__(self, conn, gather=None, sim=False):
        self.conn = conn
        self.gather = gather

        if not sim:
            # current time string (UTC)
            self.now = lambda: time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        else:
            # posix time 1485639808
            self.simtime = (2017, 1, 28, 21, 43, 28, 5, 28, 0)
            self.now = lambda self=self: time.strftime('%Y-%m-%d %H:%M:%S', self.simtime)
            
   

    def _getConfig(self, C):
        # expect previous 'select' with: id, name, created, active, next, desc, system
        ret = []
        for id, name, created, active, next, desc, system in C.fetchall():
            ret.append({
                'config_idx':id,
                'config_name':name,
                'config_create_date':created,
                'config_desc':desc,
                'config_version':u'0',
                'status': 'active' if next is None and active!=0 else 'inactive',
                'system': system or '',
            })
        return ret
    
    @abc.abstractmethod
    def encodeValue(self, V):
        return
    
    @abc.abstractmethod
    def decodeValue(self, V):
        return
    
    @abc.abstractmethod
    def storeServiceConfig(self, configname=None, oldidx=None, desc=None, config=None, system=None):
        return
        
    @abc.abstractmethod
    def loadServiceConfig(self, configid=None):
        return
        
    @abc.abstractmethod
    def retrieveServiceConfigs(self, servicename=None, configname=None, configversion=None, system=None, eventid=None, status=None):
        return
        
    
    @abc.abstractmethod
    def retrieveServiceConfigProps(self, propname=None, servicename=None, configname=None):
        return
    
    @abc.abstractmethod
    def retrieveServiceEvents(self, configid=None, start=None, end=None, comment=None, user=None, eventid=None):
        return
        
    @abc.abstractmethod
    def retrieveSnapshot(self, eventid=None, start=None, end=None, comment=None):
        return
            
    @abc.abstractmethod
    def saveSnapshot(self, servicename=None, configname=None, comment=None, user=None, desc=None):
        return
   
    @abc.abstractmethod
    def updateSnapshotEvent(self, eventid=None, configname=None, user=None, desc=None):
        return
        
    @rpc(multiType)
    def getCurrentValue(self, names=None):
        return self.gather(list(names))

    @rpc(multiType)
    def getLiveMachine(self, **kws):
        return self.gather(list(kws.values()))

    # for troubleshooting

    @rpc(NTTable.buildType([
        ('config_idx','ai'),
        ('config_name','as'),
        ('config_desc','as'),
        ('config_create_date','as'),
        ('config_version','as'),
        ('status','as'),
    ]))
    def storeTestConfig(self, **kws):
        conf = Value(NTTable.buildType([
            ('channelName', 'as'),
            ('readonly', 'a?'),
            ('groupName', 'as'),
            ('tags', 'as'),
        ]), {
            'labels': ['channelName', 'readonly', 'groupName', 'tags'],
            'value': {
                'channelName': ['pv:f64:1', 'pv:i32:2', 'pv:str:3', 'pv:bad:4'],
                'readonly':    [False,      False,      False,      False],
                'groupName':   ['A',        '',         '',         ''],
                'tags':        ['',         'a, b',     '',         ''],
            },
        })

        return self.storeServiceConfig(config=conf, **kws)

    @rpc(NTScalar.buildType('s'))
    def dumpDB(self):
        return {
            'value': '\n'.join(self.conn.iterdump())
        }

    @rpc(NTTable.buildType([
        ('config_idx','i'),
        ('config_name','s'),
        ('config_desc','s'),
        ('config_create_date','s'),
        ('config_version','s'),
        ('status','s'),
    ]))
    
    def storeServiceConfigManual(self, pvs=None, ros=None, groups=None, tags=None, **kws):
        if pvs is None:
            raise RemoteError("Missing required pvs=")

        pvs = pvs.split(u',')
        N = len(pvs)
        if N==0:
            raise RemoteError("No PVs")
        _log.debug("Load config %s", pvs)

        def mangle(L, P):
            L = (L or u'').split(u',')
            if len(L)<N:
                L = L + [P]*(N-len(L))
            return L

        ros, groups, tags = mangle(ros, False), mangle(groups, u''), mangle(tags, u'')

        config = Value(configType.type, {
            'labels': configType.labels,
            'value': {
            'channelName': pvs,
            'readonly': numpy.asarray(ros, dtype=numpy.bool),
            'groupName': groups,
            'tags': tags,
            },
        })
        _log.info("Load config %s", config.tolist())

        return self.storeServiceConfig(config=config, **kws)

   
        