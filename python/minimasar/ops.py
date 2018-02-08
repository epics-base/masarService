
import logging, zlib, numpy

import ops_base

_log = logging.getLogger(__name__)

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    from itertools import izip_longest, izip, repeat
except ImportError:
    from itertools import (zip_longest as izip_longest, repeat)
    izip = zip
from operator import itemgetter


from p4p.rpc import RemoteError, rpc
from p4p.nt import NTScalar, NTTable

from types import NoneType
from ops_base import ServiceBase

class Service(ServiceBase):
    
    parameterPlaceholder = "?"
    userColumnName = 'user'
    descriptionColumnName = 'desc'
    
    def __init__(self, conn, gather=None, sim=False):
        
        super(Service, self).__init__(conn, gather, sim)
        
    
    def encodeValue(self, V):
        """Mangle python type for storage in event_pv.value
        """
        if isinstance(V, (int, long, float, unicode, bytes, NoneType)):
            return V # store directly
        elif isinstance(V, (list, tuple, numpy.ndarray)):
            return buffer(zlib.compress(pickle.dumps(numpy.asarray(V))))
        else:
            _log.exception("Error encoding %s", V)
            raise ValueError("Can't encode type %s"%type(V))

    def decodeValue(self, S):
        if isinstance(S, buffer):
            return pickle.loads(zlib.decompress(S))
        elif isinstance(S, unicode):
            return S
        else:
            return float(S)
        
    @rpc(ops_base.configType)     
    def loadServiceConfig(self, configid=None):
        configid = int(configid)
        with self.conn as conn:
            C = conn.cursor()

            R = C.execute('select id from config where id=?;', (configid,)).fetchone()
            if R is None:
                raise RemoteError("Unknown configid %s"%configid)

            C.execute('select name as channelName, tags, groupName, readonly from config_pv where config=?;', (int(configid),))
            _log.debug("Fetch configuration %s", configid)
            
            tmp = C.fetchall()
            print tmp
            
            return tmp
        
    @rpc(ops_base.configTable)
    def retrieveServiceConfigs(self, servicename=None, configname=None, configversion=None, system=None, eventid=None, status=None):
        if servicename not in (None, u'masar'):
            _log.warning("Service names not supported")
            return []
        if status not in (None, u'', u'active', u'inactive'):
            _log.warning("Request matching unknown status %s", status)
            return []
        with self.conn as conn:
            C = conn.cursor()

            cond = []
            vals = []

            _log.debug("retrieveServiceConfigs() configname=%s configverson=%s system=%s",
                       configname, configversion, system)

            if eventid not in (None, u'', u'*', 0):
                C.execute('select config from event where id=' + self.parameterPlaceholder, (int(eventid),))
                idx = C.fetchone()['config']
                cond.append('id=' + self.parameterPlaceholder)
                vals.append(idx)

            else:
                if status==u'active':
                    cond.append('next is NULL')
                elif status==u'inactive':
                    cond.append('next is not NULL')

                if configname not in (None, u'', u'*', u'all'):
                    cond.append('name glob ?')
                    vals.append(configname)

                if system not in (None, u'', u'*', u'all'):
                    cond.append('system glob ?')
                    vals.append(system)

            if len(cond)>0:
                cond = 'where '+(', '.join(cond))
            else:
                cond = ''

            _log.debug('retrieveServiceConfigs() w/ %s %s', cond, vals)

            C.execute("""select id, name, created, active, next, desc, system
                                from config
                                %s;
                """%cond, vals)
            return self._getConfig(C)

    @rpc(NTTable([
        ('config_prop_id','i'),
        ('config_idx','i'),
        ('system_key','s'),
        ('system_val','s'),
    ]))
    def retrieveServiceConfigProps(self, propname=None, servicename=None, configname=None):
        if servicename not in (None, '*', 'masar') or propname not in (None, '*', 'system'):
            _log.warning("Service names or non 'system' prop names not supported (%s, %s)", servicename, propname)
            return []
        with self.conn as conn:
            C = conn.cursor()

            cond = []
            vals = []
            if configname not in (None, u'', u'*'):
                cond.append('name glob ?')
                vals.append(configname)

            if len(cond)>0:
                cond = 'where '+(', '.join(cond))
            else:
                cond = ''

            _log.debug("retrieveServiceConfigProps() %s %s", cond, vals)

            C.execute('select id, system from config %s'%cond, vals)
            R = []
            for id, system in C.fetchall():
                if system is None:
                    continue
                R.append({'config_prop_id':1,
                        'config_idx':id,
                        'system_key':'system',
                        'system_val':system,
                        })
            return R
    
    @rpc(ops_base.configTable)
    def storeServiceConfig(self, configname=None, oldidx=None, desc=None, config=None, system=None):
        with self.conn as conn:
            C = conn.cursor()

            _log.debug("storeServiceConfig() %s(%s)", configname, oldidx)
            
            C.execute('insert into config(name, desc, created, system) values (?,?,?,?);', (configname, desc, self.now(), system))
            newidx = C.lastrowid
            
            if oldidx is not None:
                # update existing row only if it was previously active
                C.execute('update config set next=? where id=? and next is NULL', (newidx, int(oldidx)))

            if C.execute('select count(*) from config where name=? and next is NULL and active=1', (configname,)).fetchone()[0]!=1:
                # rollback will undo our insert
                raise RemoteError("Provided configname and oldidx ('%s' and %s) are not consistent"%(configname, oldidx))

            for name, ro, group, tags in izip_longest(
                        config.value.channelName,
                        config.get('value.readonly', []),
                        config.get('value.groupName', []),
                        config.get('value.tags', []),
                    ):

                C.execute('insert into config_pv(config, name, readonly, groupName, tags) VALUES (?,?,?,?,?);',
                        (newidx, name, int(ro) or 0, group or '', tags or ''))

            C.execute('select id, name, created, active, next, desc, system from config where id=?;', (newidx,))

            _log.info("Store configuration %s as %s (old %s)", configname, newidx, oldidx)

            return self._getConfig(C)
    

    @rpc(ops_base.configTable)
    def modifyServiceConfig(self, configid=None, status=None):
        configid = int(configid)
        if status not in (None, 'active', 'inactive'):
            raise RemoteError("Unsupported status '%s'"%status)
        with self.conn as conn:
            C = conn.cursor()

            R = C.execute('select active, next from config where id=?', (int(configid),)).fetchone()
            if R is None:
                raise RemoteError("Unknown configid %s"%configid)
            if R['next'] is not None:
                raise RemoteError("Can't modify superceeded configuration")

            cond = []
            vals = [configid]

            if status=='active':
                cond.append('active=1')
            elif status=='inactive':
                cond.append('active=0')

            if len(cond)>0:
                cond = ', '.join(cond)

                C.execute('update config set %s where id=? and next is NULL'%cond, vals)

            C.execute("""select id, name, created, active, next, desc, system
                                from config
                                where id=?;
                """, (configid,))

            return self._getConfig(C)


   
    @rpc(NTTable([
        ('event_id','i'),
        ('config_id','i'),
        ('comments','s'),
        ('event_time','s'),
        ('user_name','s'),
    ]))
    def retrieveServiceEvents(self, configid=None, start=None, end=None, comment=None, user=None, eventid=None):
        with self.conn as conn:
            C = conn.cursor()

            cond = ['user is not NULL']
            vals = []
            
            if user not in (None, u'', u'*'):
                cond.append('user glob ?')
                vals.append(user)

            if comment not in (None, u'', u'*'):
                cond.append('comment glob ?')
                vals.append(comment)

            if configid not in (None, u'*'):
                cond.append('config=?')
                vals.append(int(configid))

            # HACK instead of using julianday(), use lexial comparison,
            # which should produce the same result as we always store time
            # as "YYYY-MM-DD HH:MM:SS"
            if start not in (None, u''):
                cond.append("event_time>=?")
                vals.append(ops_base.normtime(start))

            if end not in (None, u''):
                cond.append("event_time<?")
                vals.append(ops_base.normtime(end))

            if len(cond)>0:
                cond = 'where '+(' and  '.join(cond))
            else:
                cond = ''

            _log.debug("retrieveServiceEvents() %s %s", cond, vals)

            C.execute("""select id as event_id,
                                config as config_id,
                                comment as comments,
                                created as event_time,
                                user as user_name
                                from event
                                %s
                                order by config_id, event_time
                """%cond, vals)
            return C.fetchall()
         

    @rpc(ops_base.multiType)
    def retrieveSnapshot(self, eventid=None, start=None, end=None, comment=None):
        # start, end, and comment ignored
        eventid = int(eventid)
        with self.conn as conn:
            C = conn.cursor()

            _log.debug("retrieveSnapshot() %d", eventid)

            C.execute('select created from event where id=?', (eventid,))
            S, NS = ops_base.timestr2tuple(C.fetchone()[0])

            C.execute("""select name, tags, groupName, readonly, dtype, severity, status, time, timens,
                        value
                        from event_pv inner join config_pv on event_pv.pv = config_pv.id
                        where event_pv.event = ?
                        """, (eventid,))
            L = C.fetchall()

        sevr = list(map(itemgetter('severity'), L))

        def unpack(I):
            try:
                return self.decodeValue(I['value'])
            except:
                raise ValueError("Error decoding %s", type(I['value']))

        return {
            'channelName': list(map(itemgetter('name'), L)),
            'value': list(map(unpack, L)),
            'severity': sevr,
            'isConnected': list(map(lambda S: S<=3, sevr)),
            'status': list(map(itemgetter('status'), L)),
            'secondsPastEpoch': list(map(itemgetter('time'), L)),
            'nanoseconds': list(map(itemgetter('timens'), L)),
            'dbrType': list(map(itemgetter('dtype'), L)),
            'groupName': list(map(itemgetter('groupName'), L)),
            'readonly': list(map(itemgetter('readonly'), L)),
            'tags': list(map(itemgetter('tags'), L)),
            'timeStamp': {
                'secondsPastEpoch':S,
                'nanoseconds':NS,
                'userTag': eventid
            },
            'userTag': [0]*len(L),
            'message': [u'']*len(L),
        }

    @rpc(ops_base.multiType)
    def saveSnapshot(self, servicename=None, configname=None, comment=None, user=None, desc=None):
        if servicename not in (None, 'masar'):
            raise RemoteError("Bad servicename")
        with self.conn as conn:
            C = conn.cursor()

            C.execute('select id from config where name=? and next is NULL and active=1;', (configname,))
            cid = C.fetchone()
            if cid is None:
                raise RemoteError("Unknown config '%s'"%configname)
            cid = cid[0]
            _log.debug("saveSnapshot() for '%s'(%s)", configname, cid)

            C.execute('select id, name, tags, groupName, readonly from config_pv where config=?;', (cid,))
            config = C.fetchall()

            pvid  = list(map(itemgetter('id'), config))
            names = list(map(itemgetter('name'), config))

            ret = self.gather(names)
            _log.debug("Gather complete")

            C.execute('insert into event(config, user, comment, created) values (?,?,?,?);', (cid, user, desc, self.now()))
            eid = C.lastrowid
            _log.debug("Create event %s", eid)

            C.executemany("""insert into event_pv(event, pv, dtype, severity, status, time, timens, value)
                                         values  (?    , ? , ?    , ?       , ?     , ?   , ?     , ?    );""",
                          izip(
                              repeat(eid, len(names)),
                              pvid,
                              ret['dbrType'].tolist(),
                              ret['severity'].tolist(),
                              ret['status'].tolist(),
                              ret['secondsPastEpoch'].tolist(),
                              ret['nanoseconds'].tolist(),
                              [self.encodeValue(V) for V in ret['value']],
                          ))

            _log.debug("event %s with %s %s", eid, len(names), C.rowcount)

        return self.retrieveSnapshot(eventid=eid)

    @rpc(NTScalar.buildType('?'))
    def updateSnapshotEvent(self, eventid=None, configname=None, user=None, desc=None):
        eventid = int(eventid)
        if user is None or desc is None:
            raise RemoteError("must provide user name and description")
        with self.conn as conn:
            C = conn.cursor()
            _log.debug("updateSnapshotEvent() update %s with %s '%s'", eventid, user, desc[20:])

            evt = C.execute('select config.name from event inner join config on event.config=config.id where event.id=?',
                            (eventid,)).fetchone()
            if evt is None:
                raise RemoteError("No event")
            elif configname is not None and configname!=evt[0]:
                raise RemoteError('eventid and configname are inconsistent')

            C.execute('update event set user=?, comment=? where id=? and user is NULL and comment is NULL',
                      (user, desc, eventid))

            _log.debug("changed %s", C.rowcount)
            return {
                'value': C.rowcount==1,
            }