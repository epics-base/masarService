
import unittest, sqlite3

import numpy

from ..db import connect

class TestDB(unittest.TestCase):
    def setUp(self):
        self.conn = connect(':memory:')

    def tearDown(self):
        self.conn.close()

    def test_conn(self):
        with self.conn as conn:
            C = conn.cursor()
            C.execute('PRAGMA user_version;')
            self.assertEqual(1, C.fetchone()[0])

    def test_config_pv_unique(self):
        with self.conn as conn:
            cid = conn.execute('insert into config(name, created, desc) values (?,?,?);',
                ('cname', 'aaa', 'bbb'),
            ).lastrowid

            self.assertRaises(sqlite3.IntegrityError,
                conn.executemany, 'insert into config_pv(config, name) values (?,?);', [
                    (cid, 'foo'),
                    (cid, 'foo'), # should fail UNIQUE
            ])
