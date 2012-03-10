#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script is to create a sqlite database for MASAR service using the SQL file under sqlite directory.
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import os.path

import sqlite3

__sqlitedb__ = 'masar.db'
__sql__ = None

__version__ = '0.0.1'


def checkAnswer(answer):
    result = False
    if answer in ("N", "n", "no", "NO", "No"):
        result = True
    elif answer in ("Y", "y", "yes", "Yes", "YES"):
        result = False
    else:
        result = True
    return result

def createSqliteDb():
    noOverwrite = False
    if os.path.exists(__sqlitedb__): 
        if os.path.isfile(__sqlitedb__):
            print ("""SQLite database {0} exists already.""".format(__sqlitedb__))
       
            if sys.version_info[:2] > (3,0):
                answer = input ('Do you want to overwrite it? Yes, [N]o (default = No):')
            else:
                answer = raw_input('Do you want to overwrite it? Yes, [N]o (default = No):')
            noOverwrite = checkAnswer(answer)
        else:
            print ("""SQLite database name {0} already exists as a directory.""".format(__sqlitedb__))
            sys.exit()

    if noOverwrite:
        print ("Not going to overwrite existing SQLite db.")
        sys.exit()
    else:
        print ("create a new SQLite db: %s."%(__sqlitedb__))

    conn = None
    sqlfile = None
    try:
        if __sql__ is None:
            from pymasar.db.masarsqlite import SQL
        else:
            sqlfile = open(__sql__)
            SQL = sqlfile.read()
        if SQL is None:
            print ('SQLite script is empty. Cannot create SQLite db.')
            sys.exit()
        else:
            conn = sqlite3.connect(__sqlitedb__)
            cur = conn.cursor()
            cur.executescript(SQL)
    except sqlite3.Error, e:
        print ("Error %s:" % e.args[0])
        sys.exit(1)
    finally:
        if conn:
            conn.close()
        if sqlfile:
            sqlfile.close()
        
def usage():
    print ("""usage: createSqliteDb.py [options]

Options (which can be given in any of the forms shown):
-s  --source    source.sql [default: masar-sqlite.sql]
-db  --database sqlite.db  [default: masar.db]
-h  --help

If executed with no arguments, it creates a default sqlite3 database 
with a name masar.db, which uses sql script from masar-sqlite.sql file.

createSqliteDb.py v {0}. Copyright (c) 2011
National Synchrotron Light Source II
Brookhaven National Laboratory
Upton, New York, USA, 11973
All rights reserved.
""".format(__version__))
    sys.exit()

if __name__ == '__main__':
    args = sys.argv[1:]
    while args:
        arg = args.pop(0)
        if arg in ("-s", "--source"):
            __sql__ = args.pop(0)
            print (__sql__)
        elif arg in ("-db", "--database"):
            __sqlitedb__ = args.pop(0)
            print ("SQLite3 database: ", __sqlitedb__)
        elif arg in ("-h", "--help", "help"):
            usage()
    createSqliteDb()
