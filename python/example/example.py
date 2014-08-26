"""An example shows how to create one MongoDB masar configuration."""
__author__ = 'shengb'

import numpy as np

from pymasarmongo.db import utils
import pymasarmongo


def saveconfig2mongo(mongoconn, collection, name, desc, system, pvlist):

    pymasarmongo.pymasarmongo.pymasar.saveconfig(mongoconn, collection,
                                                 name,
                                                 desc=desc,
                                                 system=system,
                                                 pvlist=pvlist)

if __name__ == "__main__":
    mongoconn, collection = utils.conn()
    #print mongoconn

    saveconfig2mongo(mongoconn, collection,
                     "test configuration",
                     desc="this is for test only",
                     system="test",
                     pvlist={"names": list(np.loadtxt("examplepvlist.txt", dtype=str, comments="#"))})

    utils.close(mongoconn)

