import os
import sqlite3
import sys

from pymasarsqlite.service.serviceconfig import (saveServiceConfig, retrieveServiceConfigs, retrieveServiceConfigPVs, saveServicePvGroup, retrieveServicePvGroups)
from pymasarsqlite.pvgroup.pvgroup import (savePvGroup, retrievePvGroups)
from pymasarsqlite.pvgroup.pv import (saveGroupPvs, retrieveGroupPvs)
from pymasarsqlite.service.service import (saveService)
from pymasarmongo.pymasarmongo.pymasar import saveconfig
from pymasarmongo.pymasarmongo.pymasar import updateconfig
from pymasarmongo.db import utils
from pymasarmongo.config._config import masarconfig


def SQLITE_DB_TEST_SETUP():
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
        saveServiceConfig(conn, servicename, masarconf, system='SR', status='active',
                          configversion=20140420, configdesc='test desc')

        res = saveServicePvGroup(conn, masarconf, [pvgname])
        pvlist = retrieveServiceConfigPVs(conn, masarconf, servicename=servicename)
        results = retrieveServiceConfigs(conn, servicename, masarconf)
        conn.commit()
        conn.close()
    except sqlite3.Error, e:
        print ("Error %s:" % e.args[0])
        raise

def SQLITE_DROP_ALL_TABLES():
    __sqlitedb__ = os.environ["MASAR_SQLITE_DB"]
    try:
        with sqlite3.connect(__sqlitedb__) as conn:
            cur = conn.cursor()
            cur.execute("drop table if exists masar_data")
            cur.execute("drop table if exists pv")
            cur.execute("drop table if exists pv_pvgroup")
            cur.execute("drop table if exists pv_group")
            cur.execute("drop table if exists pvgroup_serviceconfig")
            cur.execute("drop table if exists service")
            cur.execute("drop table if exists service_config")
            cur.execute("drop table if exists service_config_prop")
            cur.execute("drop table if exists service_event")
            cur.execute("drop table if exists service_event_prop")
            conn.commit()
    except sqlite3.Error, e:
        print ("Error %s:" % e.args[0])
        raise

def MONGODB_TEST_SETUP(self):
    self.conn, collection = utils.conn(host=masarconfig.get('mongodb', 'host'), port=masarconfig.get('mongodb', 'port'),
                                       db=masarconfig.get('mongodb', 'database'))


    self.conn.drop_database(masarconfig.get('mongodb', 'database'))
    name = "SR_All_20140421"
    params = {"desc": "SR daily SCR setpoint without IS kick and septum: SR and RF",
              "system": "SR",
              "status": "active",
              "version": 20140421,
              }
    newid = saveconfig(self.conn, collection, name, **params)
    # res0 = retrieveconfig(self.conn, collection, name)
    pvs = ["masarExample0000",
           "masarExample0001",
           # "masarExampleBoUninit",
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
    # TODO: Save will fail if list contains only 1 PV
    updateconfig(self.conn, collection, name, pvlist={"names": pvs})
    # res3 = retrieveconfig(self.conn, collection, name, withpvs=True)
    return self.conn