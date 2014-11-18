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


def getLiveMachine(mc):
    params = {}
    # get a live machine with given pv list
    print '==== get live machine ===='
    pvlist = ['LTB-BI{BPM:1}LTB:MbAvgX-I',
              'LTB-BI{BPM:1}LTB:MbStdX-I',
              'LTB-BI{BPM:1}LTB:MbAvgY-I',
              'LTB-BI{BPM:1}LTB:MbStdY-I',
              'LTB-BI{BPM:1}LTB:Iavg-Calc',
              'LTB-BI{BPM:1}LTB:Istd-Calc',
              'LTB-BI{BPM:1}Rate:Update-SP',
              'LTB-BI{BPM:2}LTB:MbAvgX-I',
              'LTB-BI{BPM:2}LTB:MbStdX-I',
              'LTB-BI{BPM:2}LTB:MbAvgY-I',
              'LTB-BI{BPM:2}LTB:MbStdY-I',
              'LTB-BI{BPM:2}LTB:Iavg-Calc',
              'LTB-BI{BPM:2}LTB:Istd-Calc',
              'LTB-BI{BPM:2}Rate:Update-SP']
    for pv in pvlist:
        params[pv] = pv
    result = mc.getLiveMachine(params)
    return result


if __name__ == "__main__":
    channel='masarService'
    mc = masarClient.client(channelname=channel)

    res1 = saveMasarSnapshot(mc)
    print "event id:", res1[0]
    print "value:", res1[2]

    res2 = retrieveMasarSnapshot(mc, res1[0])
    print "value:", res2[1]

    # Call this function before exit.
    sys.exit(epicsExit())
