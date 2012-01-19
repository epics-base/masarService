from channelRPC import ChannelRPC as ChannelRPC
from ntnameValue import NTNameValue as NTNameValue
from nttable import NTTable as NTTable
from alarm import Alarm as Alarm
from timeStamp import TimeStamp as TimeStamp


def testRPC(function, params):
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
    print nttable
    
    nttable.getAlarm(alarm.getAlarmPy())
    print alarm;
    
    nttable.getTimeStamp(timeStamp.getTimeStampPy())
    print timeStamp;
    
    numberValues = nttable.getNumberValues()
    print "numberValues",numberValues
    
    label = nttable.getLabel()
    print "label",label
    
    i = 0
    while i < numberValues :
        value = nttable.getValue(i)
        print "value",label[i],value
        i += 1

def retrieveServiceConfigs():
    function = 'retrieveServiceConfigs'
    print ("=== test %s ===" %function)
    params = {'system': 'sr'
              }
    testRPC(function, params)
    print ("=== test %s end ===" %function)

def retrieveServiceConfigProps():
    function = 'retrieveServiceConfigProps'
    print ("=== test %s ===" %function)
    params = {'propname': 'system', 
              'configname': 'sr_qs'
              }
    testRPC(function, params)
    print ("=== test %s end ===" %function)
    
def retrieveServiceEvents():
    function = 'retrieveServiceEvents'
    print ("=== test %s ===" %function)
    params = {'configid': '1'}
    testRPC(function, params)
    print ("=== test %s end ===" %function)

def retrieveMasar():
    function = 'retrieveMasar'
    print ("=== test %s ===" %function)
    params = {'eventid': '56'}
#    params = {'eventid': '10'}
    testRPC(function, params)
    print ("=== test %s end ===" %function)

if __name__ == '__main__':
    retrieveServiceConfigs()
    retrieveServiceConfigProps()
    retrieveServiceEvents()
    retrieveMasar()
