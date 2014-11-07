from masarclient.gatherV3Data import GatherV3Data as GatherV3Data
from masarclient.ntmultiChannel import NTMultiChannel as NTMultiChannel
from masarclient.alarm import Alarm as Alarm
from masarclient.timeStamp import TimeStamp as TimeStamp


if __name__ == '__main__':
    names = (
        'masarExample0000',
        'masarExample0001',
        'masarExample0002',
        'masarExample0004',
        'masarExampleCharArray',
        'masarExampleStringArray',
        'masarExampleLongArray',
        'masarExampleDoubleArray',
        )
    gatherV3Data = GatherV3Data(names)
    gatherV3Data.connect(2.0)
    gatherV3Data.get()
    pvStructure = gatherV3Data.getPVStructure()
    ntmultiChannel = NTMultiChannel(pvStructure)
    print ntmultiChannel
    alarm = Alarm()
    ntmultiChannel.getAlarm(alarm)
    print "alarm:" ,alarm
    timeStamp = TimeStamp()
    ntmultiChannel.getTimeStamp(timeStamp)
    print "timeStamp:",timeStamp
    print "numberChannel:" ,ntmultiChannel.getNumberChannel();
    print "value:"
    print ntmultiChannel.getValue();
    print "channelName"
    print ntmultiChannel.getChannelName();
    print "isConnected:"
    print ntmultiChannel.getIsConnected();
    print "severity:"
    print ntmultiChannel.getSeverity();
    print "status:"
    print ntmultiChannel.getStatus();
    print "message:"
    print ntmultiChannel.getMessage();
    print "seconds:"
    print ntmultiChannel.getSecondsPastEpoch();
    print "nanoseconds:"
    print ntmultiChannel.getNanoseconds();
    print "userTag:"
    print ntmultiChannel.getUserTag();
    print "descriptor:"
    print ntmultiChannel.getDescriptor();
    num = ntmultiChannel.getNumberChannel()
    i = 0
    while i < num :
        value = ntmultiChannel.getChannelValue(i)
        print "index ", i, value
        i += 1
    print "all done"
