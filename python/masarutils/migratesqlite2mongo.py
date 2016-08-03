#import os
from masarserver.dslPY import DSL
from masarserver.dslPY import masarconfig
import pymasarmongo

#import numpy as np

SHOWTIME = False
import time


def saveconfig2mongo(dsl, mongoconn, collection):
    if SHOWTIME:
        start0 = time.time()
    res = dsl.request({"function": "retrieveServiceConfigs"})[0]
    if SHOWTIME:
        print "Get configurations from SQLite: %s seconds" % (time.time() - start0)
    cidx = pymasarmongo.pymasarmongo.pymasar.retrieveconfig(mongoconn, collection)
    cidx = [v['configidx'] for v in cidx]

    for r in res[1:]:
        configidx = r[0]
        if configidx in cidx:
            print "configuration index # (%s) exists already" % configidx
            continue
        name = r[1]
        desc = r[2]
        date = r[3]
        status = r[5]
        if SHOWTIME:
            start1 = time.time()
        system = dsl.request({"function": "retrieveServiceConfigProps", "configname": r[1]})
        system = system[0][1][3]
        pvs = dsl.retrieveChannelNames({"configname": r[1]})
        if SHOWTIME:
            print "Get system and channels from SQLite: %s seconds" % (time.time() - start1)
        pvlist = {"names": pvs}
        if SHOWTIME:
            start2 = time.time()
        pymasarmongo.pymasarmongo.pymasar.saveconfig(mongoconn, collection, name,
                                                     configidx=configidx,
                                                     desc=desc,
                                                     created_on=date,
                                                     system=system,
                                                     pvlist=pvlist,
                                                     status=status)
        if SHOWTIME:
            print "Insert one into MongoDB: %s seconds" % (time.time() - start2)


def savedata2mongo(dsl, mongoconn, collection):
    if SHOWTIME:
        start0 = time.time()
    res = dsl.request({"function": "retrieveServiceEvents"})[0]
    if SHOWTIME:
        print "Get event headers from SQLite: %s seconds" % (time.time() - start0)
    eidx = pymasarmongo.pymasarmongo.pymasar.retrieveevents(mongoconn, collection)
    eidx = [v['eventidx'] for v in eidx]
    #datasize = []
    for r in res[1:]:
        # print r[4]
        # continue
        #
        if r[0] in eidx:
            print "event index # (%s) exists already" % r[0]
            continue
        if SHOWTIME:
            start1 = time.time()
        data = dsl.request({"function": "retrieveSnapshot", "eventid": r[0]})
        #datasize.append(np.array(data[0][1][1:], dtype=object).nbytes)
        if SHOWTIME:
            print "Get event data from SQLite: %s seconds" % (time.time() - start1)
        # Got a 2-D array [[(u'user tag', u'event UTC time', u'service config name', u'service name'),
        #                   (u'pv name', u'string value', u'double value', u'long value', u'dbr type',
        #                    u'isConnected', u'secondsPastEpoch', u'nanoSeconds', u'timeStampTag', u'alarmSeverity',
        #                    u'alarmStatus', u'alarmMessage', u'is_array', u'array_value')],
        #                   [(header), (pv 1 w/ meta data), (pv 2 w/ meta data),]
        #                 ]
        if SHOWTIME:
            start2 = time.time()
        pymasarmongo.pymasarmongo.pymasar.saveevent(mongoconn, collection,
                                                    eventidx=r[0],
                                                    configidx=r[1],
                                                    comment=r[2],
                                                    created_on=r[3],
                                                    username=r[4],
                                                    approval=True,
                                                    masar_data=data[0][1][1:]
                                                    )
        if SHOWTIME:
            print "Insert one into MongoDB: %s seconds" % (time.time() - start2)
    #print datasize


if __name__ == "__main__":
    dsl = DSL()
    if masarconfig.has_section("mongodb"):
        mongodb = masarconfig.get("mongodb", "database")
        host = masarconfig.get("mongodb", "host")
        port = masarconfig.get("mongodb", "port")
        mongoconn, collection = pymasarmongo.db.utils.conn(host=host, port=port, db=mongodb)
    else:
        mongoconn, collection = pymasarmongo.db.utils.conn()

    time0 = time.time()
    saveconfig2mongo(dsl, mongoconn, collection)
    savedata2mongo(dsl, mongoconn, collection)
    print "It costs about %s seconds to migrate whole data from SQLite" %(time.time()-time0)

    pymasarmongo.db.utils.close(mongoconn)

    print "finished"
