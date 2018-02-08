

import unittest

from p4p.wrapper import Value
from p4p.nt import NTTable

from minimasar.db_postgres import connect
from minimasar.ops_postgres import Service

from p4p.rpc import RemoteError

import numpy
from numpy.testing import assert_equal
from minimasar import ops_base, db_postgres

#import dbsettings_postgres

import testing.postgresql
from sqlalchemy import create_engine
import psycopg2

    # Generate Postgresql class which shares the generated database
Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True)

class TestConfig(unittest.TestCase):
    def setUp(self):
        #with testing.postgresql.Postgresql() as postgresql:
        # Use the generated Postgresql class instead of testing.postgresql.Postgresql
        
        self.postgresql = Postgresql()
        self.conn = psycopg2.connect(**(self.postgresql).dsn())
        
        cursor = self.conn.cursor()
        
        for command in db_postgres._commands:
            cursor.execute(command)
                
        cursor.close()
        self.conn.commit()
        
        self.S = Service(conn=self.conn, sim=True) 
        

    def tearDown(self):
        #print 'closing connection'
        #print self.conn
        #self.conn.close()
        # clear cached database at end of tests
        Postgresql.clear_cache()
        #return

    def testStoreFirst(self):
        conf = Value(NTTable.buildType([
            ('channelName', 'as'),
            ('readonly', 'a?'),
            ('groupName', 'as'),
            ('tags', 'as'),
        ]), {
            'labels': ['channelName', 'readonly', 'groupName', 'tags'],
            'value': {
                'channelName': ['one', 'two'],
                'readonly': [False, True],
                'groupName': ['A', ''],
                'tags': ['', 'a, b'],
            },
        })

        ######### Store
        R = self.S.storeServiceConfig(configname='first', desc='desc', config=conf, system='xx')

        self.assertIsInstance(R, Value)
        self.assertListEqual(R.labels, [u'config_idx',
                                    u'config_name',
                                    u'config_desc',
                                    u'config_create_date',
                                    u'config_version',
                                    u'status',
                                    u'system'])

        configid = int(R.value.config_idx[0]) # numpy.int32 -> int (so sqlite can bind it)

        self.assertListEqual([
            ('config_idx', numpy.asarray([configid], dtype='i4')),
            ('config_name', [u'first']),
            ('config_desc', [u'desc']),
            ('config_create_date', [u'2017-01-28 21:43:28']),
            ('config_version', [u'0']),
            ('status', [u'active']),
            ('system', [u'xx']),
        ], R.value.tolist())

        ######### verify DB
        C = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        C.execute('select * from config where id is not NULL;')
        R = C.fetchone()
        self.assertEqual(R['id'], configid)
        self.assertEqual(R['name'], 'first')
        self.assertIsNone(R['next'])
        
        C.execute('select name, readonly, groupName, tags from config_pv where config=%s;', (configid,))

        R = list(map(tuple, C.fetchall()))
        self.assertListEqual(R, [
            (u'one', 0, u'A', u''),
            (u'two', 1, u'', u'a, b'),
        ])
        
        C.close()

        ######### Load
        R = self.S.loadServiceConfig(configid=str(configid))
        self.assertIsInstance(R, Value)
        self.assertListEqual(R.labels, conf.labels)

        self.assertListEqual(R.value.channelName, conf.value.channelName)
        assert_equal(R.value.readonly, conf.value.readonly)
        self.assertListEqual(R.value.groupName, conf.value.groupName)
        self.assertListEqual(R.value.tags, conf.value.tags)

        ######### Query
        R = self.S.retrieveServiceConfigs(configname='*')

        self.assertIsInstance(R, Value)
        self.assertListEqual(R.labels, [u'config_idx',
                                    u'config_name',
                                    u'config_desc',
                                    u'config_create_date',
                                    u'config_version',
                                    u'status',
                                    u'system'])

        self.assertListEqual(R.value.tolist(), [
            ('config_idx', numpy.asarray([configid])),
            ('config_name', [u'first']),
            ('config_desc', [u'desc']),
            ('config_create_date', [u'2017-01-28 21:43:28']),
            ('config_version', [u'0']),
            ('status', [u'active']),
            ('system', [u'xx']),
        ])

        R = self.S.retrieveServiceConfigProps()
        self.assertIsInstance(R, Value)
        self.assertListEqual(R.labels, [u'config_prop_id',
                                    u'config_idx',
                                    u'system_key',
                                    u'system_val'])

        self.assertListEqual(R.value.tolist(), [
            ('config_prop_id', numpy.asarray([1], dtype=numpy.int32)),
            ('config_idx', numpy.asarray([configid], dtype=numpy.int32)),
            ('system_key', [u'system']),
            ('system_val', [u'xx']),
        ])

    
    def testStoreUpdate(self):
        C = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        C.execute('insert into config(name, created, description) values (\'foo\',\'\',\'\') returning id')
        oldidx = C.fetchone()[0]

        conf = Value(NTTable.buildType([
            ('channelName', 'as'),
            ('readonly', 'a?'),
            ('groupName', 'as'),
            ('tags', 'as'),
        ]), {
            'labels': ['channelName', 'readonly', 'groupName', 'tags'],
            'value': {
                'channelName': ['one', 'two'],
                'readonly': [False, True],
                'groupName': ['A', ''],
                'tags': ['', 'a, b'],
            },
        })

        R = self.S.storeServiceConfig(configname='foo', oldidx=str(oldidx),
                                      desc='desc', config=conf, system='xx')
        configid = int(R.value.config_idx[0]) # numpy.int32 -> int (so sqlite can bind it)

        self.assertListEqual([
            ('config_idx', numpy.asarray([configid], dtype='i4')),
            ('config_name', [u'foo']),
            ('config_desc', [u'desc']),
            ('config_create_date', [u'2017-01-28 21:43:28']),
            ('config_version', [u'0']),
            ('status', [u'active']),
            ('system', [u'xx']),
        ], R.value.tolist())

        self.assertNotEqual(oldidx, configid)
        
        C.execute('select id, name, next from config order by id')

        self.assertListEqual(list(map(tuple, C.fetchall())), [
            (oldidx, u'foo', configid), # inactive
            (configid, u'foo', None), # active
        ])
        
        C.close()

    
    def testStoreUpdate1Bad(self):
        "Attempt to use the name of an existing config"
        
        C = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        C.execute('insert into config(name, created, description) values (\'foo\',\'\',\'\') returning id')
    
        conf = Value(NTTable.buildType([
            ('channelName', 'as'),
            ('readonly', 'a?'),
            ('groupName', 'as'),
            ('tags', 'as'),
        ]), {
            'labels': ['channelName', 'readonly', 'groupName', 'tags'],
            'value': {
                'channelName': ['one', 'two'],
                'readonly': [False, True],
                'groupName': ['A', ''],
                'tags': ['', 'a, b'],
            },
        })

        self.assertRaises(RemoteError, 
            self.S.storeServiceConfig, configname='foo',
                                      desc='desc', config=conf, system='xx')
        C.close()

    
    def testStoreUpdate2Bad(self):
        "Attempt to replace an inactive config"
        C = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        C.execute('insert into config(id, name, next, created, description) values (3,\'foo\',NULL,\'\',\'\');')
        C.execute('insert into config(id, name, next, created, description) values (2,\'foo\',3,\'\',\'\');')
        
        oldidx = 2

        conf = Value(NTTable.buildType([
            ('channelName', 'as'),
            ('readonly', 'a?'),
            ('groupName', 'as'),
            ('tags', 'as'),
        ]), {
            'labels': ['channelName', 'readonly', 'groupName', 'tags'],
            'value': {
                'channelName': ['one', 'two'],
                'readonly': [False, True],
                'groupName': ['A', ''],
                'tags': ['', 'a, b'],
            },
        })

        self.assertRaises(RemoteError, 
            self.S.storeServiceConfig, configname='foo', oldidx=str(oldidx),
                                      desc='desc', config=conf, system='xx')
        
        C.close()

    
    def testStoreUpdateActive(self):
        "Make a configuration inactive"
        C = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        C.execute('insert into config(name, created, description) values (\'foo\',\'\',\'\') returning id')
        idx = C.fetchone()[0]
        
        C.execute('select active from config where id=%s', (idx,))

        self.assertEqual(1, C.fetchone()[0])

        R = self.S.modifyServiceConfig(configid=idx, status='active')
        self.assertEqual('active', R.value.status[0])

        C.execute('select active from config where id=%s', (idx,))
        self.assertEqual(1, C.fetchone()[0])

        R = self.S.modifyServiceConfig(configid=idx, status='inactive')
        self.assertEqual('inactive', R.value.status[0])


        C.execute('select active from config where id=%s', (idx,))
        self.assertEqual(0, C.fetchone()[0])

        R = self.S.modifyServiceConfig(configid=idx, status='active')
        self.assertEqual('active', R.value.status[0])

        C.execute('select active from config where id=%s', (idx,))
        self.assertEqual(1, C.fetchone()[0])
        
        C.close()
    

class TestEvents(unittest.TestCase):
    def gather(self, pvs):
        ret = {
            'value':[],
            'channelName':pvs,
            'severity': [],
            'status': [],
            'message': ['']*len(pvs),
            'secondsPastEpoch': [12345678]*len(pvs),
            'nanoseconds': [0]*len(pvs),
            'userTag': [0]*len(pvs),
            'isConnected': [],
            'dbrType': [],
            'readonly': [False]*len(pvs),
            'groupName': ['']*len(pvs),
            'tags': ['']*len(pvs),
        }

        for i,pv in enumerate(pvs):
            if pv.startswith('pv:flt:'):
                ret['value'].append(1.2)
                ret['severity'].append(0)
                ret['status'].append(0)
                ret['dbrType'].append(6)
                ret['isConnected'].append(True)
            else:
                ret['value'].append(0)
                ret['severity'].append(4)
                ret['status'].append(0)
                ret['dbrType'].append(6)
                ret['isConnected'].append(False)
        return Value(ops_base.multiType, ret)

    def setUp(self):
        #with testing.postgresql.Postgresql() as postgresql:
        self.postgresql = Postgresql()
        self.conn = psycopg2.connect(**(self.postgresql).dsn())
        self.S = Service(conn=self.conn, gather=self.gather, sim=True)
        
        cursor = self.conn.cursor()
        
        for command in db_postgres._commands:
            cursor.execute(command)

        cursor.execute('insert into config(id,name,created,description) values (%s,%s,%s,%s)',
                          (2, 'configname', self.S.now(), 'description'))
        cursor.executemany('insert into config_pv(id,config,name) values (%s,%s,%s)', [
            (1, 2, 'pv:flt:1'),
            (2, 2, 'pv:flt:2'),
            (3, 2, 'pv:bad:3'),
        ])
        
        self.conn.commit()
        
        cursor.close()

    def tearDown(self):
        #self.conn.close()
        Postgresql.clear_cache()

    def testFetchNone(self):
        R = self.S.retrieveServiceEvents(configid='1')
        self.assertListEqual(R.labels, [u'event_id', u'config_id', u'comments', u'event_time', u'user_name'])
        self.assertListEqual(R.value.user_name, [])

    def testSaveEvent(self):
        expect = {
            'channelName': [u'pv:flt:1', u'pv:flt:2', u'pv:bad:3'],
            'dbrType': [6, 6, 6],
            'groupName': [u'', u'', u''],
            'isConnected': [True, True, False],
            'message': [u'', u'', u''],
            'nanoseconds': [0, 0, 0],
            'readonly': [0, 0, 0],
            'secondsPastEpoch': [12345678, 12345678, 12345678],
            'severity': [0, 0, 4],
            'status': [0, 0, 0],
            'tags': [u'', u'', u''],
            'timeStamp': {
                'secondsPastEpoch':1485639808,
                'nanoseconds':0,
                'userTag': 1
            },
            'userTag': [0, 0, 0],
            'value': [1.2, 1.2, 0]
        }

        R = self.S.saveSnapshot(configname='configname')

        self.assertDictEqual(R, expect)

        # won't find as user name not set
        R = self.S.retrieveServiceEvents(configid='2')
        self.assertListEqual(R.labels, [u'event_id', u'config_id', u'comments', u'event_time', u'user_name'])
        self.assertListEqual(R.value.user_name, [])

        R = self.S.updateSnapshotEvent(eventid='1', user='someone', desc='it works')
        self.assertEqual(R['value'], True)

        R = self.S.retrieveServiceEvents(configid='2')
        self.assertListEqual(R.labels, [u'event_id', u'config_id', u'comments', u'event_time', u'user_name'])
        self.assertListEqual(R.value.user_name, [
            'someone',
        ])

        R = self.S.retrieveSnapshot(eventid='1')
        self.assertDictEqual(R, expect)


class TestRetrieve(unittest.TestCase):
    def gather(self, pvs):
        ret = {
            'value':[5],
            'channelName':['one'],
            'severity': [0],
            'status': [0],
            'message': [''],
            'secondsPastEpoch': [12345678],
            'nanoseconds': [0],
            'userTag': [0],
            'isConnected': [True],
            'dbrType': [0],
            'readonly': [False],
            'groupName': [''],
            'tags': [''],
        }
        return Value(ops_base.multiType, ret)

    def setUp(self):
        #with testing.postgresql.Postgresql() as postgresql:
        self.postgresql = Postgresql()
        self.conn = psycopg2.connect(**(self.postgresql).dsn())
        self.S = Service(conn=self.conn, gather=self.gather, sim=True)
        
        cursor = self.conn.cursor()
        
        for command in db_postgres._commands:
            cursor.execute(command)
            
        self.S.simtime = (2017, 1, 28, 21, 43, 28, 5, 28, 0)

        conf = Value(NTTable.buildType([
            ('channelName', 'as'),
            ('readonly', 'a?'),
            ('groupName', 'as'),
            ('tags', 'as'),
        ]), {
            'labels': ['channelName', 'readonly', 'groupName', 'tags'],
            'value': {
                'channelName': ['one'],
                'readonly': [False],
                'groupName': [''],
                'tags': [''],
            },
        })

        R = self.S.storeServiceConfig(configname='first', desc='desc', config=conf, system='xx')
        self.configid = int(R.value.config_idx[0]) # numpy.int32 -> int (so sqlite can bind it)

        S = self.S.saveSnapshot(configname='first', user='foo', desc='bar')
        self.eid1 = S['timeStamp']['userTag']

        self.S.simtime = (2017, 1, 28, 21, 44, 28, 5, 28, 0)

        S = self.S.saveSnapshot(configname='first', user='foo', desc='bar')
        self.eid2 = S['timeStamp']['userTag']

        self.S.simtime = (2017, 1, 28, 21, 45, 28, 5, 28, 0)

        S = self.S.saveSnapshot(configname='first', user='foo', desc='bar')
        self.eid3 = S['timeStamp']['userTag']

    def tearDown(self):
        #self.conn.close()
        Postgresql.clear_cache()

    def testAll(self):
        evts = self.S.retrieveServiceEvents(configid=self.configid)
        assert_equal(evts.value.event_id, [ self.eid1, self.eid2, self.eid3])

    def testAfter(self):
        evts = self.S.retrieveServiceEvents(configid=self.configid,
                                            start='2017-01-28 21:44:00')
        assert_equal(evts.value.event_id, [ self.eid2, self.eid3])

    def testBefore(self):
        evts = self.S.retrieveServiceEvents(configid=self.configid,
                                            end='2017-01-28 21:44:00')
        assert_equal(evts.value.event_id, [ self.eid1])

    def testDuring(self):
        evts = self.S.retrieveServiceEvents(configid=self.configid,
                                            start='2017-01-28 21:44:00',
                                            end=  '2017-01-28 21:45:00')
        assert_equal(evts.value.event_id, [ self.eid2])

    def testDuring2(self):
        evts = self.S.retrieveServiceEvents(configid=self.configid,
                                            start='2017-1-28 21:44:00',
                                            end=  '2017-01-28 21:45:0')
        assert_equal(evts.value.event_id, [ self.eid2])
