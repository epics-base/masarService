/*gatherV3ScalarDataTest.cpp */

/* Author: Marty Kraimer */

#include <pv/CDRMonitor.h>
#include <epicsExit.h>

#include <pv/gatherV3ScalarData.h>

using namespace std;
using namespace epics::pvData;
using namespace epics::pvAccess;

void testGet(bool debug,GatherV3ScalarData::shared_pointer gather)
{
    String builder;
    PVStructure::shared_pointer nttable = gather->getNTTable();
    bool result = gather->get();
    if(!result) printf("connect failed\n%s\n",gather->getMessage().c_str());
    if(debug) {
        builder.clear();
        nttable->toString(&builder);
        printf("nttable\n%s\n",builder.c_str());
    }
    assert(result);
    PVDoubleArray *values = gather->getDoubleValue();
    PVIntArray    *severitys = gather->getAlarmSeverity();
    PVBooleanArray *isConnecteds = gather->getIsConnected();
    PVStringArray  *channelNames = gather->getChannelName();
    if(debug) {
        builder.clear();
        values->toString(&builder);
        printf("values: %s\n",builder.c_str());
        builder.clear();
        severitys->toString(&builder);
        printf("severitys: %s\n",builder.c_str());
        builder.clear();
        isConnecteds->toString(&builder);
        printf("isConnecteds: %s\n",builder.c_str());
        builder.clear();
        channelNames->toString(&builder);
        printf("channelNames: %s\n",builder.c_str());
    }
}

void testConnect(bool debug,GatherV3ScalarData::shared_pointer gather)
{
    bool result = gather->connect(5.0);
    if(!result) {
        printf("connect failed\n%s\n",gather->getMessage().c_str());
        printf("This test requires the test V3 database"
           " of the gather service.\n"); 
        printf("It must be started before running"
           " this test\n");
    }
    assert(result);
    testGet(debug,gather);
    testGet(debug,gather);
    gather->disconnect();
}

void test(bool debug)
{
    String builder;
    int n = 1000;
    if(debug) n = 2;
    String channelName[n];
    char name[40];
    for(int i=0; i<n; i++) {
        sprintf(name,"gatherExample%4.4d",i);
        channelName[i] = String(name);
    }
    GatherV3ScalarData::shared_pointer gather = GatherV3ScalarData::shared_pointer(
        new GatherV3ScalarData(channelName,n));
    PVStructure::shared_pointer nttable = gather->getNTTable();
    if(debug) {
        builder.clear();
        nttable->toString(&builder);
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
    CDRMonitor::get().show(stdout,true);
    return(0);
}

