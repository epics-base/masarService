from pymasarsqlite.db.addmasarconfigs import saveMongoService, saveSQLiteServiceConfig, savePvGroups
from pymasarmongo.db import utils
from pymasarmongo.config._config import masarconfig
from pymasarsqlite.service.serviceconfig import (retrieveServiceConfigs)
from pymasarsqlite.pvgroup.pvgroup import (savePvGroup, retrievePvGroups)
from pymasarsqlite.pvgroup.pv import (saveGroupPvs)
from pymasarsqlite.service.service import (saveService)
from pymasarmongo.pymasarmongo.pymasar import retrieveconfig
import ConfigParser
import os
import unittest
import json
import sqlite3
import sys

'''

Unittests for masarService/python/pymasarsqlite/db/addmasarconfigs.py

'''


class TestAddMasarConfigs(unittest.TestCase):

    def setUp(self):
        file_name = "/"+__file__.split("/")[-1]
        dir_name = __file__[:-1*len(file_name)]
        os.chdir(dir_name)
        os.chdir("../../../python/pymasarsqlite/db")
        config = self.__loadmasarconfig("../../masarserver/masarservice.conf")
        self.db = config.get("Common", "database")
        json_file = "db_config.txt"
        with open(json_file) as file:
            self.parsed_json = json.load(file)

    def tearDown(self):
        pass

    def testSaveService(self):
        if self.db == "sqlite":
            # DB SETUP
            __sqlitedb__ = os.environ["MASAR_SQLITE_DB"]
            try:
                conn = sqlite3.connect(__sqlitedb__)
                cur = conn.cursor()
                __sql__ = None
                if __sql__ is None:
                    from pymasarsqlite.db.masarsqlite import SQL
                else:
                    sqlfile = open(__sql__)
                    SQL = sqlfile.read()
                if SQL is None:
                    print ('SQLite script is empty. Cannot create SQLite db.')
                    sys.exit()
                else:
                    cur.executescript(SQL)
                    cur.execute("PRAGMA main.page_size= 4096;")
                    cur.execute("PRAGMA main.default_cache_size= 10000;")
                    cur.execute("PRAGMA main.locking_mode=EXCLUSIVE;")
                    cur.execute("PRAGMA main.synchronous=NORMAL;")
                    cur.execute("PRAGMA main.journal_mode=WAL;")
                    cur.execute("PRAGMA main.temp_store = MEMORY;")

                cur.execute('select name from sqlite_master where type=\'table\'')
                masarconf = 'SR_All_20140421'
                servicename = 'masar'

                pvgname = 'masarpvgroup'
                pvgdesc = 'this is my new pv group for masar service with same group name'
                pvs = ["masarExample0000",
                       "masarExample0001",
                       "masarExampleBoUninit",
                       "masarExampleMbboUninit",
                       "masarExample0002",
                       "masarExample0003",
                       "masarExample0004",
                       "masarExampleCharArray",
                       "masarExampleShortArray",
                       "masarExampleLongArray",
                       "masarExampleStringArray",
                       "masarExampleFloatArray",
                       "masarExampleDoubleArray",
                       "masarExampleMbboUninitTest"]
                res = savePvGroup(conn, pvgname, func=pvgdesc)
                res = saveGroupPvs(conn, pvgname, pvs)
                pvgroups = retrievePvGroups(conn)
                saveService(conn, servicename, desc='test desc')
                conn.commit()
                conn.close()
                savePvGroups(self.parsed_json['pvgroups'])
                saveSQLiteServiceConfig(self.parsed_json)
                conn = sqlite3.connect(__sqlitedb__)
                pvgroups = retrievePvGroups(conn)
                self.assertEqual('BR_MG_Set_20130419', pvgroups[1][1])
                self.assertEqual('Booster magnet power supply set points', pvgroups[1][2])
                self.assertEqual(3, len(pvgroups[1][3].split(':')))  # Confirms correct date format
                self.assertEqual(3, len(pvgroups[1][3].split('-')))
                self.assertEqual(None, pvgroups[1][4])
                configresult = retrieveServiceConfigs(conn)
                self.assertEqual('BR_MG_SCR_20130419', configresult[1][1])
                self.assertEqual('BR ramping PS daily SCR setpoint', configresult[1][2])
                self.assertEqual(3, len(configresult[1][3].split(':')))  # Confirms correct date format
                self.assertEqual(3, len(configresult[1][3].split('-')))
                self.assertEqual(None, configresult[1][4])
                self.assertEqual('active', configresult[1][5])
            except sqlite3.Error, e:
                print ("Error %s:" % e.args[0])
                raise
        elif self.db == "mongodb":
            conn, collection = utils.conn(host=masarconfig.get('mongodb', 'host'), port=masarconfig.get('mongodb', 'port'),
            db=masarconfig.get('mongodb', 'database'))
            conn.drop_database(masarconfig.get('mongodb', 'database'))
            saveMongoService(self.parsed_json)
            res3 = retrieveconfig(conn, collection, 'BR_MG_SCR_20130419', withpvs=True)
            self.assertEqual(res3[0]['status'], 'active')
            self.assertEqual('BR_MG_SCR_20130419', res3[0]['name'])
            self.assertEqual(res3[0]['pvlist']['names'], [u'masarExample0000', u'masarExample0001', u'masarExampleBoUninit', u'masarExampleMbboUninit', u'masarExample0002', u'masarExample0003', u'masarExample0004', u'masarExampleCharArray', u'masarExampleShortArray', u'masarExampleLongArray', u'masarExampleStringArray', u'masarExampleFloatArray', u'masarExampleDoubleArray', u'masarExampleMbboUninitTest'])
            self.assertEqual('BR', res3[0]['system'])
            self.assertEqual(3, len(res3[0]['created_on'].split('-')))  # Date format test
            self.assertEqual(3, len(res3[0]['created_on'].split(':')))
            self.assertEqual(None, res3[0]['version'])
            self.assertEqual(3, len(res3[0]['updated_on'].split('-')))  # Date format test
            self.assertEqual(3, len(res3[0]['updated_on'].split(':')))
            self.assertNotEqual(None, res3[0]['_id'])
            self.assertEqual('BR ramping PS daily SCR setpoint', res3[0]['desc'])

    def __loadmasarconfig(self, config):
        cf = ConfigParser.SafeConfigParser()
        cf.read([
            os.path.expanduser('~/.masarservice.conf'),
            '/etc/masarservice.conf',
            'masarservice.conf',
            config,
            "%s/masarservice.conf" % os.path.abspath(os.path.dirname(__file__))
        ])
        return cf
    if __name__ == '__main__':
        unittest.main()
