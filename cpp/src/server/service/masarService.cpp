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
}

void MasarService::destroy()
{
}

PVStructurePtr MasarService::request(
    PVStructurePtr const & pvArgument) throw (epics::pvAccess::RPCRequestException)
{
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
        throw epics::pvAccess::RPCRequestException(Status::STATUSTYPE_ERROR,"pvArgument is not an NTNameValue");
    }
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

}}

