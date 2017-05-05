
import logging, time, json
from calendar import timegm
_log = logging.getLogger(__name__)

try:
    from itertools import izip_longest, izip, repeat
except ImportError:
    from itertools import (zip_longest as izip_longest, repeat)
    izip = zip
from functools import wraps
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

def jsonarray(val):
    if isinstance(val, numpy.ndarray):
        return val.tolist()
    else:
        raise TypeError("Can't serialize %s"%type(val))

def normtime(tstr):
    'Normalize user provided time string'
    T = time.strptime(tstr, '%Y-%m-%d %H:%M:%S')
    return time.strftime('%Y-%m-%d %H:%M:%S', T)

def timestr2tuple(tstr):
    'time string to PVD time tuple'
    T = time.strptime(tstr, '%Y-%m-%d %H:%M:%S')
    S, NS = divmod(timegm(T), 1.0)
    return int(S), int(NS*1e9)

class Service(object):
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

    @rpc(configTable)
    def storeServiceConfig(self, configname=None, oldidx=None, desc=None, config=None, system=None):
        with self.conn as conn:
            C = conn.cursor()

            _log.debug("storeServiceConfig() %s(%s)", configname, oldidx)

            C.execute('insert into config(name, desc, created, system) values (?,?,?,?);', (configname, desc, self.now(), system))
            newidx = C.lastrowid
            if oldidx is not None:
                # update existing row only if it was previously active
                C.execute('update config set next=? where id=? and next is NULL', (newidx, int(oldidx)))

            if C.execute('select count(*) from config where name=? and next is NULL', (configname,)).fetchone()[0]!=1:
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

            C.execute("""select id, name, desc, created, next, system
                                from config
                                where id=?;
                """, (newidx,))

            _log.info("Store configuration %s as %s (old %s)", configname, newidx, oldidx)

            return map(lambda row: {
                            'config_idx':row['id'],
                            'config_name':row['name'],
                            'config_desc':row['desc'],
                            'config_create_date':row['created'],
                            'config_version':'0',
                            'status': 'active' if row['next'] is None else 'inactive',
                            'system': row['system'] or '',
                        },
                        C.fetchall())

    @rpc(NTTable([
        ('channelName', 's'),
        ('readonly', '?'),
        ('groupName', 's'),
        ('tags', 's'),
    ]))
    def loadServiceConfig(self, configid=None):
        configid = int(configid)
        with self.conn as conn:
            C = conn.cursor()

            R = C.execute('select id from config where id=?', (configid,)).fetchone()
            if R is None:
                raise RemoteError("Unknown configid %s"%configid)

            C.execute('select name as channelName, tags, groupName, readonly from config_pv where config=?;', (int(configid),))
            _log.debug("Fetch configuration %s", configid)
            return C.fetchall()

    @rpc(configTable)
    def retrieveServiceConfigs(self, servicename=None, configname=None, configversion=None, system=None, eventid=None, status=None):
        if servicename not in (None, 'masar'):
            _log.warning("Service names not supported")
            return []
        if status not in (None, 'active', 'inactive'):
            return []
        with self.conn as conn:
            C = conn.cursor()
            
            cond = []
            vals = []

            _log.debug("retrieveServiceConfigs() configname=%s configverson=%s system=%s",
                       configname, configversion, system)

            if eventid not in (None, u'*'):
                C.execute('select config from event where id=?', (int(eventid),))
                idx = C.fetchone()['config']
                cond.append('id=?')
                vals.append(idx)

            else:
                if status=='active':
                    cond.append('next is NULL')
                elif status=='inactive':
                    cond.append('next is not NULL')

                if configname not in (None, u'*', u'all'):
                    cond.append('name glob ?')
                    vals.append(configname)

                if system not in (None, u'*', u'all'):
                    cond.append('system glob ?')
                    vals.append(system)

            if len(cond)>0:
                cond = 'where '+(', '.join(cond))
            else:
                cond = ''

            _log.debug('retrieveServiceConfigs() w/ %s %s', cond, vals)

            C.execute("""select id, name, created, next, desc, system
                                from config
                                %s;
                """%cond, vals)
            ret = []
            for id, name, created, next, desc, system in C.fetchall():
                ret.append({
                    'config_idx':id,
                    'config_name':name,
                    'config_create_date':created,
                    'config_desc':desc,
                    'config_version':u'0',
                    'status': 'active' if next is None else 'inactive',
                    'system': system or '',
                })
            return ret

    @rpc(NTTable([
        ('config_prop_id','i'),
        ('config_idx','i'),
        ('system_key','s'),
        ('system_val','s'),
    ]))
    def retrieveServiceConfigProps(self, propname=None, servicename=None, configname=None):
        if servicename not in (None, '*', 'masar') or propname not in (None, '*', 'system'):
            _log.warning("Service names or non 'system' prop names not supported")
            return []
        with self.conn as conn:
            C = conn.cursor()

            cond = []
            vals = []
            if configname not in (None, u'*'):
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
            
            if user not in (None, u'*'):
                cond.append('user glob ?')
                vals.append(user)

            if comment not in (None, u'*'):
                cond.append('comment glob ?')
                vals.append(comment)

            if configid not in (None, u'*'):
                cond.append('config=?')
                vals.append(int(configid))

            # HACK instead of using julianday(), use lexial comparison,
            # which should produce the same result as we always store time
            # as "YYYY-MM-DD HH:MM:SS"
            if start is not None:
                cond.append("event_time>=?")
                vals.append(normtime(start))

            if end is not None:
                cond.append("event_time<?")
                vals.append(normtime(end))

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

    @rpc(multiType)
    def retrieveSnapshot(self, eventid=None, start=None, end=None, comment=None):
        # start, end, and comment ignored
        eventid = int(eventid)
        with self.conn as conn:
            C = conn.cursor()

            _log.debug("retrieveSnapshot() %d", eventid)

            C.execute('select created from event where id=?', (eventid,))
            S, NS = timestr2tuple(C.fetchone()[0])

            C.execute("""select name, tags, groupName, readonly, dtype, severity, status, time, timens,
                        value as "value [json]"
                        from event_pv inner join config_pv on event_pv.pv = config_pv.id
                        where event_pv.event = ?
                        """, (eventid,))
            L = C.fetchall()

        sevr = list(map(itemgetter('severity'), L))

        def unpack(I):
            V, dbr = I['value'], I['dtype']
            if dbr!=0 and isinstance(V, list):
                V = numpy.asarray(V)
            return V

        return {
            'channelName': list(map(itemgetter('name'), L)),
            'value': list(map(unpack, L)),   # call to json.loads happening in sqlite3 converter
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

    @rpc(multiType)
    def saveSnapshot(self, servicename=None, configname=None, comment=None, user=None, desc=None):
        if servicename not in (None, 'masar'):
            raise RemoteError("Bad servicename")
        with self.conn as conn:
            C = conn.cursor()

            C.execute('select id from config where name=? and next is NULL', (configname,))
            cid = C.fetchone()
            if cid is None:
                raise RemoteError("Unknown config '%s'"%configname)
            cid = cid[0]
            _log.debug("saveSnapshot() for '%s'(%s)", configname, cid)

            C.execute('select id, name, tags, groupName, readonly from config_pv where config=?', (cid,))
            config = C.fetchall()

            pvid  = list(map(itemgetter('id'), config))
            names = list(map(itemgetter('name'), config))

            ret = self.gather(names)
            _log.debug("Gather complete")

            C.execute('insert into event(config, user, comment, created) values (?,?,?,?)', (cid, user, desc, self.now()))
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
                              [json.dumps(V, default=jsonarray) for V in ret['value']],
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
