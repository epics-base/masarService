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

#include <pv/ntfield.h>
#include <pv/nttable.h>
#include <pv/ntnameValuePair.h>

#include <masarService.h>


namespace epics { namespace masar { 

using namespace epics::pvData;
using namespace epics::pvAccess;
using namespace epics::pvIOC;

MasarService::MasarService()
: dslIrmis(createDSL_IRMIS())
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
    String builder;
    builder += "pvArgument ";
//pvArgument->toString(&builder);
//printf("%s\n",builder.c_str());
    bool isNameValue = NTNameValuePair::isNTNameValuePair(pvArgument.get());
    if(isNameValue) {
        NTNameValuePair ntNameValuePair(pvArgument);
        PVString *function = ntNameValuePair.getFunction();
        //Guobao look at function and decide what to do
        PVStructureArray * pvNameValuePairs = ntNameValuePair.getNameValuePairs();
    } else {
        channelRPCRequester->message("illegal argument",errorMessage);
    }
    // Now what to do? What to pass to dslIrmis?
    PVStructure::shared_pointer result = dslIrmis->request(pvArgument);
    // GUOBAO WHAT TO DO?
    // Following just makes up an NTTable
    // You start with this and dslPYIRMIS

    FieldCreate * fieldCreate = getFieldCreate();
    NTField *ntField = NTField::get();
    PVNTField *pvntField = PVNTField::get();
    int n = 2;
    FieldConstPtr fields[2];
    fields[0] = fieldCreate->createScalarArray("position",pvDouble);
    fields[1] = ntField->createAlarmArray("alarms");
    PVStructure::shared_pointer pvStructure = NTTable::create(
        true,true,true,n,fields);
//builder.clear();
//pvStructure->toString(&builder);
//printf("%s\n",builder.c_str());
//builder.clear();
//pvStructure->getStructure()->toString(&builder);
//printf("%s\n",builder.c_str());
    NTTable ntTable(pvStructure);
    PVDoubleArray *pvPositions
        = static_cast<PVDoubleArray *>(ntTable.getPVField(0));
    double positions[2];
    positions[0] = 1.0;
    positions[1] = 2.0;
    pvPositions->put(0,n,positions,0);
    PVStructureArray *pvAlarms
        = static_cast<PVStructureArray *>(ntTable.getPVField(1));
    PVAlarm pvAlarm;
    Alarm alarm;
    PVStructurePtr palarms[n];
    for(int i=0; i<n; i++) {
        palarms[i] = pvntField->createAlarm(0);
        pvAlarm.attach(palarms[i]);
        alarm.setMessage("test");
        alarm.setSeverity(majorAlarm);
        alarm.setStatus(clientStatus);
        pvAlarm.set(alarm);
    }
    pvAlarms->put(0,n,palarms,0);
    String labels[n];
    labels[0] = pvPositions->getField()->getFieldName();
    labels[1] = pvAlarms->getField()->getFieldName();
    PVStringArray *label = ntTable.getLabel();
    label->put(0,n,labels,0);
    channelRPCRequester->requestDone(Status::OK,pvStructure);
}

}}

