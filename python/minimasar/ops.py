
import logging, time
_log = logging.getLogger(__name__)

from itertools import izip_longest, izip
from functools import wraps
from operator import itemgetter

from p4p.rpc import RemoteError, rpc
from p4p.nt import NTScalar, NTMultiChannel, NTTable

multiType = NTMultiChannel.buildType('av', extra=[
    ('dbrType', 'ai'),
    ('readonly', 'a?'),
    ('groupName', 'as'),
    ('tags', 'as'),
])

class Service(object):
    def __init__(self, gather=None, sim=False):
        self.gather = gather

        if not sim:
            # current time string (UTC)
            self.now = lambda: time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        else:
            self.now = lambda: time.strftime('%Y-%m-%d %H:%M:%S', (2017, 1, 28, 21, 43, 28, 5, 28, 0))

    @staticmethod
    def _storeMangle(row):
        return {
            'config_idx':row['id'],
            'config_name':row['name'],
            'config_desc':row['desc'],
            'config_create_date':row['created'],
            'config_version':'0',
            'status': 'active' if row['next'] is None else 'inactive',
        }

    @rpc(NTTable([
        ('config_idx','i'),
        ('config_name','s'),
        ('config_desc','s'),
        ('config_create_date','s'),
        ('config_version','s'),
        ('status','s'),
    ]))
    def storeServiceConfig(self, conn, configname=None, oldidx=None, desc=None, config=None):
        with conn:
            C = conn.cursor()

            C.execute('insert into config(name, desc, created) values (?,?,?);', (configname, desc, self.now()))
            newidx = C.lastrowid
            if oldidx is not None:
                C.execute('update config set next=? where id=?', (newidx, int(oldidx)))

            for name, ro, group, tags in izip_longest(
                        config.value.channelName,
                        config.get('value.readonly', []),
                        config.get('value.groupName', []),
                        config.get('value.tags', []),
                    ):

                C.execute('insert into config_pv(config, name, readonly, groupName, tags) VALUES (?,?,?,?,?);',
                        (newidx, name, int(ro) or 0, group or '', tags or ''))

            C.execute("""select id, name, desc, created, next
                                from config
                                where id=?;
                """, (newidx,))

            _log.info("Store configuration %s as %s (old %s)", configname, newidx, oldidx)

            return map(self._storeMangle, C.fetchall())

    @rpc(NTTable([
        ('channelName', 's'),
        ('readonly', '?'),
        ('groupName', 's'),
        ('tags', 's'),
    ]))
    def loadServiceConfig(self, conn, configid=None):
        with conn:
            C = conn.cursor()

            C.execute('select name as channelName, tags, groupName, readonly from config_pv where config=?;', (int(configid),))
            _log.debug("Fetch configuration %s", configid)
            return C.fetchall()

    @rpc(NTTable([
        ('config_idx','i'),
        ('config_name','s'),
        ('config_desc','s'),
        ('config_create_date','s'),
        ('config_version','s'),
        ('status','s'),
    ]))
    def retrieveServiceConfigs(self, conn, servicename=None, configname=None, configversion=None, system=None, eventid=None):
        if servicename not in (None, 'masar'):
            _log.warning("Service names not supported")
            return []
        with conn:
            C = conn.cursor()
            
            cond = []
            vals = []

            _log.debug("retrieveServiceConfigs() configname=%s configverson=%s system=%s",
                       configname, configversion, system)

            if eventid not in (None, '*'):
                C.execute('select config from event where id=?', (int(eventid),))
                idx = C.fetchone()['config']
                cond.append('id=?')
                vals.append(idx)

            else:
                if configname not in (None, '*'):
                    cond.append('name like ?')
                    vals.append(configname)
                if system not in (None, '*'):
                    cond.append('system like ?')
                    vals.append(system)

            if len(cond)>0:
                cond = 'where '+(' '.join(cond))
            else:
                cond = ''

            _log.debug('retrieveServiceConfigs() w/ %s %s', cond, vals)

            C.execute("""select id, name, created, next, desc
                                from config
                                %s;
                """%cond, vals)
            ret = []
            for id, name, created, next, desc in C.fetchall():
                ret.append({
                    'config_idx':id,
                    'config_name':name,
                    'config_create_date':created,
                    'config_desc':desc,
                    'config_version':u'0',
                    'status': 'active' if next is None else 'inactive',
                })
            return ret

    @rpc(NTTable.buildType([
        ('config_prop_id','ai'),
        ('config_idx','ai'),
        ('system_key','as'),
        ('system_val','as'),
    ]))
    def retrieveServiceConfigProps(self, conn, propname=None, servicename=None, configname=None):
        if servicename not in (None, 'masar') or propname!='system':
            _log.warning("Service names not supported")
            return []
        with conn:
            C = conn.cursor()

            cond = []
            vals = []
            if configname not in (None, '*'):
                cond.append('name like ?')
                vals.append(configname)

            if len(cond)>0:
                cond = 'where '+(' '.join(cond))
            else:
                cond = ''

            C.execute('select id, system from config %s'%cond, vals)
            R = []
            for id, system in C.fetchall():
                R.append({'config_prop_id':1,
                        'config_idx':id,
                        'system_key':'system',
                        'system_val':system,
                        })
            return R

    @rpc(NTTable.buildType([
        ('event_id','ai'),
        ('config_id','ai'),
        ('comments','as'),
        ('event_time','as'),
        ('user_name','as'),
    ]))
    def retrieveServiceEvents(self, conn, configid=None, start=None, end=None, comment=None, user=None, eventid=None):
        with conn:
            C = conn.cursor()

            cond = []
            vals = []
            
            if user not in (None, '*'):
                cond.append('user like ?')
                vals.append(user)

            if configid not in (None, '*'):
                cond.append('config=?')
                vals.append(int(configid))

            if len(cond)>0:
                cond = 'where '+(' '.join(cond))
            else:
                cond = ''
            
            C.execute("""select id as event_id,
                                config as config_id,
                                comment as comments,
                                created as event_time,
                                user as user_name
                                from event
                                %s
                """%cond, vals)
            return C.fetchall()

    @rpc(multiType)
    def retrieveSnapshot(self, eventid=None, start=None, end=None, comment=None):
        eventid = int(eventid)
        with conn:
            C = conn.cursor()

            C.execute("""select name, tags, groupName, readonly, dtype, severity, status, time, timens, value
                        from event_pv inner join config_pv on event_pv.pv = config_pv.id
                        """)
            L = C.fetchall()

            sevr = map(itemgetter('severity'), L)

            return {
                'channelName': map(itemgetter('name'), L),
                'value': map(itemgetter('value'), L),
                'severity': sevr,
                'isConnected': map(lambda S: S<=3, sevr),
                'status': map(itemgetter('status'), L),
                'secondsPastEpoch': map(itemgetter('time'), L),
                'nanoseconds': map(itemgetter('timens'), L),
                'dbrType': map(itemgetter('dtype'), L),
                'groupName': map(itemgetter('groupName'), L),
                'readonly': map(itemgetter('readonly'), L),
                'tags': map(itemgetter('tags'), L),
            }

    @rpc(multiType)
    def saveSnapshot(self, conn, servicename=None, configname=None, comment=None, user=None, desc=None):
        if servicename not in (None, 'masar'):
            raise RuntimeError("Bad servicename")
        with conn:
            C = conn.cursor()

            C.execute('select id from config where name=? and next=NULL', (configname,))
            cid = C.fetchone()
            if cid is None:
                raise ValueError("Unknown config '%s'"%configname)

            C.execute('select id, name, tags, groupName, readonly from event_pv where config=?', (cid,))
            config = C.fetchall()

            pvid  = map(itemgetter('id'), config)
            names = map(itemgetter('name'), config)

            ret = self.gather(names)

            C.execute('insert into event(config, user, comment) values (?)', (cid, user, desc))
            eid = C.lastrowid

            C.executemany("""insert into event_pv(event, pv, dtype, severity, status, time, timens, value)
                                         values  (?    , ? , ?    , ?       , ?     , ?   , ?     , ?    );""",
                          izip(
                              pvid,
                              names,
                              ret['dbrType'],
                              ret['severity'],
                              ret['status'],
                              ret['secondsPastEpoch'],
                              ret['nanoseconds'],
                              ret['value'],
                          ))

            ret['tags'] = map(itemgetter('tags'), config)
            ret['groupName'] = map(itemgetter('groupName'), config)
            ret['readonly'] = map(itemgetter('readonly'), config)

            ret['timeStamp'] = {'userTag': eid}

            return ret

    @rpc(NTScalar.buildType('?'))
    def updateSnapshotEvent(self, eventid=None, user=None, desc=None):
        eventid = int(eventid)
        with conn:
            C = conn.cursor()

            C.execute('update event set user=?, comment=? where id=?', (user, desc, eventid))

    @rpc(multiType)
    def getLiveMachine(self, **kws):
        return self.gather(kws.values())
