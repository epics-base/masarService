/*gatherV3DataExample.cpp */

/* Author: Marty Kraimer */

#include <epicsExit.h>

#include <pv/gatherV3Data.h>

using namespace std;
using namespace epics::pvData;
using namespace epics::pvAccess;
using std::tr1::static_pointer_cast;

NTTable::shared_pointer getLiveMachine(
        String channelName [], int numberChannels)
{
    GatherV3Data::shared_pointer gather = GatherV3Data::shared_pointer(
        new GatherV3Data(channelName,numberChannels));

    // wait one second, which is a magic number for now.
    // The waiting time might be removed later after stability test.
    bool result = gather->connect(1.0);
    if(!result) {
        printf("connect failed\n%s\n",gather->getMessage().c_str());
        printf("This test requires the test V3 database"
           " of the gather service.\n");
        printf("It must be started before running this test\n");
    }
    result = gather->get();

    NTTablePtr nttable = gather->getNTTable();
    String builder;
    nttable->getPVStructure()->toString(&builder);
    printf("%s\n", builder.c_str());

    // First place to show the data
//    String builder;
    PVBooleanArrayPtr isConnected = static_pointer_cast<PVBooleanArray>(nttable->getPVField(5));
    builder.clear();
    isConnected->toString(&builder);
    printf("%s\n", builder.c_str());

    return nttable;
}


void test()
{
    String builder;
    int n = 9;
    String channelName[n];
    channelName[0] = "masarExample0000";
    channelName[1] = "masarExample0001";
    channelName[2] = "masarExample0002";
    channelName[3] = "masarExample0003";
    channelName[4] = "masarExample0004";
    channelName[5] = "masarExampleCharArray";
    channelName[6] = "masarExampleStringArray";
    channelName[7] = "masarExampleLongArray";
    channelName[8] = "masarExampleDoubleArray";

    NTTable::shared_pointer pvt = getLiveMachine(channelName,n);
    PVBooleanArrayPtr isConnected = static_pointer_cast<PVBooleanArray>(pvt->getPVField(5));
    builder.clear();
    isConnected->toString(&builder);
    printf("%s\n", builder.c_str());
}

int main(int argc,char *argv[])
{
    test();
    epicsThreadSleep(.5);
    epicsExitCallAtExits();
    epicsThreadSleep(1.0);
    return 0;
}

