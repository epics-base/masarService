'''
Created on Jan 3, 2012

@author: shengb
'''

import os
import sys

import sqlite3
from pymasar.pvgroup.pvgroup import (savePvGroup)
from pymasar.pvgroup.pv import (saveGroupPvs)
from pymasar.service.service import (saveService)
from pymasar.service.serviceconfig import (saveServiceConfig, saveServicePvGroup)

try:
    __db=os.environ['MASAR_SQLITE_DB']
except KeyError:
    raise

__version__ = 'beta1'
__service = 'masar'

from settings import (pvgroups, configs, pvg2config)

def usage():
    print("""usage: setmanardb.py [option]

command option:
-s  --service    [service name]
-h  --help       print out this message


masar.py v {0}. Copyright (c) 2011 Brookhaven National Laboratory. All rights reserved.
""".format(__version__))
    sys.exit()
    
args = sys.argv[1:]
for i in range(len(args)):
    arg = args[i]
    if arg in ("-h", "--help"):
        usage()
    elif arg in ("-s", "--service"):
        i += 1
        if i >=len(args):
            print("user default service name: masar")
            sys.exit()
        __service = args[i]
    else:
        print ('Unknown option.')

class Setmasardb():
    
    def __init__(self, db, filepath, servicename='masar', servicedesc= 'machine snapshot, archiving, and retrieve service'):
        self.servicename=servicename
        self.servicedesc = servicedesc
        self.conn = sqlite3.connect(db)
        self.__filepath = filepath

    def savePvGroups(self):        
        for k,v in sorted(pvgroups.items()):
            __file = "/".join((self.__filepath, v[0]))
            if os.path.exists(__file): 
                if os.path.isfile(__file):
                    pvlist = None
                    try:
                        f = open(__file, 'r')
                        pvlist = f.read()
                        pvlist = pvlist.split('\n')
                        if len(pvlist[len(pvlist)-1]) == 0:
                            pvlist = pvlist[:-1]
                        savePvGroup(self.conn, k, func=v[1])
                        saveGroupPvs(self.conn, k, pvlist)
                    finally:
                        if f:
                            f.close()
                    print ('Finished saving pvs in {0}'.format(v[0]))
                else:
                    raise Exception ("""PV list ({0}) is not a file.""".format(v[0]))
            else:
                raise Exception ("""Can not find pv list file ({0})""".format(v[0]))
    
    def saveServiceConfig(self):
        for k, v in sorted(configs.items()):
            try:
                saveServiceConfig(self.conn, self.servicename, k, configdesc = v[0], system=v[1])
                pvg = pvg2config[k]
                saveServicePvGroup(self.conn, k, pvg)
            except:
                print ("configuration name (%s) exists already." %(k))
    
    def saveService(self):
        saveService(self.conn, self.servicename, desc=self.servicedesc)
    
    def save(self):
        self.conn.commit()
        self.conn.close()
        
def main():
    PV_LIST_ROOT = '/'.join((os.path.abspath(os.path.dirname(__file__)), 'pvs'))
    if sys.version_info[:2] > (3,0):
        root = input ('Please give absolute ROOT PATH of your pv list files \n[default: %s]:\n'%(PV_LIST_ROOT))
    else:
        root = raw_input('Please give absolute ROOT PATH of your pv list files \n[default: %s]:\n'%(PV_LIST_ROOT))
    root = root.strip()
    if root != '':
        PV_LIST_ROOT = root
        print ("Use new ROOT: %s"%(PV_LIST_ROOT))
    else:
        print ("Not ROOT directory is specified. Use default.")

    mdb = Setmasardb(__db, PV_LIST_ROOT)
    try:
        mdb.savePvGroups()
    except:
        raise
    try:
        mdb.saveService()
    except:
        raise
    try:
        mdb.saveServiceConfig()
    except:
        raise
    try:
        mdb.save()
    except:
        raise

if __name__ == '__main__':
    main()