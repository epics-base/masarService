/*gatherV3DataTest.cpp */

/* Author: Marty Kraimer */

#include <epicsExit.h>

#include <pv/gatherV3Data.h>

using namespace std;
using namespace epics::pvData;
using namespace epics::pvAccess;

void testGet(bool debug,GatherV3DataPtr gather)
{
    String builder;
    NTTablePtr nttable = gather->getNTTable();
    bool result = gather->get();
    if(!result) printf("get failed\n%s\n",gather->getMessage().c_str());
    if(debug) {
        builder.clear();
        nttable->getPVStructure()->toString(&builder);
        printf("nttable\n%s\n",builder.c_str());
    }
    PVDoubleArrayPtr values = gather->getDoubleValue();
    PVIntArrayPtr severitys = gather->getAlarmSeverity();
    PVBooleanArrayPtr isConnecteds = gather->getIsConnected();
    PVStringArrayPtr channelNames = gather->getChannelName();
    if(debug) {
        builder.clear();
        values->toString(&builder);
        printf("value: %s\n",builder.c_str());
        builder.clear();
        severitys->toString(&builder);
        printf("severity: %s\n",builder.c_str());
        builder.clear();
        isConnecteds->toString(&builder);
        printf("isConnected: %s\n",builder.c_str());
        builder.clear();
        channelNames->toString(&builder);
        printf("channelName: %s\n",builder.c_str());
    }
}

void testConnect(bool debug,GatherV3DataPtr gather)
{
    bool result = gather->connect(1.0);
    if(!result) {
        printf("connect failed\n%s\n",gather->getMessage().c_str());
        printf("This test requires the test V3 database"
           " of the gather service.\n"); 
        printf("It must be started before running"
           " this test\n");
    }
    testGet(debug,gather);
    testGet(debug,gather);
    gather->disconnect();
}

void test(bool debug)
{
    String builder;
    int n = 1000;
    if(debug) n = 6;
    StringArray channelName(n);
    char name[40];
    for(int i=0; i<n; i++) {
        sprintf(name,"masarExample%4.4d",i);
        channelName[i] = String(name);
    }
    GatherV3DataPtr gather(new GatherV3Data(channelName,n));
    NTTablePtr nttable = gather->getNTTable();
    if(debug) {
        builder.clear();
        nttable->getPVStructure()->toString(&builder);
        printf("nttable initial\n%s\n",builder.c_str());
    }
    testConnect(debug,gather);
    testConnect(debug,gather);
}

int main(int argc,char *argv[])
{
    bool debug = false;
    if(argc>1) {
        char * arg = argv[1];
        if(strcmp(arg,"debug")==0) {
           printf("debug is true\n");
           debug = true;
        }
    }
    test(debug);
    epicsExitCallAtExits();
    epicsThreadSleep(1.0);
    return(0);
}

