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
using namespace epics::pvIOC;

MasarService::MasarService()
: dslRdb(createDSL_RDB())
{}

MasarService::~MasarService()
{
printf("MasarService::~MasarService()\n");
}

void MasarService::destroy()
{
printf("MasarService::destroy()\n");
}

void MasarService::request(
    ChannelRPCRequester::shared_pointer const & channelRPCRequester,
    epics::pvData::PVStructure::shared_pointer const & pvArgument)
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
//pvArgument->toString(&builder);
//printf("%s\n",builder.c_str());
    if(!NTNameValue::isNTNameValue(pvArgument)) {
        StringArray names;
        FieldConstPtrArray fields;
        NTTablePtr ntTable(NTTable::create(
            false,true,true,names,fields));
        PVStructurePtr pvStructure = ntTable->getPVStructure();
        Alarm alarm;
        PVAlarm pvAlarm;
        pvAlarm.attach(ntTable->getTimeStamp());
        alarm.setMessage("pvArgument is not an NTNameValue");
        alarm.setSeverity(majorAlarm);
        pvAlarm.set(alarm);
        channelRPCRequester->requestDone(Status::Ok,pvStructure);
        return;
    }
    NTNameValuePtr ntNameValue(NTNameValue::create(true,true,true));
    PVStringPtr &function = ntNameValue->getFunction();
    String functionName;
    for(int i=0; i<numberFunctions; i++) {
        if(function->get().compare(functionNames[i])==0) {
             functionName = functionNames[i];
             break;
        }
    }
    if(functionName.c_str()==0) {
        StringArray names;
        FieldConstPtrArray fields;
        NTTablePtr ntTable(NTTable::create(
            false,true,true,names,fields));
        PVStructurePtr pvStructure = ntTable->getPVStructure();
        Alarm alarm;
        PVAlarm pvAlarm;
        pvAlarm.attach(ntTable->getTimeStamp());
        alarm.setMessage("pvArgument has an unsupported function");
        alarm.setSeverity(majorAlarm);
        pvAlarm.set(alarm);
        channelRPCRequester->requestDone(Status::Ok,pvStructure);
        return;
    }
    PVStringArray * pvNames = ntNameValue.getNames();
    PVStringArray * pvValues = ntNameValue.getValues();
    StringArrayData data;
    int num = pvNames->getLength();
    pvNames->get(0,num,&data);
    String *names = data.data;
    pvValues->get(0,num,&data);
    String *values = data.data;
    PVStructure::shared_pointer result = dslRdb->request(
        functionName,num,names,values);
    channelRPCRequester->requestDone(Status::OK,result);
}

}}

