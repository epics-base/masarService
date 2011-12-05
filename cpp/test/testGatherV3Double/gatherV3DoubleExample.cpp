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

int main(int argc,char *argv[])
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
    assert(result);
    result = gather->get();
    assert(result);
    PVDoubleArray *values = gather->getValue();
    builder.clear();
    values->toString(&builder);
    printf("values: %s\n",builder.c_str());
    return(0);
}

