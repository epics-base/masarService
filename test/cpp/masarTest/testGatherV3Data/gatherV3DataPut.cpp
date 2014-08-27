/*gatherV3DataPut.cpp */

/* Author: Marty Kraimer */


#include <pv/gatherV3Data.h>
#include <pv/clientFactory.h>
#include <pv/caProvider.h>

using namespace std;
using namespace epics::pvData;
using namespace epics::pvAccess;
using namespace epics::masar;
using namespace epics::nt;
using std::tr1::static_pointer_cast;

void test()
{
    size_t n = 11;
n = 4;
    shared_vector<string> names(n);
names[0] = "masarExampleStringArray";
names[1] = "masarExampleCharArray";
names[2] = "masarExampleLongArray";
names[3] = "masarExampleDoubleArray";
//    names[0] = "masarExample0000";
//    names[1] = "masarExample0001";
//    names[2] = "masarExample0002";
//    names[3] = "masarExample0003";
//    names[4] = "masarExample0004";
//    names[5] = "masarExampleCharArray";
//    names[6] = "masarExampleStringArray";
//    names[7] = "masarExampleLongArray";
//    names[8] = "masarExampleDoubleArray";
//    names[9] = "masarExampleBoUninit";
//    names[10] = "masarExampleMbboUninit";
    shared_vector<const string> channelName(freeze(names));
    GatherV3DataPtr gather = GatherV3Data::create(channelName);
    bool result = gather->connect(5.0);
    if(!result) {
        cout << "connect failed " << gather->getMessage() << endl;
        cout << "This test requires iocBoot/iocAll. ";
        cout << "It must be started before running this test\n";
        return;
    }
    result = gather->get();
    if(!result) {
        cout << "get problem " << gather->getMessage() << endl;
    }
    NTMultiChannelPtr ntmultiChannel = gather->getNTMultiChannel();
    PVUnionArrayPtr pvUnionArray = ntmultiChannel->getValue();
    shared_vector<const PVUnionPtr> pvUnions = pvUnionArray->view();

   for(size_t i=0; i<n; i++) {
        const PVUnionPtr pvUnion = pvUnions[i];
        PVFieldPtr pvField = pvUnion->get();
        Type type = pvField->getField()->getType();
        if(type==scalar) {
             PVScalarPtr pvScalar = static_pointer_cast<PVScalar>(pvField);
             ScalarType scalarType = pvScalar->getScalar()->getScalarType();
             if(scalarType==pvString) {
                 PVStringPtr pvValue = static_pointer_cast<PVString>(pvScalar);
                 ostringstream oss;
                 oss << "channel " << i;
                 pvValue->put(oss.str());
                 continue;
             }
             if(scalarType==pvByte) {
                 PVBytePtr pvValue = static_pointer_cast<PVByte>(pvScalar);
                 pvValue->put(i);
                 continue;
             }
             if(scalarType==pvShort) {
                 PVShortPtr pvValue = static_pointer_cast<PVShort>(pvScalar);
                 pvValue->put(i);
                 continue;
             }
             if(scalarType==pvInt) {
                 PVIntPtr pvValue = static_pointer_cast<PVInt>(pvScalar);
                 pvValue->put(i);
                 continue;
             }
             if(scalarType==pvFloat) {
                 PVFloatPtr pvValue = static_pointer_cast<PVFloat>(pvScalar);
                 pvValue->put(i);
                 continue;
             }
             if(scalarType==pvDouble) {
                 PVDoublePtr pvValue = static_pointer_cast<PVDouble>(pvScalar);
                 pvValue->put(i);
                 continue;
             }
             cout << "got unexpected type\n";
             exit(1);
        }
        if(type==scalarArray) {
             PVScalarArrayPtr pvScalarArray = static_pointer_cast<PVScalarArray>(pvField);
             ScalarType elementType = pvScalarArray->getScalarArray()->getElementType();
             if(elementType==pvString) {
                PVStringArrayPtr pvValue = static_pointer_cast<PVStringArray>(pvScalarArray);
                size_t num = 4;
                shared_vector<string> value(num);
                value[0] = "aaa";
                value[1] = "bbb";
                value[2] = "ccc";
                value[3] = "ddd";
                shared_vector<const string> xxx(freeze(value));
                pvValue->replace(xxx);
                continue;
             }
             if(elementType==pvByte) {
                PVByteArrayPtr pvValue = static_pointer_cast<PVByteArray>(pvScalarArray);
                size_t num = 4;
                shared_vector<int8> value(num);
                value[0] = 1;
                value[1] = 2;
                value[2] = 3;
                value[3] = 4;
                shared_vector<const int8> xxx(freeze(value));
                pvValue->replace(xxx);
                continue;
             }
             if(elementType==pvShort) {
                PVShortArrayPtr pvValue = static_pointer_cast<PVShortArray>(pvScalarArray);
                size_t num = 4;
                shared_vector<int16> value(num);
                value[0] = 1;
                value[1] = 2;
                value[2] = 3;
                value[3] = 4;
                shared_vector<const int16> xxx(freeze(value));
                pvValue->replace(xxx);
                continue;
             } 
             if(elementType==pvInt) {
                PVIntArrayPtr pvValue = static_pointer_cast<PVIntArray>(pvScalarArray);
                size_t num = 4;
                shared_vector<int32> value(num);
                value[0] = 1;
                value[1] = 2;
                value[2] = 3;
                value[3] = 4;
                shared_vector<const int32> xxx(freeze(value));
                pvValue->replace(xxx);
                continue;
             } 
             if(elementType==pvFloat) {
                PVFloatArrayPtr pvValue = static_pointer_cast<PVFloatArray>(pvScalarArray);
                size_t num = 4;
                shared_vector<float> value(num);
                value[0] = 1;
                value[1] = 2;
                value[2] = 3;
                value[3] = 4;
                shared_vector<const float> xxx(freeze(value));
                pvValue->replace(xxx);
                continue;
             } 
             if(elementType==pvDouble) {
                PVDoubleArrayPtr pvValue = static_pointer_cast<PVDoubleArray>(pvScalarArray);
                size_t num = 4;
                shared_vector<double> value(num);
                value[0] = 1;
                value[1] = 2;
                value[2] = 3;
                value[3] = 4;
                shared_vector<const double> xxx(freeze(value));
                pvValue->replace(xxx);
                continue;
             } 
             if(type==structure) {
                 continue;
             }
             cout << "got unexpected type\n";
             exit(1);
        }
        if(type==structure) {
            PVStructurePtr pvTop = static_pointer_cast<PVStructure>(pvField);
            PVIntPtr pvIndex = pvTop->getSubField<PVInt>("index");
            if(!pvIndex) {
                cout << "got unexpected " << *pvTop << endl;
            } else {
                pvIndex->put(1);
            }
            continue;
        }
        cout << "got unexpected type\n";
        exit(1);
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
    cout << "ntmultiChannel\n";
    cout <<  *ntmultiChannel->getPVStructure() << endl;
}

int main(int argc,char *argv[])
{
    ClientFactory::start();
    ::epics::pvAccess::ca::CAClientFactory::start();
    test();
    return 0;
}

