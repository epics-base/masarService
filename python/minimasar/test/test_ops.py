
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
        R = self.S.storeServiceConfig(self.conn, configname='first', desc='desc', config=conf)

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
