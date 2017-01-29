
import unittest

from ..db import connect
from ..ops import Service
from p4p.wrapper import Value, Type
from p4p.nt import NTTable

import numpy
from numpy.testing import assert_equal

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.conn = connect(':memory:')
        self.S = Service(sim=True)

    def tearDown(self):
        self.conn.close()

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
        R = self.S.storeServiceConfig(self.conn, configname='first', desc='desc', config=conf, system='xx')

        self.assertIsInstance(R, Value)
        self.assertListEqual(R.labels, [u'config_idx',
                                    u'config_name',
                                    u'config_desc',
                                    u'config_create_date',
                                    u'config_version',
                                    u'status'])

        self.assertListEqual(R.value.tolist(), [
            ('config_idx', numpy.asarray([1])),
            ('config_name', [u'first']),
            ('config_desc', [u'desc']),
            ('config_create_date', [u'2017-01-28 21:43:28']),
            ('config_version', [u'0']),
            ('status', [u'active'])
        ])

        ######### verify DB
        R = self.conn.execute('select * from config;').fetchone()
        self.assertEqual(R['id'], 1)
        self.assertEqual(R['name'], 'first')
        self.assertIsNone(R['next'])

        R = map(tuple, self.conn.execute('select name, readonly, groupName, tags from config_pv where config=?;', (1,)).fetchall())
        self.assertListEqual(R, [
            (u'one', 0, u'A', u''),
            (u'two', 1, u'', u'a, b'),
        ])

        ######### Load
        R = self.S.loadServiceConfig(self.conn, configid='1')
        self.assertIsInstance(R, Value)
        self.assertListEqual(R.labels, conf.labels)

        self.assertListEqual(R.value.channelName, conf.value.channelName)
        assert_equal(R.value.readonly, conf.value.readonly)
        self.assertListEqual(R.value.groupName, conf.value.groupName)
        self.assertListEqual(R.value.tags, conf.value.tags)

        ######### Query
        R = self.S.retrieveServiceConfigs(self.conn, configname='*')

        self.assertIsInstance(R, Value)
        self.assertListEqual(R.labels, [u'config_idx',
                                    u'config_name',
                                    u'config_desc',
                                    u'config_create_date',
                                    u'config_version',
                                    u'status'])

        self.assertListEqual(R.value.tolist(), [
            ('config_idx', numpy.asarray([1])),
            ('config_name', [u'first']),
            ('config_desc', [u'desc']),
            ('config_create_date', [u'2017-01-28 21:43:28']),
            ('config_version', [u'0']),
            ('status', [u'active'])
        ])

        R = self.S.retrieveServiceConfigProps(self.conn)
        self.assertIsInstance(R, Value)
        self.assertListEqual(R.labels, [u'config_prop_id',
                                    u'config_idx',
                                    u'system_key',
                                    u'system_val'])

        self.assertListEqual(R.value.tolist(), [
            ('config_prop_id', numpy.asarray([1], dtype=numpy.int32)),
            ('config_idx', numpy.asarray([1], dtype=numpy.int32)),
            ('system_key', [u'system']),
            ('system_val', [u'xx']),
        ])


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
        return ret

    def setUp(self):
        self.conn = connect(':memory:')
        self.S = Service(gather=self.gather, sim=True)
        self.conn.execute('insert into config(id,name,created,desc) values (?,?,?,?)',
                          (1, 'configname', self.S.now(), 'description'))
        self.conn.executemany('insert into config_pv(id,config,name) values (?,?,?)', [
            (1, 1, 'pv:flt:1'),
            (2, 1, 'pv:flt:2'),
            (3, 1, 'pv:bad:3'),
        ])

    def tearDown(self):
        self.conn.close()

    def testFetchNone(self):
        R = self.S.retrieveServiceEvents(self.conn, configid='1')
        self.assertListEqual(R.labels, [u'event_id', u'config_id', u'comments', u'event_time', u'user_name'])
        self.assertListEqual(R.value.user_name, [])

    def testSaveEvent(self):
        expect = {
            'channelName': [u'pv:flt:1', u'pv:flt:2', u'pv:bad:3'],
            'dbrType': [6, 6, 6],
            'groupName': [u'', u'', u''],
            'isConnected': [True, True, False],
            'message': ['', '', ''],
            'nanoseconds': [0, 0, 0],
            'readonly': [0, 0, 0],
            'secondsPastEpoch': [12345678, 12345678, 12345678],
            'severity': [0, 0, 4],
            'status': [0, 0, 0],
            'tags': [u'', u'', u''],
            'timeStamp': {'userTag': 1},
            'userTag': [0, 0, 0],
            'value': [1.2, 1.2, 0]
        }

        R = self.S.saveSnapshot(self.conn, configname='configname')

        self.assertDictEqual(R, expect)

        # won't find as user name not set
        R = self.S.retrieveServiceEvents(self.conn, configid='1')
        self.assertListEqual(R.labels, [u'event_id', u'config_id', u'comments', u'event_time', u'user_name'])
        self.assertListEqual(R.value.user_name, [])

        R = self.S.updateSnapshotEvent(self.conn, eventid='1', user='someone', desc='it works')
        self.assertEqual(R['value'], True)

        R = self.S.retrieveServiceEvents(self.conn, configid='1')
        self.assertListEqual(R.labels, [u'event_id', u'config_id', u'comments', u'event_time', u'user_name'])
        self.assertListEqual(R.value.user_name, [
            'someone',
        ])

        R = self.S.retrieveSnapshot(self.conn, eventid='1')
        self.assertDictEqual(R, expect)
