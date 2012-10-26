/*gatherV3DataExample.cpp */

/* Author: Marty Kraimer */

#include <epicsExit.h>

#include <pv/gatherV3Data.h>

using namespace std;
using namespace epics::pvData;
using namespace epics::pvAccess;

void test()
{
    String builder;
    int n = 1000;
    String channelName[n];
    char name[40];
    for(int i=0; i<n; i++) {
        sprintf(name,"masarExample%4.4d",i);
        channelName[i] = String(name);
    }
    GatherV3Data::shared_pointer gather = GatherV3Data::shared_pointer(
        new GatherV3Data(channelName,n));
    bool result = gather->connect(1.0);
    if(!result) {
        printf("connect failed\n%s\n",gather->getMessage().c_str());
        printf("This test requires the test V3 database"
           " of the gather service.\n");
        printf("It must be started before running"
           " this test\n");
    }
    int ntimes = 0;
    while(true) {
        printf("calling get ntimes %d\n",ntimes++);
        result = gather->get();
        if(!result) printf("get failed\n%s\n",gather->getMessage().c_str());
        PVBooleanArrayPtr isConnected = gather->getIsConnected();
        BooleanArrayData data;
        isConnected->get(0,n,data);
        for(int i=0; i<n; i++) {
            if(!data.data[i]) {
                printf("channel %d not connected\n",i);
            }
        }
        epicsThreadSleep(1.0);
    }
}

int main(int argc,char *argv[])
{
    test();
    epicsThreadSleep(.5);
    epicsExitCallAtExits();
    epicsThreadSleep(1.0);
    return 0;
}

