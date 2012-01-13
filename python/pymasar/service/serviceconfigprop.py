'''
Created on Dec 23, 2011

@author: shengb
'''

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sqlite3

from pymasar.utils import checkConnection
from pymasar.service.serviceconfig import (retrieveServiceConfigs)

def saveServiceConfigProp(conn, propname=None, propvalue=None, servicename=None, configname=None):
    """
    save a service config property, for example, which system this config belongs to.
    
    >>> import sqlite3
    >>> from pymasar.service.service import (saveService, retrieveServices)
    >>> from pymasar.service.serviceconfig import (saveServiceConfig, retrieveServiceConfigs)
    >>> from pymasar.db.masarsqlite import (SQL)
    >>> conn = sqlite3.connect(":memory:")
    >>> cur = conn.cursor()
    >>> result = cur.executescript(SQL)
    >>> saveService(conn, 'masar1', desc='non-empty description')
    1
    >>> saveService(conn, 'masar2', desc='non-empty description')
    2
    >>> saveServiceConfig(conn, 'masar1', 'orbit C01', 'BPM horizontal readout for storage ring')
    1
    >>> saveServiceConfig(conn, 'masar2', 'booster orbit', 'Horizontal orbit for booster ring')
    2
    >>> saveServiceConfigProp(conn, 'system', 'SR', 'masar1', 'orbit C01')
    1
    >>> saveServiceConfigProp(conn, 'system', 'booster', 'masar2', 'booster orbit')
    2
    >>> saveServiceConfigProp(conn, 'system', 'booster', 'masar2', 'booster orbit')
    2
    >>> conn.close()
    """
    if servicename is None or configname is None:
        raise Exception('service or service config is empty. Can not associate the event with service and its config.')
    if propname is None or propvalue is None:
        raise Exception('Property name and value can not be empty.')
    
    checkConnection(conn)
    
    serviceconfigid = retrieveServiceConfigs(conn, servicename=servicename, configname=configname)[1:]
    if len(serviceconfigid) > 0:
        serviceconfigid = serviceconfigid[0][0]
    else:
        raise Exception('Can not find service config (%s) with service (%s)' %(configname, servicename))
    sql = '''
    insert into service_config_prop (service_config_prop_id, service_config_id, service_config_prop_name, service_config_prop_value)
    values (?, ?, ?, ?)
    '''
    try:
        cur = conn.cursor()
        # check this entity exists or not.
        cur.execute('select service_config_prop_id from service_config_prop where service_config_id = ? and service_config_prop_name = ? and service_config_prop_value = ?',
                    (serviceconfigid, propname, propvalue, ))
        result = cur.fetchone()
        if result is None:
            cur.execute(sql, (None, serviceconfigid, propname, propvalue))
            result = cur.lastrowid
        else:
            result = result[0]
    except sqlite3.Error, e:
        print ('Error %s' %e.args[0])
        raise
    return result

def retrieveServiceConfigProps(conn, propname=None, servicename=None, configname=None):
    """
    retrieve a service config property, for example, which system this config belongs to.
    
    >>> import sqlite3
    >>> from pymasar.service.service import (saveService, retrieveServices)
    >>> from pymasar.service.serviceconfig import (saveServiceConfig, retrieveServiceConfigs)
    >>> from pymasar.db.masarsqlite import (SQL)
    >>> conn = sqlite3.connect(":memory:")
    >>> cur = conn.cursor()
    >>> result = cur.executescript(SQL)
    >>> saveService(conn, 'masar1', desc='non-empty description')
    1
    >>> saveService(conn, 'masar2', desc='non-empty description')
    2
    >>> saveServiceConfig(conn, 'masar1', 'orbit C01', 'BPM horizontal readout for storage ring')
    1
    >>> saveServiceConfig(conn, 'masar2', 'booster orbit', 'Horizontal orbit for booster ring')
    2
    >>> saveServiceConfigProp(conn, 'system', 'SR', 'masar1', 'orbit C01')
    1
    >>> saveServiceConfigProp(conn, 'system', 'booster', 'masar2', 'booster orbit')
    2
    >>> retrieveServiceConfigProps(conn)[1:]
    [(1, 1, u'system', u'SR'), (2, 2, u'system', u'booster')]
    >>> retrieveServiceConfigProps(conn, propname='system')[1:]
    [(1, 1, u'system', u'SR'), (2, 2, u'system', u'booster')]
    >>> retrieveServiceConfigProps(conn, propname='system', servicename='masar1', configname='orbit C01')[1:]
    [(1, 1, u'system', u'SR')]
    >>> retrieveServiceConfigProps(conn, propname='system', servicename='masar2', configname='booster orbit')[1:]
    [(2, 2, u'system', u'booster')]
    >>> conn.close()
    """
    checkConnection(conn)
    
    serviceconfigids = retrieveServiceConfigs(conn, servicename=servicename, configname=configname)[1:]
    serviceconfigid = []
    if len(serviceconfigids) > 0:
        for ids in serviceconfigids:
            serviceconfigid.append(ids[0])
    else:
        raise Exception('Can not find service config (%s) with service (%s)' %(configname, servicename))
    sql = '''
    select service_config_prop_id, service_config_id, service_config_prop_name, service_config_prop_value from service_config_prop 
    '''
    results = []
    try:
        for configid in serviceconfigid:
            cur = conn.cursor()
            if configid is None and propname is None:
                cur.execute(sql)
            elif serviceconfigid is None:
                cur.execute(sql + ' where service_config_prop_name like ?', (propname,))
            elif propname is None:
                cur.execute(sql + ' where service_config_id = ?', (configid,))
            else:
                cur.execute(sql + ' where service_config_id = ? and service_config_prop_name like ?', (configid, propname,))
            result = cur.fetchall()
            if len(result) > 0:
                results.append(result[0])
            else:
                print ('Did not find matched service config property.')
    except sqlite3.Error, e:
        print ('Error %s' %e.args[0])
        raise
    results = [('service_config_prop_id', 'service_config_id', 'service_config_prop_name', 'service_config_prop_value'),] + results[:]
    return results

if __name__ == '__main__':
    import doctest
    doctest.testmod()