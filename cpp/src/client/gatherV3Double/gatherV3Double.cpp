/* gatherV3Double.cpp */
/*
 * Copyright - See the COPYRIGHT that is included with this distribution.
 * This code is distributed subject to a Software License Agreement found
 * in file LICENSE that is included with this distribution.
 */
/* Author Marty Kraimer 2011.11 */

#include <pv/gatherV3Double.h>

namespace epics { namespace pvData {

struct GatherV3DoublePvt;

struct ChannelID
{
    GatherV3DoublePvt *pvt;
    chid theChid;
    int offset;
};

enum State {
    idle,
    connecting,
    connected,
    geting,
};

struct GatherV3DoublePvt
{
    GatherV3DoublePvt(PVStructure::shared_pointer const & pvStructure)
    : pvStructure(pvStructure),
      nttable(NTTable(pvStructure))
    {}
    ~GatherV3DoublePvt(){}
    Mutex mutex;
    Event event;
    PVTimeStamp pvtimeStamp;
    TimeStamp timeStamp;
    PVAlarm pvalarm;
    Alarm alarm;
    String message;
    PVStructure::shared_pointer pvStructure;
    NTTable nttable;
    int numberChannels;
    ChannelID **apchannelID; // array of  pointer to ChanneID
    PVDoubleArray *pvvalue;
    PVDoubleArray *pvdeltaTime;
    PVIntArray *pvseverity;
    PVBooleanArray *pvisConnected;
    PVStringArray *pvchannelName;
    State state;
    int numberConnected;
    int numberCallbacks;
    bool requestOK;
};

static void messageCat(
    GatherV3DoublePvt *pvt,const char *cafunc,int castatus,int channel)
{
    StringArrayData data;
    pvt->pvchannelName->get(0,pvt->numberChannels,&data);
    String name = data.data[channel];
    int len = name.length();
    char buf[len+30];
    //following prevents compiler warning message
    sprintf(buf,"%s %s for channel %s",
        cafunc,
        ca_message(castatus),
        name.c_str());
    pvt->message += String(buf);
}

static void connectionCallback(struct connection_handler_args args)
{
    chid        chid = args.chid;
    ChannelID *id = static_cast<ChannelID *>(ca_puser(chid));
    GatherV3DoublePvt * pvt = id->pvt;
    Lock xx(pvt->mutex);
    int offset = id->offset;
    
    BooleanArrayData data;
    pvt->pvisConnected->get(0,pvt->numberChannels,&data);
    bool isConnected = data.data[offset];
    bool newState = ((ca_state(chid)==cs_conn) ? true : false);
    if(isConnected==newState) {
        throw std::runtime_error("Why extra connection callback");
    }
    data.data[offset] = newState;
    if(newState) {
        pvt->numberConnected++;
        if(pvt->state==connecting && pvt->numberConnected==pvt->numberChannels) {
            pvt->event.signal();
        }
        return;
    }
    pvt->numberConnected--;
}

static void getCallback ( struct event_handler_args args )
{
    chid        chid = args.chid;
    ChannelID *id = static_cast<ChannelID *>(ca_puser(chid));
    GatherV3DoublePvt * pvt = id->pvt;
//    Lock xx(pvt->mutex);
    int offset = id->offset;
    pvt->numberCallbacks++;
    if ( args.status != ECA_NORMAL ) {
          messageCat(pvt,"getCallback",args.status,offset);
          if(pvt->numberCallbacks==pvt->numberChannels) {
              pvt->event.signal();
          }
          return;
    }
    if ( args.type != DBR_TIME_DOUBLE ) {
        throw std::runtime_error("Why extra connection callback");
    }
    const struct dbr_time_double * pTD =
         ( const struct dbr_time_double * ) args.dbr;
    dbr_short_t    severity = pTD->severity;
    epicsTimeStamp stamp = pTD->stamp;
    dbr_double_t   value = pTD->value;
    DoubleArrayData data;
    pvt->pvvalue->get(0,pvt->numberChannels,&data);
    double * pvalue = data.data;
    pvt->pvdeltaTime->get(0,pvt->numberChannels,&data);
    double * pdeltaTime = data.data;
    IntArrayData idata;
    pvt->pvseverity->get(0,pvt->numberChannels,&idata);
    int *pseverity = idata.data;
    pvalue[offset] = value;
    pseverity[offset] = severity;
    int64 secs = stamp.secPastEpoch - posixEpochAtEpicsEpoch;
    int32 nano = stamp.nsec;
    TimeStamp timeStamp(secs,nano);
    double diff = TimeStamp::diff(timeStamp,pvt->timeStamp);
    pdeltaTime[offset] = diff;
    if(pvt->numberCallbacks==pvt->numberChannels) {
        pvt->event.signal();
    }
}

void GatherV3Double::createContext()
{
    static bool isCreated = false;
    static Mutex mutex;
    Lock xx(mutex);
    if(isCreated) return;
    isCreated = true;
    SEVCHK(ca_context_create(ca_enable_preemptive_callback),"ca_context_create");
}

GatherV3Double::GatherV3Double(String channelNames[],int numberChannels)
: pvt(0)
{
    createContext();
    int n = 5;
    FieldConstPtr fields[n];
    FieldCreate *fieldCreate = getFieldCreate();
    fields[0] = fieldCreate->createScalarArray("value",pvDouble);
    fields[1] = fieldCreate->createScalarArray("deltaTime",pvDouble);
    fields[2] = fieldCreate->createScalarArray("severity",pvInt);
    fields[3] = fieldCreate->createScalarArray("isConnected",pvBoolean);
    fields[4] = fieldCreate->createScalarArray("channelName",pvString);
    PVStructure::shared_pointer pvStructure = NTTable::create(
        false,true,true,n,fields);
    pvt = new GatherV3DoublePvt(pvStructure);
    pvt->nttable.attachTimeStamp(pvt->pvtimeStamp);
    pvt->nttable.attachAlarm(pvt->pvalarm);
    pvt->pvtimeStamp.attach(pvStructure->getSubField("timeStamp"));
    pvt->pvalarm.attach(pvStructure->getSubField("alarm"));
    pvt->numberChannels = numberChannels;
    ChannelID **apchannelID = new ChannelID*[numberChannels];
    for(int i=0; i<numberChannels; i++) {
        ChannelID *pChannelID = new ChannelID();
        pChannelID->pvt = pvt;
        pChannelID->theChid = 0;
        pChannelID->offset = i;
        apchannelID[i] = pChannelID;
    }
    pvt->apchannelID = apchannelID;
    pvt->pvvalue = static_cast<PVDoubleArray *>(pvt->nttable.getPVField(0));
    pvt->pvvalue->setCapacity(numberChannels);
    pvt->pvvalue->setCapacityMutable(false);
    DoubleArrayData ddata;
    pvt->pvvalue->get(0,numberChannels,&ddata);
    double *pdouble = ddata.data;
    for (int i=0; i<numberChannels; i++) pdouble[i] = 0.0;
    pvt->pvvalue->setLength(numberChannels);
    pvt->pvdeltaTime = static_cast<PVDoubleArray *>(pvt->nttable.getPVField(1));
    pvt->pvdeltaTime->setCapacity(numberChannels);
    pvt->pvdeltaTime->setCapacityMutable(false);
    pvt->pvdeltaTime->get(0,numberChannels,&ddata);
    pdouble = ddata.data;
    for (int i=0; i<numberChannels; i++) pdouble[i] = 0.0;
    pvt->pvdeltaTime->setLength(numberChannels);
    pvt->pvseverity = static_cast<PVIntArray *>(pvt->nttable.getPVField(2));
    pvt->pvseverity->setCapacity(numberChannels);
    pvt->pvseverity->setCapacityMutable(false);
    IntArrayData idata;
    pvt->pvseverity->get(0,numberChannels,&idata);
    int *pint = idata.data;
    for (int i=0; i<numberChannels; i++) pint[i] = 4;
    pvt->pvseverity->setLength(numberChannels);
    pvt->pvisConnected = static_cast<PVBooleanArray *>(pvt->nttable.getPVField(3));
    pvt->pvisConnected->setCapacity(numberChannels);
    pvt->pvisConnected->setCapacityMutable(false);
    BooleanArrayData bdata;
    pvt->pvisConnected->get(0,numberChannels,&bdata);
    bool *pbool = bdata.data;
    for (int i=0; i<numberChannels; i++) pbool[i] = false;
    pvt->pvisConnected->setLength(numberChannels);
    pvt->pvchannelName = static_cast<PVStringArray *>(pvt->nttable.getPVField(4));
    pvt->pvchannelName->setCapacity(numberChannels);
    pvt->pvchannelName->setCapacityMutable(false);
    pvt->pvchannelName->put(0,numberChannels,channelNames,0);
    pvt->state = idle;
    pvt->numberConnected = 0;
    pvt->numberCallbacks = 0;
    pvt->requestOK = false;
}

GatherV3Double::~GatherV3Double()
{
    for(int i=0; i<pvt->numberChannels; i++) {
        ChannelID *pChannelID = pvt->apchannelID[i];
        delete pChannelID;
    }
    delete pvt->apchannelID;
}

bool GatherV3Double::connect(double timeOut)
{
//    Lock xx(pvt->mutex);
    if(pvt->state!=idle) {
        throw std::runtime_error("GatherV3Double::connect illegal state\n");
    }
    pvt->state = connecting;
    pvt->numberConnected = 0;
    pvt->numberCallbacks = 0;
    pvt->requestOK = true;
    pvt->event.tryWait();
    for(int i=0; i< pvt->numberChannels; i++) {
        StringArrayData data;
        pvt->pvchannelName->get(0,pvt->numberChannels,&data);
        const char * channelName = data.data[i].c_str();
        ChannelID *pchannelID = pvt->apchannelID[i];
        int result = ca_create_channel(
           channelName,
           connectionCallback,
           pchannelID,
           20,
           &pchannelID->theChid);
        if(result!=ECA_NORMAL) {
            throw std::runtime_error("ca_create_channel failed");
        }
    }
    ca_flush_io();
    bool result = pvt->event.wait(timeOut);
    if(result && pvt->requestOK) {
        pvt->state = connected;
        return pvt->requestOK;
    }
    if(pvt->numberConnected!=pvt->numberChannels) {
        char buf[30];
        sprintf(buf,"%d channels are not connected. returning to idle state",
            (pvt->numberChannels - pvt->numberConnected));
        disconnect();
    }
    return false;
}

void GatherV3Double::disconnect()
{
    Lock xx(pvt->mutex);
    if(pvt->state==idle) return;
    pvt->state = idle;
    for(int i=0; i< pvt->numberChannels; i++) {
        chid theChid = pvt->apchannelID[i]->theChid;
        int result = ca_clear_channel(theChid);
    }
}

bool GatherV3Double::get()
{
    Lock xx(pvt->mutex);
    if(pvt->state!=connected) {
        throw std::runtime_error("GatherV3Double::get illegal state\n");
    }
    pvt->state = geting;
    pvt->numberCallbacks = 0;
    pvt->requestOK = true;
    pvt->message = String();
    pvt->event.tryWait();
    for(int i=0; i< pvt->numberChannels; i++) {
        chid theChid = pvt->apchannelID[i]->theChid;
        int result = ca_get_callback(
            DBR_TIME_DOUBLE,
            theChid,
            getCallback,
            pvt->apchannelID[i]);
        if(result!=ECA_NORMAL) {
            messageCat(pvt,"ca_get_callback",result,i);
            pvt->requestOK = false;
        }
    }
    ca_flush_io();
    bool result = pvt->event.wait();
    if(!result) {
        pvt->message += "timeout";
        pvt->requestOK = false;
    }
    return pvt->requestOK;
}

String GatherV3Double::getMessage()
{
    return pvt->message;
}

PVStructure::shared_pointer GatherV3Double::getNTTable()
{
    return pvt->pvStructure;
}

PVDoubleArray * GatherV3Double::getValue()
{
    return pvt->pvvalue;
}

PVDoubleArray * GatherV3Double::getDeltaTime()
{
    return pvt->pvdeltaTime;
}

PVIntArray * GatherV3Double::getSeverity()
{
    return pvt->pvseverity;
}

PVBooleanArray * GatherV3Double::getIsConnected()
{
    return pvt->pvisConnected;
}

PVStringArray * GatherV3Double::getChannelName()
{
    return pvt->pvchannelName;
}

}}
