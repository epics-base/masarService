/* masarService.h */
/**
 * Copyright - See the COPYRIGHT that is included with this distribution.
 * EPICS pvDataCPP is distributed subject to a Software License Agreement found
 * in file LICENSE that is included with this distribution.
 */
#ifndef MASAR_SERVICE_H
#define MASAR_SERVICE_H
#include <string>
#include <cstring>
#include <stdexcept>
#include <memory>

#include <pv/service.h>
#include <pv/dslPYIRMIS.h>

namespace epics { namespace masar { 

class MasarService;

class MasarService :
  public virtual epics::pvIOC::ServiceRPC,
  public std::tr1::enable_shared_from_this<MasarService>
{
public:
    POINTER_DEFINITIONS(MasarService);
    MasarService();
    virtual ~MasarService();
    virtual void destroy();
    virtual void request(
        epics::pvAccess::ChannelRPCRequester::shared_pointer const & channelRPCRequester,
        epics::pvData::PVStructure::shared_pointer const & pvArgument);
private:
    MasarService::shared_pointer getPtrSelf()
    {
        return shared_from_this();
    }
    DSL::shared_pointer dslIrmis;
};

}}

#endif  /* MASAR_SERVICE_H */
