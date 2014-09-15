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
    if(!NTNameValue::is_a(pvArgument->getStructure())) {
        throw epics::pvAccess::RPCRequestException(
             Status::STATUSTYPE_ERROR,"pvArgument is not an NTNameValue");
    }
    string functionName;
    PVStringPtr pvFunction = pvArgument->getSubField<PVString>("function");
    if (!pvFunction) {
        throw epics::pvAccess::RPCRequestException(
             Status::STATUSTYPE_ERROR,"pvArgument does not have function field");
    }
    functionName = pvFunction->get();
    if(functionName.size()<1) {
        throw epics::pvAccess::RPCRequestException(
            Status::STATUSTYPE_ERROR,"pvArgument has an unsupported function");
    }
    try {

        const shared_vector<const string> name = pvArgument->getSubField<PVStringArray>("names")->view();
        const shared_vector<const string> value = pvArgument->getSubField<PVStringArray>("values")->view();
        PVStructurePtr result = dslRdb->request(functionName,name,value);
        return result;
    } catch (std::exception &e) {
        throw RPCRequestException(Status::STATUSTYPE_ERROR,
            std::string("request failed ") + e.what());
    }

}

}}

