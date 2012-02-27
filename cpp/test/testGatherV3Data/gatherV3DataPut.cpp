/*gatherV3DataPut.cpp */

/* Author: Marty Kraimer */

#include <pv/CDRMonitor.h>
#include <epicsExit.h>

#include <pv/gatherV3Data.h>

using namespace std;
using namespace epics::pvData;
using namespace epics::pvAccess;

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
    GatherV3Data::shared_pointer gather = GatherV3Data::shared_pointer(
        new GatherV3Data(channelName,n));
    bool result = gather->connect(5.0);
    if(!result) {
        printf("connect failed\n%s\n",gather->getMessage().c_str());
        printf("This test requires iocBoot/iocAll ");
        printf("It must be started before running this test\n");
        exit(1);
    }
    PVStructure::shared_pointer nttable = gather->getNTTable();
    BooleanArrayData booldata;
    PVBooleanArray *pvIsArray = static_cast<PVBooleanArray *>(nttable->getScalarArrayField("isArray",pvBoolean));
    pvIsArray->get(0,n,&booldata);
    bool *isArray = booldata.data;
    DoubleArrayData ddata;
    gather->getDoubleValue()->get(0,n,&ddata);
    double *dvalue = ddata.data;
    StringArrayData sdata;
    gather->getStringValue()->get(0,n,&sdata);
    String *svalue = sdata.data;
    LongArrayData ldata;
    gather->getLongValue()->get(0,n,&ldata);
    int64 *lvalue = ldata.data;
    IntArrayData idata;
    StructureArrayData structdata;
    gather->getArrayValue()->get(0,n,&structdata);
    PVStructurePtr *structvalue = structdata.data;
    gather->getDBRType()->get(0,n,&idata);
    int32 *dbrType = idata.data;
    for(int i=0; i<n; i++) {
        if(isArray[i]) {
            PVStructurePtr pvStructure = structvalue[i];
            switch(dbrType[i]) {
            case DBF_STRING: {
                PVStringArray * pvValue = static_cast<PVStringArray *>(
                    pvStructure->getScalarArrayField("stringValue",pvString));
                int num = 4;
                String value[4] {"aaa","bbb","ccc","ddd"};
                pvValue->put(0,num,value,0);
                break;
            }
            case DBF_CHAR:
            case DBF_INT:
            case DBF_LONG: {
                PVIntArray * pvValue = static_cast<PVIntArray *>(
                    pvStructure->getScalarArrayField("intValue",pvInt));
                int num = 4;
                int32 value[4] {1,2,3,4};
                pvValue->put(0,num,value,0);
                 break;
            }
            case DBF_FLOAT:
            case DBF_DOUBLE: {
                PVDoubleArray * pvValue = static_cast<PVDoubleArray *>(
                    pvStructure->getScalarArrayField("doubleValue",pvDouble));
                int num = 4;
                double value[4] {1e1,1e2,1e3,1e4};
                pvValue->put(0,num,value,0);
                 break;
            }
            default:
                printf("got an unexpected DBF type. Logic error\n");
                exit(1);
            }
            continue;
        }
        switch(dbrType[i]) {
        case DBF_STRING:
             svalue[i] = String("this is set by gatherV3DataPut"); break;
        case DBF_ENUM:
             svalue[i] = String("one"); break;
        case DBF_CHAR:
        case DBF_INT:
        case DBF_LONG:
             lvalue[i] = i; break;
        case DBF_FLOAT:
        case DBF_DOUBLE:
             dvalue[i] = i; break;
        default:
            printf("got an unexpected DBF type. Logic error\n");
            exit(1);
        }
    }
    result = gather->put();
    if(!result) {printf("put failed\n%s\n",gather->getMessage().c_str()); exit(1);}
    result = gather->get();
    if(!result) {printf("get failed\n%s\n",gather->getMessage().c_str()); exit(1);}
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

