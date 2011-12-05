/*gatherV3DoubleTest.cpp */

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
    bool debug = false;
    if(argc>1) {
        char * arg = argv[1];
        if(strcmp(arg,"debug")==0) {
           printf("debug is true\n");
           debug = true;
        }
    }
    String builder;
    int n = 1000;
    if(debug) n = 2;
    String channelName[n];
    char name[40];
    for(int i=0; i<n; i++) {
        sprintf(name,"gatherExample%4.4d",i);
        channelName[i] = String(name);
    }
    GatherV3Double::shared_pointer gather = GatherV3Double::shared_pointer(
        new GatherV3Double(channelName,n));
    PVStructure::shared_pointer nttable = gather->getNTTable();
    if(debug) {
        builder.clear();
        nttable->toString(&builder);
        printf("nttable initial\n%s\n",builder.c_str());
    }
    bool result = gather->connect(5.0);
    if(debug) printf("connect %s\n",(result ? "true" : "false"));
    assert(result);
    result = gather->get();
    if(debug) {
        printf("get %s\n",(result ? "true" : "false"));
        builder.clear();
        nttable->toString(&builder);
        printf("nttable\n%s\n",builder.c_str());
    }
    assert(result);
    PVDoubleArray *values = gather->getValue();
    PVDoubleArray *deltas = gather->getDeltaTime();
    PVIntArray    *severitys = gather->getSeverity();
    PVBooleanArray *isConnecteds = gather->getIsConnected();
    PVStringArray  *channelNames = gather->getChannelName();
    if(debug) {
        builder.clear();
        values->toString(&builder);
        printf("values: %s\n",builder.c_str());
        builder.clear();
        deltas->toString(&builder);
        printf("deltas: %s\n",builder.c_str());
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
    return(0);
}

