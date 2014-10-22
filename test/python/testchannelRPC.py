import sys
import traceback

from masarclient.channelRPC import ChannelRPC as ChannelRPC
from masarclient.channelRPC import epicsExit
from masarclient.ntscalar import NTScalar
from masarclient.ntnameValue import NTNameValue
from masarclient.ntmultiChannel import NTMultiChannel
from masarclient.nttable import NTTable
from masarclient.alarm import Alarm
from masarclient.timeStamp import TimeStamp


def __clientRPC(function, params):
    alarm = Alarm()
    timeStamp = TimeStamp()

    ntnv = NTNameValue(function, params)

    # now do issue + wait
    channelRPC = ChannelRPC("masarService")
    channelRPC.issueConnect()
    if not channelRPC.waitConnect(1.0):
        print "error when waiting connection.", channelRPC.getMessage()
        exit(1)
    channelRPC.issueRequest(ntnv.getNTNameValue(), False)
    result = channelRPC.waitResponse()
    if result is None:
        print channelRPC.getMessage()
        exit(1)
#    print "problem to get nttable using getNTTable()"
    if function in ["retrieveSnapshot", "getLiveMachine", "saveSnapshot"]:
        result = NTMultiChannel(result)
    elif function in ["retrieveServiceEvents", "retrieveServiceConfigs", "retrieveServiceConfigProps"]:
        result = NTTable(result)
        label = result.getLabels()
        print "label", label
        print result.getPVStructure()
    elif function == "updateSnapshotEvent":
        result = NTScalar(result)
#    print "Problem above"
    print result

    result.getAlarm(alarm)
    # print alarm

    result.getTimeStamp(timeStamp)
    # print timeStamp

    # numberValues = result.getNumberValues()
    # print "numberValues", numberValues

#
#    i = 0
#    while i < numberValues :
#        value = nttable.getValue(i)
#        print "value",label[i],value
#        i += 1
    return result

def retrieveSystemList():
    function = 'retrieveServiceConfigProps'
    print ("=== test %s (system list)===" %function)
    params = {}
    nttable = __clientRPC(function, params)
    print ("=== test %s end ===" %function)


def retrieveServiceConfigs():
    function = 'retrieveServiceConfigs'
    print ("=== test %s configs===" %function)
    params = {'system': 'all'
              }
    result = __clientRPC(function, params)
    print ("=== test %s end ===" %function)

def retrieveServiceConfigProps():
    function = 'retrieveServiceConfigProps'
    print ("=== test %s ===" %function)
    params = {'propname': 'system', 
              'configname': 'SR_All_SCR_20140421'
              }
    __clientRPC(function, params)
    print ("=== test %s end ===" %function)
    
def retrieveServiceEvents():
    function = 'retrieveServiceEvents'
    print ("=== test %s ===" %function)
    params = {'configid': '1'}
    __clientRPC(function, params)
    print ("=== test %s end ===" %function)

def retrieveSnapshot():
    function = 'retrieveSnapshot'
    print ("=== test %s ===" %function)
    params = {'eventid': '365'}
#    params = {'eventid': '132'}
    ntmultichannels = __clientRPC(function, params)
    result = ntmultichannels
    print "All: ", ntmultichannels
    print "PV Values:", ntmultichannels.getValue()
    print "PV Names:", ntmultichannels.getChannelName()
    print "Structure", ntmultichannels.getPVStructure()
    # # should return
    # # 'pv name': 0
    # # 'string value': 1
    # # 'double value': 2
    # # 'long value': 3
    # # 'dbr type': 4
    # # 'isConnected': 5
    # # 'secondsPastEpoch': 6
    # # 'nanoSeconds': 7
    # # 'timeStampTag': 8
    # # 'alarmSeverity': 9
    # # 'alarmStatus': 10
    # # 'alarmMessage': 11
    # # 'is_array': 12
    # # 'array_value'13
    # # numbers = nttable.getNumberValues()
    # print result
    # print ntmultichannels.getNumberChannel()
    # label = result.getLabels()
    #
    # if label[0] == 'status' and not ntmultichannels.getValue(0)[0]:
    #     print (ntmultichannels)
    # else:
    #     dbr_type = ntmultichannels.getValue(4)
    #     is_array = ntmultichannels.getValue(12)
    #     print (is_array)
    #     raw_array_value = ntmultichannels.getValue(13)
    #     print (raw_array_value)
    #     array_value = []
    #     epicsint    = [1, 4, 5]
    #     epicsString = [0]
    #     epicsDouble = [2, 6]
    #
    #     for i in range(len(is_array)):
    #         if dbr_type[i] in epicsint:
    #             array_value.append(raw_array_value[i][2])
    #         elif dbr_type[i] in epicsDouble:
    #             array_value.append(raw_array_value[i][1])
    #         elif dbr_type[i] in epicsString:
    #             array_value.append(raw_array_value[i][0])
    #     print (array_value)
    #     print (len(is_array), len(array_value))
    print ("=== test %s end ===" %function)

def saveSnapshot():
    function = 'saveSnapshot'
    print ("=== test %s ===" %function)
#    params = {'configname': 'sr_bpm',
#              'servicename': 'masar'}
    params = {'configname': 'wf_test',
              'servicename': 'masar'}
    ntmultichannels = __clientRPC(function, params)
    print(ntmultichannels)
    print ("=== test %s end ===" %function)

if __name__ == '__main__':
    try:
        # retrieveSystemList()
        # retrieveServiceConfigs()
        # retrieveServiceConfigProps()
        # retrieveServiceEvents()
        retrieveSnapshot()
        # saveSnapshot()
    except AttributeError:
        print traceback.print_exc()
        pass
    sys.exit(epicsExit())
