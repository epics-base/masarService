import sys

from masarclient import masarClient
from masarclient.channelRPC import epicsExit

channel='masarService'

mc = masarClient.client( channelname = channel)

# retrieve all system defined in masar configuration
print '==== retrieve system list ===='
result = mc.retrieveSystemList()
print result

# retrieve all configuration with given constrains
print '==== retrieve service config ===='
params = {'system': 'LTD2'}
result = mc.retrieveServiceConfigs(params)
print result

# retrieve all events list with given constrains
print '==== retrieve service event list ===='
params = {'configid': '1'}
result = mc.retrieveServiceEvents(params)
print result

# retrieve all events list with given constrains
print '==== retrieve snapshot ===='
params = {'eventid': '1'}
result = mc.retrieveSnapshot(params)
print result

# get a machine preview and save it into database
print '==== machine preview snapshot ===='
params = {'configname': 'LTD2_SC_Daily_All',
          'servicename': 'masar'}
result = mc.saveSnapshot(params)
print result

# approve a machine preview
print '==== approve machine preview snapshot ===='
params = {'eventid':    '1',
          'configname': 'LTD2_SC_Daily_All',
          'user':       'test',
          'desc':       'this is a good snapshot, and I approved it.'}
result = mc.updateSnapshotEvent(params)
print result

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
print result

# Call this function before exit.
sys.exit(epicsExit())
