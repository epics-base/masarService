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
__sql__ = 'sqlite/masar-sqlite.sql'

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
        print ("create a new SQLite db.")

    con = None
    try:
        conn = sqlite3.connect(__sqlitedb__)
        cur = conn.cursor()
        SQL = open(__sql__).read()
        cur.executescript(SQL)
    except sqlite3.Error, e:
        print ("Error %s:" % e.args[0])
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    createSqliteDb()
