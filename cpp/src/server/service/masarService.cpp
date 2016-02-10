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
    try{
        assert(dslRdb.get() != NULL);

        string functionName(pvArgument->getSubFieldT<PVString>("function")->get());
        if(functionName.empty()) {
            throw epics::pvAccess::RPCRequestException(
                        Status::STATUSTYPE_ERROR,"pvArgument has an unsupported function");
        }

        if(!NTNameValue::is_a(pvArgument->getStructure())) {
            // support non NTNameValue Pair for some general purpose client, for example command line tools

            const StringArray& fieldNames = pvArgument->getStructure()->getFieldNames();
            size_t fieldcounts = fieldNames.size();
            shared_vector<string> names  (fieldcounts-1);
            shared_vector<string> values (fieldcounts-1);
            size_t counts = 0;
            for (size_t i = 0; i < fieldcounts; i ++) {
                if(fieldNames[i].compare("function")!=0) {
                    names[counts] = fieldNames[i];
                    values[counts] = pvArgument->getSubFieldT<PVString>(fieldNames[i])->get();
                    counts += 1;
                }
            }

            PVStructurePtr result = dslRdb->request(functionName, freeze(names), freeze(values));
            return result;
        } else{

            const shared_vector<const string> name = pvArgument->getSubFieldT<PVStringArray>("name")->view();
            const shared_vector<const string> value = pvArgument->getSubFieldT<PVStringArray>("value")->view();
            PVStructurePtr result = dslRdb->request(functionName, name, value);
            return result;
        }

    }catch(epics::pvAccess::RPCRequestException&){
        throw;
    }catch(std::exception& e){
        // since request(RPCRequestException) in our base class has a throw() specifier,
        // if anything else is thrown we abort() :P
        // so must translate all exceptions to RPCRequestException.
        throw epics::pvAccess::RPCRequestException(Status::STATUSTYPE_ERROR,
                                                   std::string("request failed ") + e.what());
    }
}

}}

