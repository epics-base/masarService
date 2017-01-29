
import unittest, sqlite3

import numpy

from ..db import connect

class TestDB(unittest.TestCase):
    def setUp(self):
        self.conn = connect(':memory:')

    def tearDown(self):
        self.conn.close()

    def test_conn(self):
        with self.conn:
            C = self.conn.cursor()
            C.execute('PRAGMA user_version;')
            self.assertEqual(1, C.fetchone()[0])
