import sys

from masarclient import masarClient
from masarclient.channelRPC import epicsExit


def getSystemList(mc):
    # retrieve all system defined in masar configuration
    print '==== retrieve system list ===='
    result = mc.retrieveSystemList()
    return result


def getMasarConfigs(mc):
    # retrieve all configuration with given constrains
    print '==== retrieve service config ===='
    params = {'system': 'LTD2'}
    result = mc.retrieveServiceConfigs(params)
    return result


def getMasarEvent(mc):
    # retrieve all events list with given constrains
    print '==== retrieve service event list ===='
    params = {'configid': '1'}
    result = mc.retrieveServiceEvents(params)
    return result


def retrieveMasarSnapshot(mc, eid):
    # retrieve snapshot data with event_id = 1
    print '==== retrieve snapshot ===='
    params = {'eventid': str(eid)}
    result = mc.retrieveSnapshot(params)
    return result


def saveMasarSnapshot(mc):
    # get a machine preview and save it into database
    print '==== machine preview snapshot ===='
    params = {'configname': 'test',
              'servicename': 'masar'}
    result = mc.saveSnapshot(params)
    return result


def approveMasarSnapshot(mc, eid):
    # approve a machine preview
    print '==== approve machine preview snapshot ===='
    params = {'eventid':    str(eid),
              'configname': 'test',
              'user':       'test',
              'desc':       'this is a good snapshot, and I approved it.'}
    result = mc.updateSnapshotEvent(params)
    return result


def getLiveMachine(mc, pvlist):
    params = {}
    # get a live machine with given pv list
    print '==== get live machine ===='
    for pv in pvlist:
        params[pv] = pv
    result = mc.getLiveMachine(params)
    return result


if __name__ == "__main__":
    channel = 'masarService'
    mc = masarClient.client(channelname=channel)

    res1 = saveMasarSnapshot(mc)
    print res1
    print "event id:", res1[0]
    print "value:", res1[2]

    res2 = retrieveMasarSnapshot(mc, res1[0])
    res2 = retrieveMasarSnapshot(mc, 17)
    print "name:", res2[0][-10:]
    print "value:", res2[1][-10:]

    pvlist = ["masarExampleCharArray",
              "masarExampleFloatArray",
              "masarExampleShortArray",
              "masarExampleUCharArray"]
    print "((pv name),(value),(isConnected),(secondsPastEpoch),(nanoSeconds),(timeStampTag),(alarmSeverity),(alarmStatus),(alarmMessage))"
    for i in range(len(pvlist)):
        print getLiveMachine(mc, pvlist[i:])
    # Call this function before exit.
    sys.exit(epicsExit())
