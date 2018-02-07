
import logging
_log = logging.getLogger(__name__)

from types import NoneType

import psycopg2
import dbsettings_postgres

try:
    import cPickle as pickle
except ImportError:
    import pickle

import numpy, json

# like buildin group_concat() which also does de-duplication, but doesn't preserve order
class ConcatUnique(object):
    def __init__(self):
        self.values = set()
    def step(self, V):
        self.values.add(str(V))
    def finalize(self):
        return ', '.join(map(str,self.values))

"""
def encodeValue(V):
   
    if isinstance(V, (int, long, float, unicode, bytes, list, tuple, NoneType)):
        return V # store directly
    elif isinstance(V, numpy.ndarray):
        return json.dumps(numpy.asarray(V).tolist())
    else:
        _log.exception("Error encoding %s", V)
        raise ValueError("Can't encode type %s"%type(V))

def decodeValue(S):
        return numpy.asarray(json.loads(S))
        
"""

def     connect():
    try:
        conn = psycopg2.connect(dbname=dbsettings_postgres.name, 
                                user=dbsettings_postgres.user, 
                                password=dbsettings_postgres.password, 
                                host=dbsettings_postgres.host, 
                                port=dbsettings_postgres.port)
        cursor = conn.cursor()
        for command in _commands:
            cursor.execute(command)
            
        cursor.close();
        conn.commit()
        
    except:
        conn.close()
        raise
    else:
        return conn

# We would like to add 'UNIQUE(name, )' to config,
# but this is difficult for sqlite to handle w/ update and distinct-ness of NULL
#
# so this must be ensured by our logic (cf. storeServiceConfig())
#
#  https://www.sqlite.org/nulls.html

_commands = ("""
CREATE TABLE IF NOT EXISTS config (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  next INTEGER REFERENCES config(id) ON DELETE CASCADE,
  created TEXT NOT NULL,
  active INTEGER NOT NULL DEFAULT 1,
  description TEXT NOT NULL,
  system TEXT
);""",

"""CREATE INDEX IF NOT EXISTS config_name ON config(name);""",


"""CREATE TABLE IF NOT EXISTS config_pv (
  id SERIAL PRIMARY KEY,
  config INTEGER REFERENCES config(id) ON DELETE CASCADE NOT NULL,
  name TEXT NOT NULL,
  tags TEXT NOT NULL DEFAULT '',
  groupName TEXT NOT NULL DEFAULT '',
  readonly INT NOT NULL DEFAULT 0,
  UNIQUE(config, name)
);""",

"""CREATE INDEX IF NOT EXISTS config_pv_config ON config_pv(config);""",
"""CREATE UNIQUE INDEX IF NOT EXISTS config_pv_config_name ON config_pv(config, name);""",

"""CREATE TABLE IF NOT EXISTS event (
  id SERIAL PRIMARY KEY,
  config INTEGER REFERENCES config(id) ON DELETE CASCADE NOT NULL,
  created TEXT NOT NULL,
  userName TEXT,
  comment TEXT,
  approve INTEGER
);""",

"""CREATE INDEX IF NOT EXISTS event_config ON event(config);""",
"""CREATE INDEX IF NOT EXISTS event_config_created ON event(config,created);""",

"""CREATE TABLE IF NOT EXISTS event_pv (
  id SERIAL PRIMARY KEY,
  event INTEGER REFERENCES event(id) ON DELETE CASCADE NOT NULL,
  pv INTEGER REFERENCES config_pv(id) ON DELETE CASCADE NOT NULL,
  dtype INTEGER NOT NULL,
  severity INTEGER NOT NULL,
  status INTEGER NOT NULL,
  time INTEGER NOT NULL,
  timens INTEGER NOT NULL,
  value TEXT NOT NULL DEFAULT '0',
  UNIQUE(event, pv)
);""",

"""CREATE INDEX IF NOT EXISTS event_pv_event ON event_pv(event);""",
"""CREATE UNIQUE INDEX IF NOT EXISTS event_pv_event_pv ON event_pv(event, pv);""")
