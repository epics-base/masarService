import os
import sys
import sqlite3
import json
import ConfigParser
import argparse
from pymasarmongo.db import utils
from pymasarmongo.config._config import masarconfig
from masarclient import masarClient
from pymasarsqlite.service.serviceconfig import (saveServiceConfig, retrieveServiceConfigs, retrieveServiceConfigPVs, saveServicePvGroup, retrieveServicePvGroups)
from pymasarsqlite.pvgroup.pvgroup import (savePvGroup, retrievePvGroups)
from pymasarsqlite.pvgroup.pv import (saveGroupPvs, retrieveGroupPvs)
from pymasarsqlite.service.service import (saveService)
from pymasarmongo.pymasarmongo.pymasar import saveconfig
from pymasarmongo.pymasarmongo.pymasar import updateconfig

def __loadmasarconfig(config=""):
    cf = ConfigParser.SafeConfigParser()
    cf.read([
        os.path.expanduser('~/.masarservice.conf'),
        '/etc/masarservice.conf',
        'masarservice.conf',
        config,
        "%s/masarservice.conf" % os.path.abspath(os.path.dirname(__file__))
    ])
    return cf

def savePvGroups(json, basedir):
    for group in json:
        pvgname = group[u'name']
        pvgdesc = group[u'description']
        pv_file = group[u'pvlist']
        pvlist = []
        with open(os.path.join(basedir, pv_file)) as file:
            for line in file:
                pvlist.append(line.strip())
    __sqlitedb__ = os.environ["MASAR_SQLITE_DB"]
    with sqlite3.connect(__sqlitedb__) as conn:
        savePvGroup(conn, pvgname, func=pvgdesc)
        saveGroupPvs(conn, pvgname, pvlist)
        conn.commit()

def saveSQLiteServiceConfig(json):
    servicename = "masar"
    servicedesc = 'machine snapshot, archiving, and retrieve service'
    __sqlitedb__ = os.environ["MASAR_SQLITE_DB"]
    with sqlite3.connect(__sqlitedb__) as conn:
        saveService(conn, servicename, desc=servicedesc)
        for conf in json['configs']:
            try:
                saveServiceConfig(conn, servicename, conf['config_name'], system=conf['system'], status='active', configdesc=conf['config_desc'])
            except:  # TODO: This should be more specific
                print ("configuration name (%s) exists already." % (conf['config_name']))
        for conf in json['pvg2config']:
            try:
                saveServicePvGroup(conn, conf['config_name'], conf['pvgroups'])
            except:
                print "Service config " + str(conf['config_name']) + " already has associated pvgroups: " + str(conf['pvgroups'])
        conn.commit()

def saveMongoService(json):
    conn, collection = utils.conn(host=masarconfig.get('mongodb', 'host'), port=masarconfig.get('mongodb', 'port'),
                                       db=masarconfig.get('mongodb', 'database'))
    for conf in json['configs']:
        params = {"desc": conf['config_desc'],
                  "system": conf['system'],
                  "status": "active"}
        try:
            saveconfig(conn, collection, conf['config_name'], **params)
        except:  # TODO: This should be more specific
            print ("configuration name (%s) exists already." % (conf['config_name']))
    pvgroups = {}  # {"pvgname":["pv1","pv2"]}
    for pvgroup in json['pvgroups']:
        pvlist = []
        pv_file = pvgroup['pvlist']
        if os.path.exists(pv_file):
            with open(pv_file) as file:
                for line in file:
                    pvlist.append(line.strip())
        pvgroups[pvgroup['name']] = pvlist
    for conf in json['pvg2config']:
        pvs = []
        for pvgroup in conf['pvgroups']:
            pvs = pvs + pvgroups[pvgroup]
        updateconfig(conn, collection, conf['config_name'], pvlist={"names": pvs})

def main():
    parser = argparse.ArgumentParser(description='Add masar configurations to either MongoDB or SQLite')
    parser.add_argument('-d', '--database')
    parser.add_argument('-o', '--toggledbtype', action='store_true', default=False)
    parser.add_argument('-c', '--config')
    parser.add_argument('file')
    args = parser.parse_args(args=sys.argv[1:])
    print "args: ",args
    conf_name = ""
    file_name = args.file
    if args.config!=None:
        conf_name = args['config']
    if args.database:
        os.environ["MASAR_SQLITE_DB"] = args.database

    config = __loadmasarconfig(config=conf_name)
    db = config.get("Common", "database")

    fdir = os.path.dirname(file_name)
    with open(file_name) as file:
        parsed_json = json.load(file)

    if args.toggledbtype:
        if db == "sqlite":
            db = "mongodb"
        if db == "mongodb":
            db = "sqlite"

    if db == "sqlite":
        savePvGroups(parsed_json['pvgroups'], fdir)
        saveSQLiteServiceConfig(parsed_json)
    elif db == "mongodb":
        saveMongoService(parsed_json)

if __name__ == '__main__':
    main()
