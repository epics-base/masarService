/*gatherV3ScalarDataExample.cpp */

/* Author: Marty Kraimer */

#include <pv/CDRMonitor.h>
#include <epicsExit.h>

#include <pv/gatherV3ScalarData.h>

using namespace std;
using namespace epics::pvData;
using namespace epics::pvAccess;

NTTable::shared_pointer getLiveMachine(
        String channelName [], int numberChannels)
{
    GatherV3ScalarData::shared_pointer gather = GatherV3ScalarData::shared_pointer(
        new GatherV3ScalarData(channelName,numberChannels));

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

    PVStructure::shared_pointer nttable = gather->getNTTable();

    // First place to show the data
    String builder;
    NTTable::shared_pointer pvt = NTTable::shared_pointer(new NTTable(nttable));
    PVBooleanArray * isConnected = static_cast<PVBooleanArray *>(pvt->getPVField(5));
    isConnected->toString(&builder);
    printf("%s\n", builder.c_str());

    return pvt;
}


void test()
{
    String builder;
    int n = 10;
    String channelName[n];
    char name[40];
    for(int i=0; i<n; i++) {
        sprintf(name,"masarExample%4.4d",i);
        channelName[i] = String(name);
    }

    NTTable::shared_pointer pvt = getLiveMachine(channelName,n);
    PVBooleanArray * isConnected = static_cast<PVBooleanArray *>(pvt->getPVField(5));
    isConnected->toString(&builder);
    printf("%s\n", builder.c_str());

//    // do itself.
//    GatherV3ScalarData::shared_pointer gather = GatherV3ScalarData::shared_pointer(
//        new GatherV3ScalarData(channelName,n));
//    bool result = gather->connect(5.0);
//    if(!result) {
//        printf("connect failed\n%s\n",gather->getMessage().c_str());
//        printf("This test requires the test V3 database"
//           " of the gather service.\n");
//        printf("It must be started before running"
//           " this test\n");
//    }
//    assert(result);
//    result = gather->get();
//    if(!result) printf("get failed\n%s\n",gather->getMessage().c_str());
//    assert(result);
//    PVDoubleArray *values = gather->getDoubleValue();
//    builder.clear();
//    values->toString(&builder);
//    printf("values: %s\n",builder.c_str());
//    // issue get again
//    epicsThreadSleep(.9);
//    result = gather->get();
//    if(!result) printf("get failed\n%s\n",gather->getMessage().c_str());
//    assert(result);
//    values = gather->getDoubleValue();
//    builder.clear();
//    values->toString(&builder);
//    printf("values: %s\n",builder.c_str());
//    isConnected = gather->getIsConnected();
//    builder.clear();
//    isConnected->toString(&builder);
//    printf("isConnected: %s\n",builder.c_str());
}

int main(int argc,char *argv[])
{
    test();
    epicsThreadSleep(.5);
    epicsExitCallAtExits();
    epicsThreadSleep(1.0);
    CDRMonitor::get().show(stdout,true);
    return 0;
}

