/*gatherV3DoubleExample.cpp */

/* Author: Marty Kraimer */

#include <cstddef>
#include <cstdlib>
#include <cstddef>
#include <string>
#include <cstdio>
#include <memory>
#include <iostream>

#include <cantProceed.h>
#include <epicsStdio.h>
#include <epicsMutex.h>
#include <epicsEvent.h>
#include <epicsThread.h>
#include <epicsAssert.h>

#include <epicsExport.h>
#include <pv/pvIntrospect.h>
#include <pv/pvData.h>
#include <pv/nt.h>

#include <pv/gatherV3Double.h>

using namespace std;
using namespace epics::pvData;

void test()
{
    String builder;
    int n = 10;
    String channelName[n];
    char name[40];
    for(int i=0; i<n; i++) {
        sprintf(name,"gatherExample%4.4d",i);
        channelName[i] = String(name);
    }
    GatherV3Double::shared_pointer gather = GatherV3Double::shared_pointer(
        new GatherV3Double(channelName,n));
    bool result = gather->connect(5.0);
    if(!result) {
        printf("connect failed\n%s\n",gather->getMessage().c_str());
        printf("This test requires the test V3 database"
           " of the gather service.\n");
        printf("It must be started before running"
           " this test\n");
    }
    assert(result);
    result = gather->get();
    if(!result) printf("get failed\n%s\n",gather->getMessage().c_str());
    assert(result);
    PVDoubleArray *values = gather->getValue();
    builder.clear();
    values->toString(&builder);
    printf("values: %s\n",builder.c_str());
    // issue get again
    epicsThreadSleep(.9);
    result = gather->get();
    if(!result) printf("get failed\n%s\n",gather->getMessage().c_str());
    assert(result);
    values = gather->getValue();
    builder.clear();
    values->toString(&builder);
    printf("values: %s\n",builder.c_str());
}

int main(int argc,char *argv[])
{
    test();
    epicsThreadSleep(.5);
    test();
    return(0);
}

