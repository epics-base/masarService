/*gatherV3ScalarDataPut.cpp */

/* Author: Marty Kraimer */

#include <pv/CDRMonitor.h>
#include <epicsExit.h>

#include <pv/gatherV3ScalarData.h>

using namespace std;
using namespace epics::pvData;
using namespace epics::pvAccess;

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
    GatherV3ScalarData::shared_pointer gather = GatherV3ScalarData::shared_pointer(
        new GatherV3ScalarData(channelName,n));
    bool result = gather->connect(5.0);
    if(!result) {
        printf("connect failed\n%s\n",gather->getMessage().c_str());
        printf("This test requires iocBoot/iocAll ");
        printf("It must be started before running this test\n");
        exit(1);
    }
    DoubleArrayData ddata;
    gather->getDoubleValue()->get(0,n,&ddata);
    double *dvalue = ddata.data;
    StringArrayData sdata;
    gather->getStringValue()->get(0,n,&sdata);
    String *svalue = sdata.data;
    IntArrayData idata;
    gather->getIntValue()->get(0,n,&idata);
    int32 *ivalue = idata.data;
    gather->getDBRType()->get(0,n,&idata);
    int32 *dbrType = idata.data;
    for(int i=0; i<n; i++) {
        switch(dbrType[i]) {
        case DBF_STRING:
             svalue[i] = String("this is set by gatherV3ScalarDataPut"); break;
        case DBF_ENUM:
             svalue[i] = String("seven"); break;
        case DBF_CHAR:
        case DBF_INT:
        case DBF_LONG:
             ivalue[i] = i; break;
        case DBF_FLOAT:
        case DBF_DOUBLE:
             dvalue[i] = i; break;
        default:
            printf("got an unexpected DBF type. Logic error\n");
            exit(1);
        }
    }
    if(!result) {printf("put failed\n%s\n",gather->getMessage().c_str()); exit(1);}
    result = gather->get();
    if(!result) {printf("get failed\n%s\n",gather->getMessage().c_str()); exit(1);}
     PVStructure::shared_pointer nttable = gather->getNTTable();
     builder.clear();
     nttable->toString(&builder);
     printf("nttable\n%s\n",builder.c_str());
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

