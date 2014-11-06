/* gatherV3Data.cpp */
/*
 * Copyright - See the COPYRIGHT that is included with this distribution.
 * This code is distributed subject to a Software License Agreement found
 * in file LICENSE that is included with this distribution.
 */
/* Author Marty Kraimer 2011.11 */

#include <stdexcept>
#include <vector>
#include <sstream>

#include <epicsThread.h>
#include <alarm.h>
#include <alarmString.h>

#include <pv/createRequest.h>
#include <pv/convert.h>
#include <pv/standardPVField.h>

#include <pv/clientFactory.h>
#include <pv/caProvider.h>

#include <pv/gatherV3Data.h>

namespace epics { namespace masar {

using namespace epics::pvData;
using namespace epics::pvAccess;
using namespace epics::nt;
using std::tr1::static_pointer_cast;
using namespace std;
using namespace epics::masar::detail;

static FieldCreatePtr fieldCreate = getFieldCreate();
static PVDataCreatePtr pvDataCreate = getPVDataCreate();
static StandardPVFieldPtr standardPVField = getStandardPVField();
static ConvertPtr convert = getConvert();

enum State {
    idle,
    connecting,
    connected,
    creatingGet,
    getting,
    creatingPut,
    putting,
    destroying,
};

namespace detail {

GatherV3DataChannel::GatherV3DataChannel(
    GatherV3DataPtr const& gatherV3Data, size_t offset)
: gatherV3Data(gatherV3Data),
  offset(offset),
  beingDestroyed(false)
{
//cout << "GatherV3DataChannel::GatherV3DataChannel\n";
}

GatherV3DataChannel::~GatherV3DataChannel()
{
//cout << "GatherV3DataChannel::~GatherV3DataChannel " << offset << endl;
}

void GatherV3DataChannel::destroy()
{
//cout << "GatherV3DataChannel::destroy " << offset << endl;
   { 
        Lock xx(gatherV3Data->mutex);
        if(beingDestroyed) return;
        beingDestroyed = true;
   }
   if(channel) {
      channel->destroy();
      channel.reset();
   }
   gatherV3Data.reset();
   channelGet.reset();
   channelPut.reset();
}

void GatherV3DataChannel::message(
    std::string const &message,
    MessageType messageType)
{
}

void GatherV3DataChannel::channelCreated(
        const Status& status,
        Channel::shared_pointer const & channel)
{
//cout << "GatherV3DataChannel::channelCreated " << offset << endl;
//cout << "state " << channel->getConnectionState() << endl;
}

void GatherV3DataChannel::channelStateChange(
    Channel::shared_pointer const & channel,
    Channel::ConnectionState connectionState)
{
//cout << "GatherV3DataChannel::channelStateChange " << offset << " state " << gatherV3Data->state << endl;
    if(gatherV3Data->state==destroying) return;
    bool isConnected = false;
    if(connectionState==Channel::CONNECTED) isConnected = true;
    Lock xx(gatherV3Data->mutex);
    if(isConnected==gatherV3Data->isConnected[offset]) {
        cout << "gatherV3Data connectionCallback. Why extra connection callback?\n";
        return;
    }
    gatherV3Data->isConnected[offset] = isConnected;;
    if(isConnected) {
         ++gatherV3Data->numberConnected;
        if(gatherV3Data->state==connecting
        && gatherV3Data->numberConnected==gatherV3Data->numberChannel)
        {
            gatherV3Data->event.signal();
        }
    } else {
         --gatherV3Data->numberConnected;
    }
    return;
}

void GatherV3DataChannel::channelGetConnect(
    const Status& status,
    ChannelGet::shared_pointer const & channelGet,
    Structure::const_shared_pointer const & structure)
{
//cout << "GatherV3DataChannel::channelGetConnect\n";
    Lock xx(gatherV3Data->mutex);
    while(true) {
        if(!status.isOK()) {
             string message = gatherV3Data->channelName[offset] +
                  " " + status.getMessage();
             gatherV3Data->message += message;
             gatherV3Data->requestOK = false;
             break;
        }
        FieldConstPtr value = structure->getField("value");
        if(!value) {
            string message = gatherV3Data->channelName[offset] +
                 " no value field";
            gatherV3Data->message += message;
            gatherV3Data->requestOK = false;
            break;
        }
        Type type = value->getType();
        if(type==scalar) {
             ScalarConstPtr scalar = static_pointer_cast<const Scalar>(value);
             PVScalarPtr pvScalar = pvDataCreate->createPVScalar(
                 scalar->getScalarType());
             gatherV3Data->value[offset]->set(pvScalar);
             break;
        }
        if (type==scalarArray) {
             ScalarArrayConstPtr scalarArray =
                 static_pointer_cast<const ScalarArray>(value);
             PVScalarArrayPtr pvScalarArray = pvDataCreate->createPVScalarArray(
                 scalarArray->getElementType());
             gatherV3Data->value[offset]->set(pvScalarArray);
             break;
        }
        if (type==epics::pvData::structure) {
             StructureConstPtr structure =
                 static_pointer_cast<const Structure>(value);
             if(structure->getField("index")
             || (structure->getField("choices"))) {
                 StringArray stringArray;
                 gatherV3Data->value[offset]->set(
                     standardPVField->enumerated(stringArray)); 
             }
             break;
        }
         string message = gatherV3Data->channelName[offset] +
                 "  value field has unsupported type ";
         gatherV3Data->message += message;
         gatherV3Data->requestOK = false;
    }
    ++gatherV3Data->numberCallback;
    if(gatherV3Data->numberCallback==gatherV3Data->numberChannel) {
        gatherV3Data->event.signal();
    }
}

void GatherV3DataChannel::getDone(
    const Status& status,
    ChannelGet::shared_pointer const & channelGet,
    PVStructure::shared_pointer const & pvStructure,
    BitSet::shared_pointer const & bitSet)
{
//cout << "GatherV3DataChannel::getDone\n";
    Lock xx(gatherV3Data->mutex);
    PVFieldPtr pvFrom = pvStructure->getSubField("value");
    PVFieldPtr pvTo = gatherV3Data->value[offset]->get();
    convert->copy(pvFrom,pvTo);
    PVLongPtr pvSec = pvStructure->getSubField<PVLong>("timeStamp.secondsPastEpoch");
    gatherV3Data->secondsPastEpoch[offset] = pvSec->get();
    PVIntPtr pvNano = pvStructure->getSubField<PVInt>("timeStamp.nanoseconds");
    gatherV3Data->nanoseconds[offset] = pvNano->get();
    PVIntPtr pvUser = pvStructure->getSubField<PVInt>("timeStamp.userTag");
    gatherV3Data->userTag[offset] = pvUser->get();
    PVIntPtr pvSev = pvStructure->getSubField<PVInt>("alarm.severity");
    gatherV3Data->alarmSeverity[offset] = pvSev->get();
    PVIntPtr pvStat = pvStructure->getSubField<PVInt>("alarm.status");
    gatherV3Data->alarmStatus[offset] = pvStat->get();
    PVStringPtr pvMess = pvStructure->getSubField<PVString>("alarm.message");
    gatherV3Data->alarmMessage[offset] = pvMess->get();
    ++gatherV3Data->numberCallback;
    if(gatherV3Data->numberCallback==gatherV3Data->numberChannel) {
        gatherV3Data->event.signal();
    }
}

void GatherV3DataChannel::channelPutConnect(
    const Status& status,
    ChannelPut::shared_pointer const & channelPut,
    Structure::const_shared_pointer const & structure)
{
    Lock xx(gatherV3Data->mutex);
    gatherV3Data->putPVStructure[offset] =
       pvDataCreate->createPVStructure(structure);
    gatherV3Data->putBitSet[offset] = BitSetPtr(
         new BitSet(gatherV3Data->putPVStructure[offset]->getNumberFields()));
    ++gatherV3Data->numberCallback;
    if(gatherV3Data->numberCallback==gatherV3Data->numberChannel) {
        gatherV3Data->event.signal();
    }
}

void GatherV3DataChannel::putDone(
    const Status& status,
    ChannelPut::shared_pointer const & channelPut)
{
//cout << "GatherV3DataChannel::getDone\n";
    Lock xx(gatherV3Data->mutex);
    ++gatherV3Data->numberCallback;
    if(gatherV3Data->numberCallback==gatherV3Data->numberChannel) {
        gatherV3Data->event.signal();
    }
}

void GatherV3DataChannel::getDone(
    const Status& status,
    ChannelPut::shared_pointer const & channelPut,
    PVStructure::shared_pointer const & pvStructure,
    BitSet::shared_pointer const & bitSet)
{
}


void  GatherV3DataChannel::connect()
{
//cout << "GatherV3DataChannel::connect()\n";
     channel = gatherV3Data->channelProvider->createChannel(
        gatherV3Data->channelName[offset],getPtrSelf());
}


void GatherV3DataChannel::createGet()
{
   channelGet = channel->createChannelGet(getPtrSelf(),gatherV3Data->pvGetRequest);
}

void GatherV3DataChannel::get()
{
    channelGet->get();
}


void GatherV3DataChannel::createPut()
{
   channelPut = channel->createChannelPut(getPtrSelf(),gatherV3Data->pvPutRequest);
}


void GatherV3DataChannel::put()
{
    PVStructurePtr pvTop = gatherV3Data->putPVStructure[offset];
    PVUnionPtr pvUnion = gatherV3Data->value[offset];
    PVFieldPtr pvFrom = pvUnion->get();
    PVFieldPtr pvTo = pvTop->getSubField("value");
    BitSetPtr bitSet = gatherV3Data->putBitSet[offset];
    bitSet->clear();
    if(pvTo->getField()->getType()==structure) {
        PVStructurePtr pv = static_pointer_cast<PVStructure>(pvFrom);
        PVIntPtr from = pv->getSubField<PVInt>("index");
        pv = static_pointer_cast<PVStructure>(pvTo);
        PVIntPtr to = pv->getSubField<PVInt>("index");
        to->put(from->get());
        bitSet->set(to->getFieldOffset());
    } else {
        convert->copy(pvFrom,pvTo);
        bitSet->set(pvTo->getFieldOffset());
    }
    channelPut->put(pvTop,bitSet);
}


} // end detail




GatherV3DataPtr GatherV3Data::create(
    shared_vector<const std::string> const & channelNames)
{
    if(!getChannelProviderRegistry()->getProvider("pva")) {
       ClientFactory::start();
    }
    if(!getChannelProviderRegistry()->getProvider("caa")) {
       ::epics::pvAccess::ca::CAClientFactory::start();
    }
    NTMultiChannelBuilderPtr builder = NTMultiChannel::createBuilder();
    NTMultiChannelPtr multiChannel = builder->
            value(fieldCreate->createVariantUnion()) ->
            addAlarm()->
            addTimeStamp()->
            addSeverity() ->
            addStatus() ->
            addMessage() ->
            addSecondsPastEpoch() ->
            addNanoseconds() ->
            addUserTag() ->
            addDescriptor() ->
            create();
    PVStringArrayPtr pvChannelName = multiChannel->getChannelName();
    pvChannelName->replace(channelNames);
    GatherV3DataPtr xx(new GatherV3Data(multiChannel,channelNames.size()));
    xx->init();
    return xx;
}

GatherV3Data::GatherV3Data(
    NTMultiChannelPtr const & multiChannel,
    size_t numberChannel)
: channelProvider(getChannelProviderRegistry()->getProvider("ca")),
  multiChannel(multiChannel),
  numberChannel(numberChannel),
  channelName(multiChannel->getChannelName()->view())
{ }

void GatherV3Data::init()
{
//cout << "GatherV3Data::init\n";
ChannelProvider::shared_pointer  xxx = getChannelProviderRegistry()->getProvider("ca");
    CreateRequest::shared_pointer createRequest = CreateRequest::create();
    pvGetRequest = createRequest->createRequest("value,alarm,timeStamp");
    pvPutRequest = createRequest->createRequest("value");
    multiChannel->attachTimeStamp(pvtimeStamp);
    multiChannel->attachAlarm(pvalarm);
    PVStructurePtr pvStructure = multiChannel->getPVStructure();
    pvtimeStamp.attach(pvStructure->getSubField("timeStamp"));
    pvalarm.attach(pvStructure->getSubField("alarm"));
    channel.resize(numberChannel);
    value.resize(numberChannel);
    isConnected.resize(numberChannel);
    secondsPastEpoch.resize(numberChannel);
    nanoseconds.resize(numberChannel);
    userTag.resize(numberChannel);
    alarmSeverity.resize(numberChannel);
    alarmStatus.resize(numberChannel);
    alarmMessage.resize(numberChannel);
    for(size_t i=0; i<numberChannel; ++i) {
        value[i] = pvDataCreate->createPVVariantUnion();
        isConnected[i] = false;
        secondsPastEpoch[i] = 0;
        nanoseconds[i] = 0;
        userTag[i] = 0;
        alarmSeverity[i] = undefinedAlarm;
        alarmStatus[i] = 0;
        alarmMessage[i] = "never connected";
    }
    state = idle;
    numberConnected = 0;
    numberCallback = 0;
    requestOK = false;
    getCreated = false;
    putCreated = false;
    atLeastOneGet = false;
}

GatherV3Data::~GatherV3Data()
{
//cout << "GatherV3Data::~GatherV3Data()\n";
    destroy();
}

bool GatherV3Data::connect(double timeOut)
{
//cout << "GatherV3Data::connect() numberChannel " << numberChannel << endl;
//cout << *multiChannel->getPVStructure() << endl;
    if(state!=idle) {
        throw std::logic_error(
            "GatherV3Data::connect only legal when state is idle\n");
    }
    for(size_t i=0; i<numberChannel; ++i) {
        GatherV3DataChannelPtr xxx(new GatherV3DataChannel(getPtrSelf(),i));
        channel[i] = xxx;
    }
    state = connecting;
    numberConnected = 0;
    numberCallback = 0;
    requestOK = true;
    getCreated = false;
    putCreated = false;
    atLeastOneGet = false;
    event.tryWait();
    for(size_t i=0; i< numberChannel; i++) {
//cout << "isConnected[" << i << "] = false\n";
        isConnected[i] = false;
//cout << "calling channel[" << i << "]->connect()\n";
        channel[i]->connect();
    }
    std::stringstream ss;
    while(true) {
        size_t oldNumber = numberConnected;
        bool result = event.wait(timeOut);
        if(result && requestOK) {
            state = connected;
            return requestOK;
        }
        if(numberConnected!=numberChannel) {
            ss.str("");
            ss << (numberChannel - numberConnected);
            std::string buf = ss.str();
            buf += " channels of ";
            ss.str("");
            ss << numberChannel;
            buf += ss.str();
            buf += " are not connected.";
            message = buf;
            alarm.setMessage(message);
            alarm.setSeverity(invalidAlarm);
            alarm.setStatus(clientStatus);
        }
        if(oldNumber==numberConnected) {
            state = connected;
            return false;
        }
        timeOut = 1.0;
    }
    return false;
}

void GatherV3Data::destroy()
{
//cout << "GatherV3Data::destroy state " << state << endl;
    {
        Lock xx(mutex);
        if(state==idle) return;
        state = destroying;
    }
    for(size_t i=0; i< numberChannel; i++) {
        channel[i]->destroy();
        channel[i].reset();
    }
    channel.clear();
    epicsThreadSleep(1.0);
    putPVStructure.clear();
    putBitSet.clear();
    state = idle;
}

bool GatherV3Data::createGet()
{
    if(state!=connected) {
        throw std::logic_error("GatherV3Data::get illegal state\n");
    }
    state = creatingGet;
    numberCallback = 0;
    requestOK = true;
    message = std::string();
    event.tryWait();
    for(size_t i=0; i< numberChannel; i++) {
        channel[i]->createGet();
    }
    channelProvider->flush();
    event.wait();
    getCreated = true;
    state = connected;
    return requestOK;
}

bool GatherV3Data::get()
{
//cout << "GatherV3Data::get()\n";
    if(state!=connected) {
        throw std::logic_error("GatherV3Data::get illegal state\n");
    }
    if(!getCreated) createGet();
    state = getting;
    numberCallback = 0;
    requestOK = true;
    message = std::string();
    event.tryWait();
    timeStamp.getCurrent();
    alarm.setMessage("");
    alarm.setSeverity(noAlarm);
    alarm.setStatus(noStatus);
    for(size_t i=0; i< numberChannel; i++) {
//cout << "calling channel[" << i << "]->get()\n";
        channel[i]->get();
    }
    channelProvider->flush();
    event.wait();
    PVUnionArrayPtr pvValue = multiChannel->getValue();
    PVBooleanArrayPtr pvIsConnected = multiChannel->getIsConnected();
    PVLongArrayPtr pvSecondsPastEpoch = multiChannel->getSecondsPastEpoch();
    PVIntArrayPtr pvNanoseconds = multiChannel->getNanoseconds();
    PVIntArrayPtr pvUserTag = multiChannel->getUserTag();
    PVIntArrayPtr pvSeverity = multiChannel->getSeverity();
    PVIntArrayPtr pvStatus = multiChannel->getStatus();
    PVStringArrayPtr pvMessage = multiChannel->getMessage();
    shared_vector<PVUnionPtr> xvalue(numberChannel);
    shared_vector<boolean> xisConnected(numberChannel);
    shared_vector<int64> xsecondsPastEpoch(numberChannel);
    shared_vector<int32> xnanoseconds(numberChannel);
    shared_vector<int32> xuserTag(numberChannel);
    shared_vector<int32> xalarmSeverity(numberChannel);
    shared_vector<int32> xalarmStatus(numberChannel);
    shared_vector<string> xalarmMessage(numberChannel);
    for(size_t i=0; i< numberChannel; i++) {
        xvalue[i] = pvDataCreate->createPVVariantUnion();
        xvalue[i]->set(value[i]->get());
        xisConnected[i] = isConnected[i];
        xsecondsPastEpoch[i] = secondsPastEpoch[i];
        xnanoseconds[i] = nanoseconds[i];
        xuserTag[i] = userTag[i];
        xalarmSeverity[i] = alarmSeverity[i];
        xalarmStatus[i] = alarmStatus[i];
        xalarmMessage[i] = alarmMessage[i];
    }
    pvValue->replace(freeze(xvalue));
    pvIsConnected->replace(freeze(xisConnected));
    pvSecondsPastEpoch->replace(freeze(xsecondsPastEpoch));
    pvNanoseconds->replace(freeze(xnanoseconds));
    pvUserTag->replace(freeze(xuserTag));
    pvSeverity->replace(freeze(xalarmSeverity));
    pvStatus->replace(freeze(xalarmSeverity));
    pvMessage->replace(freeze(xalarmMessage));
    atLeastOneGet = true;
    state = connected;
    return requestOK;
}

bool GatherV3Data::createPut()
{
    if(state!=connected) {
        throw std::logic_error("GatherV3Data::cretePut illegal state\n");
    }
    if(!atLeastOneGet) get();
    putPVStructure.resize(numberChannel);
    putBitSet.resize(numberChannel);
    state = creatingPut;
    numberCallback = 0;
    requestOK = true;
    message = std::string();
    event.tryWait();
    for(size_t i=0; i< numberChannel; i++) {
        channel[i]->createPut();
    }
    channelProvider->flush();
    event.wait();
    putCreated = true;
    state = connected;
    return requestOK;
}

bool GatherV3Data::put()
{
    if(state!=connected) {
        throw std::logic_error("GatherV3Data::put illegal state\n");
    }
    if(!putCreated) createPut();
    state = putting;
    numberCallback = 0;
    requestOK = true;
    message = std::string();
    event.tryWait();
    for(size_t i=0; i< numberChannel; i++) {
        channel[i]->put();
    }
    channelProvider->flush();
    event.wait();
    putCreated = true;
    state = connected;
    return requestOK;

}

}}
