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
#    alarm = Alarm()
#    ntmultiChannel->getAlarm(alarm.getAlarmPy())
#    print alarm
#    timeStamp TimeStamp()
#    ntmultiChannel->getTimeStamp(timeStamp.getTimeStampPy())
#    print timeStamp
    print ntmultiChannel.getNumberChannel();
    print ntmultiChannel.getValue();
    print ntmultiChannel.getChannelName();
    print ntmultiChannel.getIsConnected();
    print ntmultiChannel.getSeverity();
    print ntmultiChannel.getStatus();
    print ntmultiChannel.getMessage();
    print ntmultiChannel.getSecondsPastEpoch();
    print ntmultiChannel.getNanoseconds();
    print ntmultiChannel.getUserTag();
    print ntmultiChannel.getDescriptor();
