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
#include <cstdio>
#include <stdexcept>
#include <memory>

#include <pv/nt.h>

#include <pv/masarService.h>


namespace epics { namespace masar { 

using namespace epics::pvData;
using namespace epics::pvAccess;

MasarService::MasarService()
: dslRdb(createDSL_RDB())
{}

MasarService::~MasarService()
{
//printf("MasarService::~MasarService()\n");
}

void MasarService::destroy()
{
//printf("MasarService::destroy()\n");
}

PVStructurePtr MasarService::request(
    PVStructurePtr const & pvArgument) throw (epics::pvAccess::RPCRequestException)
{
    String tmpbuilder; 
    pvArgument->toString(&tmpbuilder);
    printf("pvArguments got:\n %s\n", tmpbuilder.c_str());
    static const int numberFunctions = 9;
    static const String functionNames[numberFunctions] = {
        String("saveSnapshot"),
        String("retrieveSnapshot"),
        String("retrieveServiceConfigProps"),
        String("retrieveServiceConfigs"),
        String("saveServiceConfig"),
        String("retrieveServiceEvents"),
        String("saveServiceEvent"),
        String("updateSnapshotEvent"),
        String("getLiveMachine")
    };
    String builder;
    builder += "pvArgument ";
    if(!NTNameValue::isNTNameValue(pvArgument)) {
        String functionName;
        PVStringPtr pvFunction = pvArgument->getStringField("function");
        if (pvFunction.get() == NULL) {
            throw epics::pvAccess::RPCRequestException(Status::STATUSTYPE_ERROR,"unknown MASAR function");
        }
        functionName = pvFunction->get();
        if(functionName.c_str()==0) {
            throw epics::pvAccess::RPCRequestException(Status::STATUSTYPE_ERROR,"pvArgument has an unsupported function");
        }
        StringArray fieldNames = pvArgument->getStructure()->getFieldNames();
        size_t fieldcounts = (size_t) fieldNames.size();
        std::vector<std::string> names  (fieldcounts-1);
        std::vector<std::string> values (fieldcounts-1);
        size_t counts = 0;
        for (size_t i = 0; i < fieldcounts; i ++) {
            if(fieldNames[i].compare("function")!=0) {
                names[counts] = fieldNames[i];
                values[counts] = pvArgument->getStringField(fieldNames[i])->get();
                counts += 1;
            }
        }
        return dslRdb->request(functionName,fieldcounts-1,names,values);

    } else{
        NTNameValuePtr ntNameValue(NTNameValue::create(pvArgument));
        PVStringPtr function = ntNameValue->getFunction();
        String functionName;
        for(int i=0; i<numberFunctions; i++) {
            if(function->get().compare(functionNames[i])==0) {
                functionName = functionNames[i];
                break;
            }
        }
        if(functionName.c_str()==0) {
            throw epics::pvAccess::RPCRequestException(Status::STATUSTYPE_ERROR,"pvArgument has an unsupported function");
        }
        PVStringArrayPtr pvNames = ntNameValue->getNames();
        PVStringArrayPtr pvValues = ntNameValue->getValues();
        StringArray const &names = pvNames->getVector();
        StringArray const &values = pvValues->getVector();
        int num = pvNames->getLength();
        return dslRdb->request(functionName,num,names,values);
    }
}

}}

