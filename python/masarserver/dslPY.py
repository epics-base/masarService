# dsl.py
#
# Copyright - See the COPYRIGHT that is included with this distribution.
# This code is distributed subject to a Software License Agreement
#    found in file LICENSE that is included with this distribution.
# Author: Guobao Shen   2012.01
#         Marty Kraimer 2011.11

import os
import os.path

import ConfigParser


def __loadmasarconfig():
    cf = ConfigParser.SafeConfigParser()
    cf.read([
        os.path.expanduser('~/.masarservice.conf'),
        '/etc/masarservice.conf',
        'masarservice.conf',
        "%s/masarservice.conf" % os.path.abspath(os.path.dirname(__file__))
    ])
    return cf

masarconfig = __loadmasarconfig()
if masarconfig.has_section("Common"):
    dbsrc = masarconfig.get("Common", "database")

if dbsrc == "mongodb":
    os.environ["MASAR_MONGO_DB"] = masarconfig.get('mongodb', 'database')
    os.environ["MASAR_MONGO_HOST"] = masarconfig.get('mongodb', 'host')
    os.environ["MASAR_MONGO_PORT"] = masarconfig.get('mongodb', 'port')
    print "Using MongoDB as backend."
    print "MongoDB: host: %s, port: %s, database: %s" % (os.environ["MASAR_MONGO_HOST"],
                                                         os.environ["MASAR_MONGO_PORT"],
                                                         os.environ["MASAR_MONGO_DB"])
    import pymasarmongo as pymasar
    from dslPYMongo import DSL
# elif dbsrc == "mysql":
#     print "Using MySQL as backend."
#     import pymasarmysql as pymasar
elif dbsrc == "sqlite":
    if os.getenv("MASAR_SQLITE_DB", None) is None:
        os.environ["MASAR_SQLITE_DB"] = masarconfig.get("sqlite", "database")
    if not os.access(os.environ["MASAR_SQLITE_DB"], os.W_OK):
        raise RuntimeError("MASAR database (%s) is not writable." % os.environ["MASAR_SQLITE_DB"])
    print "Using SQLite as backend."
    print "DB file: ", os.environ["MASAR_SQLITE_DB"]
    import pymasarsqlite as pymasar
    from dslPYSQLite import DSL
else:
    raise ImportError("Unknown database source.")

__all__ = pymasar.__all__
