
import logging
_log = logging.getLogger(__name__)

from types import NoneType
import sqlite3, json, sys, zlib

try:
    import cPickle as pickle
except ImportError:
    import pickle

import numpy

# like buildin group_concat() which also does de-duplication, but doesn't preserve order
class ConcatUnique(object):
    def __init__(self):
        self.values = set()
    def step(self, V):
        self.values.add(str(V))
    def finalize(self):
        return ', '.join(map(str,self.values))

def encodeValue(V):
    """Mangle python type for storage in event_pv.value
    """
    if isinstance(V, (int, long, float, unicode, bytes, NoneType)):
        return V # store directly
    elif isinstance(V, (list, tuple, numpy.ndarray)):
        return buffer(zlib.compress(pickle.dumps(numpy.asarray(V))))
    else:
        _log.exception("Error encoding %s", V)
        raise ValueError("Can't encode type %s"%type(V))

def decodeValue(S):
    if isinstance(S, buffer):
        return pickle.loads(zlib.decompress(S))
    else:
        return S

def connect(fname):
    conn = sqlite3.connect(fname,
                           isolation_level='DEFERRED',
                           detect_types=sqlite3.PARSE_COLNAMES)
    try:
        conn.create_aggregate('py_concat_unique', 1, ConcatUnique)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        C = conn.cursor()
        C.execute("PRAGMA user_version;")
        ver = C.fetchone()[0]
        if ver==0:
            _log.info("Initialize new database")
            C.executescript(_schema)
        elif ver!=1:
            raise RuntimeError(".db has newer schema version %d"%ver)
        else:
            _log.debug("Use existing database")
        C.execute("PRAGMA user_version=1;")
    except:
        conn.close()
        raise
    else:
        return conn

# We would like to add 'UNIQUE(name, next)' to config,
# but this is difficult for sqlite to handle w/ update and distinct-ness of NULL
#
# so this must be ensured by our logic (cf. storeServiceConfig())
#
#  https://www.sqlite.org/nulls.html

_schema = """
CREATE TABLE config (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  next REFERENCES config(id) ON DELETE CASCADE,
  created TEXT NOT NULL,
  active INTEGER NOT NULL DEFAULT 1,
  desc TEXT NOT NULL,
  system TEXT
);
CREATE INDEX config_name ON config(name);
CREATE INDEX config_name_supercede ON config(name, next);

CREATE TABLE config_pv (
  id INTEGER PRIMARY KEY,
  config REFERENCES config(id) ON DELETE CASCADE NOT NULL,
  name TEXT NOT NULL,
  tags TEXT NOT NULL DEFAULT "",
  groupName TEXT NOT NULL DEFAULT "",
  readonly INT NOT NULL DEFAULT 0,
  UNIQUE(config, name)
);
CREATE INDEX config_pv_config ON config_pv(config);
CREATE UNIQUE INDEX config_pv_config_name ON config_pv(config, name);

CREATE TABLE event (
  id INTEGER PRIMARY KEY,
  config REFERENCES config(id) ON DELETE CASCADE NOT NULL,
  created TEXT NOT NULL,
  user TEXT,
  comment TEXT,
  approve INTEGER
);
CREATE INDEX event_config ON event(config);
CREATE INDEX event_config_created ON event(config,created);

CREATE TABLE event_pv (
  id INTEGER PRIMARY KEY,
  event REFERENCES event(id) ON DELETE CASCADE NOT NULL,
  pv REFERENCES config_pv(id) ON DELETE CASCADE NOT NULL,
  dtype INTEGER NOT NULL,
  severity INTEGER NOT NULL,
  status INTEGER NOT NULL,
  time INTEGER NOT NULL,
  timens INTEGER NOT NULL,
  value NOT NULL,
  UNIQUE(event, pv)
);
CREATE INDEX event_pv_event ON event_pv(event);
CREATE UNIQUE INDEX event_pv_event_pv ON event_pv(event, pv);
"""
