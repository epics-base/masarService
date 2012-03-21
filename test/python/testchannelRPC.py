import sys

from masarclient.channelRPC import ChannelRPC as ChannelRPC
from masarclient.channelRPC import epicsExit
from masarclient.ntnameValue import NTNameValue as NTNameValue
from masarclient.nttable import NTTable as NTTable
from masarclient.alarm import Alarm as Alarm
from masarclient.timeStamp import TimeStamp as TimeStamp


def __clientRPC(function, params):
    alarm = Alarm()
    timeStamp = TimeStamp()

    ntnv = NTNameValue(function,params)
    print ntnv
    
    # now do issue + wait
    channelRPC = ChannelRPC("masarService","record[process=true]field()")
    channelRPC.issueConnect()
    if not channelRPC.waitConnect(1.0) :
        print channelRPC.getMessage()
        exit(1)
    channelRPC.issueRequest(ntnv.getNTNameValue(),False)
    result = channelRPC.waitRequest()
    if(result==None) :
        print channelRPC.getMessage()
        exit(1)
    nttable = NTTable(result)
#    print nttable
    
    nttable.getAlarm(alarm.getAlarmPy())
#    print alarm;
    
    nttable.getTimeStamp(timeStamp.getTimeStampPy())
#    print timeStamp;
    
#    numberValues = nttable.getNumberValues()
#    print "numberValues",numberValues
#    
#    label = nttable.getLabel()
#    print "label",label
#    
#    i = 0
#    while i < numberValues :
#        value = nttable.getValue(i)
#        print "value",label[i],value
#        i += 1
    return nttable

def retrieveSystemList():
    function = 'retrieveServiceConfigProps'
    print ("=== test %s ===" %function)
    params = {}
    nttable = __clientRPC(function, params)
    print (nttable)
    print ("=== test %s end ===" %function)


def retrieveServiceConfigs():
    function = 'retrieveServiceConfigs'
    print ("=== test %s ===" %function)
    params = {'system': 'sr'
              }
    __clientRPC(function, params)
    print ("=== test %s end ===" %function)

def retrieveServiceConfigProps():
    function = 'retrieveServiceConfigProps'
    print ("=== test %s ===" %function)
    params = {'propname': 'system', 
              'configname': 'sr_qs'
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
    nttable = __clientRPC(function, params)
    # should return 
    # 'pv name': 0
    # 'string value': 1
    # 'double value': 2
    # 'long value': 3
    # 'dbr type': 4
    # 'isConnected': 5
    # 'secondsPastEpoch': 6
    # 'nanoSeconds': 7
    # 'timeStampTag': 8
    # 'alarmSeverity': 9
    # 'alarmStatus': 10
    # 'alarmMessage': 11
    # 'is_array': 12
    # 'array_value'13
    # numbers = nttable.getNumberValues()
    label = nttable.getLabel()
    
    if label[0] == 'status' and not nttable.getValue(0)[0]:
        print (nttable)
    else:
        dbr_type = nttable.getValue(4)
        is_array = nttable.getValue(12)
        print (is_array)
        raw_array_value = nttable.getValue(13)
        print (raw_array_value)
        array_value = []
        epicsint    = [1, 4, 5]
        epicsString = [0]
        epicsDouble = [2, 6]
    
        for i in range(len(is_array)):
            if dbr_type[i] in epicsint:
                array_value.append(raw_array_value[i][2])
            elif dbr_type[i] in epicsDouble:
                array_value.append(raw_array_value[i][1])
            elif dbr_type[i] in epicsString:
                array_value.append(raw_array_value[i][0])
        print (array_value)
        print (len(is_array), len(array_value))
    print ("=== test %s end ===" %function)

def saveSnapshot():
    function = 'saveSnapshot'
    print ("=== test %s ===" %function)
#    params = {'configname': 'sr_bpm',
#              'servicename': 'masar'}
    params = {'configname': 'sr_test',
              'servicename': 'masar'}
    nttable = __clientRPC(function, params)
    print(nttable)
    print ("=== test %s end ===" %function)

if __name__ == '__main__':
    try:
        retrieveSystemList()
        retrieveServiceConfigs()
        retrieveServiceConfigProps()
        retrieveServiceEvents()
        retrieveSnapshot()
        saveSnapshot()
    except:
        pass
    sys.exit(epicsExit())
