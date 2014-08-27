/* masarService.cpp */
/**
 * Copyright - See the COPYRIGHT that is included with this distribution.
 * EPICS pvDataCPP is distributed subject to a Software License Agreement found
 * in file LICENSE that is included with this distribution.
 */
/* Marty Kraimer 2011.03 */
/* This connects to a V3 record and presents the data as a PVStructure
 * It provides access to  value, alarm, display, and control.
 */

#include <cstddef>
#include <cstdlib>
#include <cstddef>
#include <string>
#include <stdexcept>
#include <memory>

#include <pv/nt.h>
#include <pv/sharedVector.h>

#include <pv/masarService.h>


namespace epics { namespace masar { 

using namespace epics::pvData;
using namespace epics::pvAccess;
using namespace epics::nt;
using namespace std;
using std::tr1::static_pointer_cast;

MasarService::MasarService()
: dslRdb(createDSL_RDB())
{}

MasarService::~MasarService()
{
}

void MasarService::destroy()
{
}

PVStructurePtr MasarService::request(
    PVStructurePtr const & pvArgument) throw (epics::pvAccess::RPCRequestException)
{
    static const int numberFunctions = 9;
    static const string functionNames[numberFunctions] = {
        string("saveSnapshot"),
        string("retrieveSnapshot"),
        string("retrieveServiceConfigProps"),
        string("retrieveServiceConfigs"),
        string("saveServiceConfig"),
        string("retrieveServiceEvents"),
        string("saveServiceEvent"),
        string("updateSnapshotEvent"),
        string("getLiveMachine")
    };
    if(!NTNameValue::is_a(pvArgument->getStructure())) {
        string functionName;
        PVStringPtr pvFunction = pvArgument->getSubField<PVString>("function");
        if (!pvFunction) {
            throw epics::pvAccess::RPCRequestException(
                 Status::STATUSTYPE_ERROR,"unknown MASAR function");
        }
        functionName = pvFunction->get();
        if(functionName.size()<1) {
            throw epics::pvAccess::RPCRequestException(
                Status::STATUSTYPE_ERROR,"pvArgument has an unsupported function");
        }
        StringArray fieldNames = pvArgument->getStructure()->getFieldNames();
        size_t fieldcounts = (size_t) fieldNames.size();
        shared_vector<string> name(fieldcounts-1);
        shared_vector<string> value(fieldcounts-1);
        size_t counts = 0;
        for (size_t i = 0; i < fieldcounts; ++i) {
            if(fieldNames[i].compare("function")!=0) {
                name[counts] = fieldNames[i];
                value[counts] = pvArgument->getStringField(fieldNames[i])->get();
                counts += 1;
            }
        }
        shared_vector<const string> names(freeze(name));
        shared_vector<const string> values(freeze(value));
        return dslRdb->request(functionName,names,values);

    } else{
//        NTNameValuePtr ntNameValue(NTNameValue::create(pvArgument));
//        PVStringPtr function = ntNameValue->getFunction();
//        String functionName;
//        for(int i=0; i<numberFunctions; i++) {
//            if(function->get().compare(functionNames[i])==0) {
//                functionName = functionNames[i];
//                break;
//            }
//        }
//        if(functionName.c_str()==0) {
//            throw epics::pvAccess::RPCRequestException(
//                Status::STATUSTYPE_ERROR,"pvArgument has an unsupported function");
//        }
        PVStringArrayPtr pvNames = pvArgument->getSubField<PVStringArray>("names");
        shared_vector<const string> names = pvNames->view();
        string functionName;
        for (size_t i = 0; i < names.size(); ++i) {
            if(names[i].compare("function")==0) {
                 functionName = names[i];
                 break;
            }
        }
        if(functionName.size()<1) {
            throw epics::pvAccess::RPCRequestException(
                Status::STATUSTYPE_ERROR,"pvArgument has no function definition");
        }
        PVFieldPtr pvField = pvArgument->getSubField("values");
        if(pvField->getField()->getType()!=scalarArray) {
            throw epics::pvAccess::RPCRequestException(
                Status::STATUSTYPE_ERROR,"pvArgument has illegal type for values");
        }
        PVScalarArrayPtr pvScalarArray = static_pointer_cast<PVScalarArray>(pvField);
        if(pvScalarArray->getScalarArray()->getElementType()!=pvString) {
	    throw epics::pvAccess::RPCRequestException(
	        Status::STATUSTYPE_ERROR,"pvArgument has illegal type for values");
        }
        PVStringArrayPtr pvValues = static_pointer_cast<PVStringArray>(pvScalarArray);
        shared_vector<const string> values = pvValues->view();
        return dslRdb->request(functionName,names,values);
    }
}

}}

