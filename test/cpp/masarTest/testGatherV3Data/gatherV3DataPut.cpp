/*gatherV3DataPut.cpp */

/* Author: Marty Kraimer */

#include <epicsExit.h>

#include <pv/gatherV3Data.h>

using namespace std;
using namespace epics::pvData;
using namespace epics::pvAccess;
using std::tr1::static_pointer_cast;
using std::cout;
using std::endl;

void test()
{
    int n = 11;
    StringArray channelName(n);
    channelName[0] = "masarExample0000";
    channelName[1] = "masarExample0001";
    channelName[2] = "masarExample0002";
    channelName[3] = "masarExample0003";
    channelName[4] = "masarExample0004";
    channelName[5] = "masarExampleCharArray";
    channelName[6] = "masarExampleStringArray";
    channelName[7] = "masarExampleLongArray";
    channelName[8] = "masarExampleDoubleArray";
    channelName[9] = "masarExampleBoUninit";
    channelName[10] = "masarExampleMbboUninit";
    GatherV3DataPtr gather(new GatherV3Data(channelName,n));
    bool result = gather->connect(5.0);
    if(!result) {
        cout << "connect failed " << gather->getMessage() << endl;
        cout << "This test requires iocBoot/iocAll. ";
        cout << "It must be started before running this test\n";
        exit(1);
    }
    result = gather->get();
    if(!result) {
        cout << "get problem " << gather->getMessage() << endl;
    }
    NTTablePtr nttable = gather->getNTTable();
    PVBooleanArrayPtr pvIsArray = static_pointer_cast<PVBooleanArray>
            (nttable->getPVStructure()->getScalarArrayField("isArray",pvBoolean));
    uint8 * isArray = pvIsArray->get();
    double *dvalue = gather->getDoubleValue()->get();
    String *svalue = gather->getStringValue()->get();
    int64 * lvalue = gather->getLongValue()->get();
    PVStructurePtr *structvalue = gather->getArrayValue()->get();
    int32 * dbrType = gather->getDBRType()->get();
    for(int i=0; i<n; i++) {
        if(isArray[i]) {
            PVStructurePtr pvStructure = structvalue[i];
            switch(dbrType[i]) {
            case DBF_STRING: {
                PVStringArrayPtr pvValue = static_pointer_cast<PVStringArray>(
                    pvStructure->getScalarArrayField("stringValue",pvString));
                int num = 4;
                String value[4];
                value[0] = "aaa";
                value[1] = "bbb";
                value[2] = "ccc";
                value[3] = "ddd";
                pvValue->put(0,num,value,0);
                break;
            }
            case DBF_CHAR:
            case DBF_INT:
            case DBF_LONG: {
                PVIntArrayPtr pvValue = static_pointer_cast<PVIntArray>(
                    pvStructure->getScalarArrayField("intValue",pvInt));
                int num = 4;
                int32 value[4] = {1,2,3,4};
                pvValue->put(0,num,value,0);
                 break;
            }
            case DBF_FLOAT:
            case DBF_DOUBLE: {
                PVDoubleArrayPtr pvValue = static_pointer_cast<PVDoubleArray>(
                    pvStructure->getScalarArrayField("doubleValue",pvDouble));
                int num = 4;
                double value[4] = {1e1,1e2,1e3,1e4};
                pvValue->put(0,num,value,0);
                 break;
            }
            default:
                cout << "got an unexpected DBF type. Logic error\n";
                exit(1);
            }
            continue;
        }
        switch(dbrType[i]) {
        case DBF_STRING:
             svalue[i] = String("this is set by gatherV3DataPut"); break;
        case DBF_ENUM:
             svalue[i] = String("one");
             break;
        case DBF_CHAR:
        case DBF_INT:
        case DBF_LONG:
             lvalue[i] = i; break;
        case DBF_FLOAT:
        case DBF_DOUBLE:
             dvalue[i] = i; break;
        default:
            cout << "got an unexpected DBF type. Logic error\n";
            exit(1);
        }
    }
    result = gather->put();
    if(!result) {
        cout << "put failed " << gather->getMessage() << endl;
        exit(1);
    }
    result = gather->get();
    if(!result) {
        cout << "get failed " << gather->getMessage() << endl;
        exit(1);
    }
    cout << "nttable\n";
    cout <<  nttable->getPVStructure()->dumpValue(cout) << endl;
}

int main(int argc,char *argv[])
{
    test();
    epicsThreadSleep(.5);
    epicsExitCallAtExits();
    epicsThreadSleep(1.0);
    return 0;
}

