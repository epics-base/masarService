/* dslPY.cpp */
/**
 * Copyright - See the COPYRIGHT that is included with this distribution.
 * This code is distributed subject to a Software License Agreement found
 * in file LICENSE that is included with this distribution.
 */

#undef _POSIX_C_SOURCE
#undef _XOPEN_SOURCE
#include <Python.h>

#include <string>
#include <stdexcept>
#include <memory>
#include <vector>

#include <db_access.h>

#include <pv/pvIntrospect.h>
#include <pv/pvData.h>
#include <pv/dsl.h>
#include <pv/nt.h>

#include <pv/gatherV3Data.h>

namespace epics { namespace masar { 

using namespace std;
using namespace epics::pvData;
using namespace epics::pvAccess;
using namespace epics::nt;
using std::tr1::static_pointer_cast;

static FieldCreatePtr fieldCreate = getFieldCreate();
static PVDataCreatePtr pvDataCreate = getPVDataCreate();

class DSL_RDB;
typedef std::tr1::shared_ptr<DSL_RDB> DSL_RDBPtr;

class DSL_RDB :
    public DSL,
    public std::tr1::enable_shared_from_this<DSL_RDB>
{
public:
    POINTER_DEFINITIONS(DSL_RDB);
    DSL_RDB();
    virtual ~DSL_RDB();
    virtual void destroy();
    virtual PVStructurePtr request(
        string const & functionName,shared_vector<const string> const &names,shared_vector<const string> const &values);
    bool init();
private:
    DSL_RDBPtr getPtrSelf()
    {
        return shared_from_this();
    }

    PyObject * prequest;
    PyObject * pgetchannames;
};

DSL_RDB::DSL_RDB()
    : DSL(),prequest(0), pgetchannames(0)
{
   PyThreadState *py_tstate = NULL;
   Py_Initialize();
   PyEval_InitThreads();
   py_tstate = PyGILState_GetThisThreadState();
   PyEval_ReleaseThread(py_tstate);
}

DSL_RDB::~DSL_RDB()
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    if(prequest!=0) Py_XDECREF(prequest);
    if(pgetchannames!=0) Py_XDECREF(pgetchannames);
    PyGILState_Release(gstate);
    PyGILState_Ensure();
    Py_Finalize();
}

bool DSL_RDB::init()
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject * module = PyImport_ImportModule("masarserver.dslPY");
    if(module==0) {
        string message("dslPY");
        message += " does not exist or is not a python module";
        cout << "DSL_RDB::init " << message << endl;
        return false;
    }
    PyObject *pclass = PyObject_GetAttrString(module, "DSL");
    if(pclass==0) {
        string message("class DSL");
        message += " does not exist";
        cout << "DSL_RDB::init " << message << endl;
        Py_XDECREF(module);
        return false;
    }
    PyObject *pargs = Py_BuildValue("()");
    if (pargs == NULL) {
        Py_DECREF(pclass);
        cout <<"Can't build arguments list\n";
        return false;
    }
    PyObject *pinstance = PyEval_CallObject(pclass,pargs);
    Py_DECREF(pargs);
    if(pinstance==0) {
        string message("class DSL");
        message += " constructor failed";
        cout << "DSL_RDB::init " << message << endl;
        Py_XDECREF(pclass);
        Py_XDECREF(module);
        return false;
    }
    prequest = PyObject_GetAttrString(pinstance, "request");
    if(prequest==0) {
        string message("DSL::request");
        message += " could not attach to method";
        cout << "DSL_RDB::init " << message << endl;
        Py_XDECREF(pinstance);
        Py_XDECREF(pclass);
        Py_XDECREF(module);
        return false;
    }
    pgetchannames = PyObject_GetAttrString(pinstance, "retrieveChannelNames");
    if(pgetchannames==0) {
        string message("DSL::request");
        message += " could not attach to method";
        cout << "DSL_RDB::init " << message << endl;
        Py_XDECREF(pinstance);
        Py_XDECREF(pclass);
        Py_XDECREF(module);
        return false;
    }
    Py_XDECREF(pinstance);
    Py_XDECREF(pclass);
    Py_XDECREF(module);
    PyGILState_Release(gstate);
    return true;
}

void DSL_RDB::destroy() {}

static NTMultiChannelPtr noDataMultiChannel(std::string message) {
    NTMultiChannelBuilderPtr builder = NTMultiChannel::createBuilder();
    NTMultiChannelPtr ntMultiChannel = builder->
            addAlarm()->
            addTimeStamp()->
            create();
    PVStructurePtr pvStructure = ntMultiChannel->getPVStructure();

    // Set alarm and severity
    PVAlarm pvAlarm;
    Alarm alarm;
    ntMultiChannel->attachAlarm(pvAlarm);

    alarm.setMessage(message);
    alarm.setSeverity(majorAlarm);
    alarm.setStatus(clientStatus);
    pvAlarm.set(alarm);

    // set time stamp
    PVTimeStamp pvTimeStamp;
    ntMultiChannel->attachTimeStamp(pvTimeStamp);
    TimeStamp timeStamp;
    timeStamp.getCurrent();
    timeStamp.setUserTag(0);
    pvTimeStamp.set(timeStamp);

    return ntMultiChannel;
}

static NTMultiChannelPtr getLiveMachine(shared_vector<const string> const & channelName)
{
cout << "getLiveMachine\n";
    GatherV3DataPtr gather = GatherV3Data::create(channelName);

    // wait one second, which is a magic number for now.
    // The waiting time might be removed later after stability test.
    bool result = gather->connect(1.0);
    if(!result) {
cout << "getLiveMachine connect failed\n";
        return noDataMultiChannel("connect failed");
    }
    result = gather->get();
    if(!result) {
cout << "getLiveMachine get failed\n";
        return noDataMultiChannel("get failed");
    }
    NTMultiChannelPtr ntmultiChannel = gather->getNTMultiChannel();
    // set time stamp, no need anymore since gather put time stamp on it
    //PVTimeStamp pvTimeStamp;
    //ntmultiChannel->attachTimeStamp(pvTimeStamp);
    //TimeStamp timeStamp;
    //timeStamp.getCurrent();
    //timeStamp.setUserTag(0);
    //pvTimeStamp.set(timeStamp);
    gather->destroy();
cout << "getLiveMachine success\n";
    return ntmultiChannel;
}

static NTMultiChannelPtr retrieveSnapshot(PyObject * list)
{
    Py_ssize_t top_len = PyList_Size(list);
    if (top_len != 2) {
        return noDataMultiChannel("Wrong format for returned data from dslPY when retrieving masar data.");
    }
    PyObject * data_array = PyList_GetItem(list, 1); // get data array
    // data length in each field
    // (the first row is a description instead of real data)
    Py_ssize_t numberChannels = PyList_Size(data_array) - 1;
    if (numberChannels < 0)
        return noDataMultiChannel("no channel found in this snapshot.");

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
            add("dbrType",fieldCreate->createScalarArray(pvInt)) ->
            create();
    shared_vector<string> channelName(numberChannels);
    shared_vector<PVUnionPtr> channelValue(numberChannels);
    shared_vector<boolean> isConnected(numberChannels);
    shared_vector<int64> secondsPastEpoch(numberChannels);
    shared_vector<int32> nanoseconds(numberChannels);
    shared_vector<int32> userTag(numberChannels);
    shared_vector<int32> severity(numberChannels);
    shared_vector<int32> status(numberChannels);
    shared_vector<string> message(numberChannels);
    shared_vector<int32> dbr_type(numberChannels);
    PyObject * sublist;
    for(size_t index = 0; index < (size_t)numberChannels; index++ ){
        channelValue[index] = pvDataCreate->createPVVariantUnion();
        sublist = PyList_GetItem(data_array, index+1);
        // ('pv name', 'string value', 'double value', 'long value', 'dbr type', 'isConnected',
        //  'secondsPastEpoch', 'nanoSeconds', 'timeStampTag', 'alarmSeverity', 'alarmStatus', 'alarmMessage'
        //  'is_array', 'array_value')
        PyObject * temp = PyTuple_GetItem(sublist,0);
        channelName[index] = (PyString_AsString(temp)==NULL) ? "" : PyString_AsString (temp);
        temp = PyTuple_GetItem(sublist,4);
        dbr_type[index] = PyLong_AsLong(temp);
        temp = PyTuple_GetItem(sublist,5);
        isConnected[index] = (PyLong_AsLong(temp)==0) ? false : true;
        temp = PyTuple_GetItem(sublist,6);
        secondsPastEpoch[index] = PyLong_AsLongLong(temp);
        temp = PyTuple_GetItem(sublist,7);
        nanoseconds[index] = PyLong_AsLong(temp);
        temp = PyTuple_GetItem(sublist,8);
        userTag[index] = PyLong_AsLong(temp);
        temp = PyTuple_GetItem(sublist,9);
        severity[index] = PyLong_AsLong(temp);
        temp = PyTuple_GetItem(sublist,10);
        status[index] = PyLong_AsLong(temp);
        temp = PyTuple_GetItem(sublist,11);
        message[index] = PyString_AsString(temp);
        //int32 dbr_type = PyLong_AsLong(PyTuple_GetItem(sublist,4));
        int32 is_array = PyLong_AsLong(PyTuple_GetItem(sublist,12));
        bool isArray = (is_array==0) ? false : true;
        if(!isArray) {
            if(dbr_type[index]==DBR_STRING) {
                char * str = PyString_AsString(PyTuple_GetItem(sublist,1));
                PVStringPtr pvString = pvDataCreate->createPVScalar<PVString>();
                pvString->put(str);
                channelValue[index]->set(pvString);
                continue;
            }
            if(dbr_type[index]==DBR_LONG) {
                int32 val = PyLong_AsLong(PyTuple_GetItem(sublist,3));
                PVIntPtr pvInt = pvDataCreate->createPVScalar<PVInt>();
                pvInt->put(val);
                channelValue[index]->set(pvInt);
                continue;
            }
            if(dbr_type[index]==DBR_DOUBLE) {
                double val = PyFloat_AsDouble(PyTuple_GetItem(sublist,2));
                PVDoublePtr pvDouble = pvDataCreate->createPVScalar<PVDouble>();
                pvDouble->put(val);
                channelValue[index]->set(pvDouble);
                continue;
            }
        } else {
            PyObject * arrayValueList = PyTuple_GetItem(sublist, 13);
            if(dbr_type[index]==DBR_STRING) {
                shared_vector<string> values;
                if (PyList_Check(arrayValueList)) {
                    size_t array_len = (size_t)PyList_Size(arrayValueList);
                    values.resize(array_len);
                    for (size_t i = 0; i < array_len; i++){
                        char * str = PyString_AsString(PyList_GetItem(arrayValueList, i));
                        values[i] = string(str);;
                    }
                } else if (PyTuple_Check(arrayValueList)) {
                    size_t array_len = (size_t)PyTuple_Size(arrayValueList);
                    values.resize(array_len);
                    for (size_t i = 0; i < array_len; i++){
                        char * str = PyString_AsString(PyTuple_GetItem(arrayValueList, i));
                        values[i] = string(str);;
                    }
                }
                PVStringArrayPtr pvStringArray = pvDataCreate->createPVScalarArray<PVStringArray>();
                pvStringArray->replace(freeze(values));
                channelValue[index]->set(pvStringArray);
                continue;
            }
            if(dbr_type[index]==DBR_LONG || dbr_type[index]==DBR_INT || dbr_type[index]==DBR_CHAR) {
                shared_vector<int> values;
                if (PyList_Check(arrayValueList)) {
                    size_t array_len = (size_t)PyList_Size(arrayValueList);
                    values.resize(array_len);
                    for (size_t i = 0; i < array_len; i++){
                        values[i] = PyLong_AsLong(PyList_GetItem(arrayValueList, i));
                    }
                } else if (PyTuple_Check(arrayValueList)) {
                    size_t array_len = (size_t)PyTuple_Size(arrayValueList);
                    values.resize(array_len);
                    for (size_t i = 0; i < array_len; i++){
                        values[i] = PyLong_AsLong(PyTuple_GetItem(arrayValueList, i));
                    }
                }
                PVIntArrayPtr pvIntArray = pvDataCreate->createPVScalarArray<PVIntArray>();
                pvIntArray->replace(freeze(values));
                channelValue[index]->set(pvIntArray);
                continue;
            }
            if(dbr_type[index]==DBR_DOUBLE || dbr_type[index]==DBR_FLOAT) {
                shared_vector<double> values;
                if (PyList_Check(arrayValueList)) {
                    size_t array_len = (size_t)PyList_Size(arrayValueList);
                    values.resize(array_len);
                    for (size_t i = 0; i < array_len; i++){
                        values[i] = PyFloat_AsDouble(PyList_GetItem(arrayValueList, i));
                    }
                } else if (PyTuple_Check(arrayValueList)) {
                    size_t array_len = (size_t)PyTuple_Size(arrayValueList);
                    values.resize(array_len);
                    for (size_t i = 0; i < array_len; i++){
                        values[i] = PyFloat_AsDouble(PyTuple_GetItem(arrayValueList, i));
                    }
                }
                PVDoubleArrayPtr pvDoubleArray = pvDataCreate->createPVScalarArray<PVDoubleArray>();
                pvDoubleArray->replace(freeze(values));
                channelValue[index]->set(pvDoubleArray);
                continue;
            }
        }
    }

    multiChannel->getChannelName()->replace(freeze(channelName));
    multiChannel->getValue()->replace(freeze(channelValue));
    multiChannel->getPVStructure()->getSubField<PVIntArray>("dbrType")->replace(freeze(dbr_type));
    multiChannel->getIsConnected()->replace(freeze(isConnected));
    multiChannel->getSecondsPastEpoch()->replace(freeze(secondsPastEpoch));
    multiChannel->getNanoseconds()->replace(freeze(nanoseconds));
    multiChannel->getUserTag()->replace(freeze(userTag));
    multiChannel->getSeverity()->replace(freeze(severity));
    multiChannel->getStatus()->replace(freeze(status));
    multiChannel->getMessage()->replace(freeze(message));
    return multiChannel;
}

static NTMultiChannelPtr saveSnapshot(PyObject * list, NTMultiChannelPtr data)
{
    // Get save masar event id
    // -1 means saveSnapshot failure
    int64 eid = -2;

    if (PyTuple_Check(list)){
        PyObject * plist = PyTuple_GetItem(list, 0);
        PyObject * pstatus = PyList_GetItem(plist,0);
        eid = PyLong_AsLongLong(pstatus);
    } else if(PyList_Check(list)) {
        PyObject * pstatus = PyList_GetItem(list,0);
        eid = PyLong_AsLongLong(pstatus);
    } else {
        return noDataMultiChannel("Wrong format for returned data from dslPY.");
    }

    if (eid == -1) {
        return noDataMultiChannel("Machine preview failed.");
    } else {
        // Set alarm and severity
        PVAlarm pvAlarm;
        Alarm alarm;
        data->attachAlarm(pvAlarm);

        alarm.setMessage("Machine preview Successed.");
        alarm.setSeverity(majorAlarm);
        alarm.setStatus(clientStatus);
        pvAlarm.set(alarm);

        // set time stamp
        PVTimeStamp pvTimeStamp;
        data->attachTimeStamp(pvTimeStamp);
        TimeStamp timeStamp;
        timeStamp.getCurrent();
        timeStamp.setUserTag(eid);
        pvTimeStamp.set(timeStamp);
        return data;
    }
}

static NTScalarPtr noDataScalar(std::string message)
{
    NTScalarBuilderPtr builder = NTScalar::createBuilder();
    NTScalarPtr ntscalar = builder->
            value(pvBoolean) ->
            addAlarm()->
            addTimeStamp()->
            create();
    PVStructurePtr pvStructure = ntscalar->getPVStructure();

    PVBooleanPtr pvBool = pvStructure->getSubField<PVBoolean>("value");
    pvBool->put(false);
    // Set alarm and severity
    PVAlarm pvAlarm;
    Alarm alarm;
    ntscalar->attachAlarm(pvAlarm);

    alarm.setMessage(message);
    alarm.setSeverity(majorAlarm);
    alarm.setStatus(clientStatus);
    pvAlarm.set(alarm);

    // set time stamp
    PVTimeStamp pvTimeStamp;
    ntscalar->attachTimeStamp(pvTimeStamp);
    TimeStamp timeStamp;
    timeStamp.getCurrent();
    timeStamp.setUserTag(0);
    pvTimeStamp.set(timeStamp);

    return ntscalar;
}

static NTScalarPtr updateSnapshotEvent(PyObject * list)
{
    // Get save masar event id
    // -1 means updateSnapshotEvent failure
    int64 eid = -2;
    if (PyTuple_Check(list)){
        PyObject * plist = PyTuple_GetItem(list, 0);
        PyObject * pstatus = PyList_GetItem(plist,0);
        eid = PyLong_AsLongLong(pstatus);
    } else if(PyList_Check(list)) {
        PyObject * pstatus = PyList_GetItem(list,0);
        eid = PyLong_AsLongLong(pstatus);
    } else {
        return noDataScalar("Wrong format for returned data from dslPY.");
    }

    NTScalarBuilderPtr builder = NTScalar::createBuilder();
    NTScalarPtr ntscalar = builder ->
        value(pvBoolean) ->
        addAlarm()->
        addTimeStamp()->
        create();
    PVStructurePtr pvStructure = ntscalar->getPVStructure();
    PVBooleanPtr pvBool = pvStructure->getSubField<PVBoolean>("value");
    if (eid >= 0) {
        pvBool->put(true);
    } else {
        pvBool->put(false);
    }

    PVAlarm pvAlarm;
    Alarm alarm;
    ntscalar->attachAlarm(pvAlarm);
    if (eid >= 0) {
        alarm.setMessage("Success to save snapshot preview.");
    } else {
        alarm.setMessage("Falied to save snapshot preview.");
    }
    alarm.setSeverity(majorAlarm);
    alarm.setStatus(clientStatus);
    pvAlarm.set(alarm);
    PVTimeStamp pvTimeStamp;
    ntscalar->attachTimeStamp(pvTimeStamp);
    TimeStamp timeStamp;
    timeStamp.getCurrent();
    timeStamp.setUserTag(0);
    pvTimeStamp.set(timeStamp);
    return ntscalar;
}

static NTTablePtr noDataTable(string message)
{
    NTTableBuilderPtr builder = NTTable::createBuilder();
    NTTablePtr ntTable = builder->
            add("status", pvBoolean)->
            addAlarm()->
            addTimeStamp()->
            create();
    PVStructurePtr pvStructure = ntTable->getPVStructure();
    PVBooleanArrayPtr pvBoolVal =
        pvStructure->getSubField<PVBooleanArray>("value.status");
    shared_vector<boolean> temp(1);
    temp[0]=false;
    pvBoolVal->replace(freeze(temp));

    // Set alarm and severity
    PVAlarm pvAlarm;
    Alarm alarm;
    ntTable->attachAlarm(pvAlarm);

    alarm.setMessage(message);
    alarm.setSeverity(majorAlarm);
    alarm.setStatus(clientStatus);
    pvAlarm.set(alarm);

    // set time stamp
    PVTimeStamp pvTimeStamp;
    ntTable->attachTimeStamp(pvTimeStamp);
    TimeStamp timeStamp;
    timeStamp.getCurrent();
    timeStamp.setUserTag(0);
    pvTimeStamp.set(timeStamp);

    return ntTable;
}

static NTTablePtr retrieveServiceConfigEvents(PyObject * list, long numeric)
{
    Py_ssize_t list_len = PyList_Size(list);
    // data order in the tuple
    // for example result of service config
    // (service_config_id, service_config_name, service_config_desc, service_config_create_date,
    //  service_config_version, and service_name)
    PyObject * labelList = PyList_GetItem(list, 0);
    Py_ssize_t tuple_size = PyTuple_Size(labelList);
    if (tuple_size < numeric) {
        numeric = tuple_size; // all array are numbers
    }
    shared_vector<string> label(tuple_size);
    for(int i=0; i<tuple_size; ++i) {
         label[i] = string(PyString_AsString(PyTuple_GetItem(labelList, i)));
    }
    NTTableBuilderPtr builder = NTTable::createBuilder();
    for(int i=0 ; i< tuple_size; ++i) {
        ScalarType scalarType = (i<numeric) ? pvLong : pvString;
        builder->add(label[i],scalarType);
    }
    NTTablePtr ntTable = builder->
            addAlarm()->
            addTimeStamp()->
            create();
    PVStructurePtr pvStructure = ntTable->getPVStructure();

    std::vector<shared_vector<int64> > scIdVals(numeric);
    for(size_t i=0; i<scIdVals.size(); i++) {
        scIdVals[i].resize(list_len-1);
    }

    std::vector<shared_vector<string> > vals (tuple_size-numeric);
    for (size_t i = 0; i < vals.size(); i++){
        vals[i].resize(list_len-1);
    }
    // Get values for each fields from list
    PyObject * sublist;
    for (int index = 1; index < list_len; index++ ){
        sublist = PyList_GetItem(list, index);
        for (int i = 0; i < tuple_size; i ++) {
            PyObject * temp = PyTuple_GetItem(sublist, i);
            if (i < numeric){
                // PyLong_Check for type check?
                scIdVals[i][index-1] = PyLong_AsLongLong(temp);
            } else {
                // PyString_Check for type check?
                if (PyString_AsString(temp) == NULL) {
                    vals[i-numeric][index-1] = "";
                } else {
                    vals[i-numeric][index-1] = PyString_AsString(temp);
                }
            }
        }
    }

    // set value to each numeric field
    for (int i = 0; i < numeric; i ++) {
        //PVLongArrayPtr pvLongArray = ntTable->getColumn<PVLongArray>(label[i]);
        PVLongArrayPtr pvLongArray = pvStructure->getSubField<PVLongArray>("value."+label[i]);
        //TODO: add logging information here
        if (!pvLongArray) cout << "empty sub field for " << label[i] << endl;
        else pvLongArray->replace(freeze(scIdVals[i]));
    }
    // set value to each string field
    for (int i = numeric; i < tuple_size; i ++) {
        //PVStringArrayPtr pvStringArray = ntTable->getColumn<PVStringArray>(label[i]);
        PVStringArrayPtr pvStringArray = pvStructure->getSubField<PVStringArray>("value."+label[i]);
        //TODO: add logging information here
        if (!pvStringArray) cout << "empty sub field for " << label[i] << endl;
        else pvStringArray->replace(freeze(vals[i-numeric]));
    }

    PVTimeStamp pvTimeStamp;
    ntTable->attachTimeStamp(pvTimeStamp);
    TimeStamp timeStamp;
    timeStamp.getCurrent();
    timeStamp.setUserTag(0);
    pvTimeStamp.set(timeStamp);

    return ntTable;
}

PVStructurePtr DSL_RDB::request(
    string const & functionName,shared_vector<const string> const & names,shared_vector<const string> const &values)
{
    if (functionName.compare("getLiveMachine")==0) {
        NTMultiChannelPtr ntmultiChannel = getLiveMachine(values);
        return ntmultiChannel->getPVStructure();
    }
    int num = names.size();
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject *pyDict = PyDict_New();
    for (int i = 0; i < num; i ++) {
        PyObject *pyValue = Py_BuildValue("s",values[i].c_str());
        PyDict_SetItemString(pyDict,names[i].c_str(),pyValue);
    }
    PyObject *pyValue = Py_BuildValue("s",functionName.c_str());
    PyDict_SetItemString(pyDict,"function",pyValue);
    if (functionName.compare("updateSnapshotEvent")==0) {
        NTScalarPtr pvReturn;
        PyObject * pyTuple = PyTuple_New(1);
        // put dictionary into the tuple
        PyTuple_SetItem(pyTuple, 0, pyDict);
        PyObject *result = PyEval_CallObject(prequest,pyTuple);
        Py_DECREF(pyTuple);
        if(result == NULL) {
            pvReturn = noDataScalar("No data entry found in database.");
        } else {
            PyObject *list = 0;
            if(!PyArg_ParseTuple(result,"O!:dslPY", &PyList_Type,&list))
            {
               throw std::runtime_error("Wrong format for returned data from dslPY.");
            }
            pvReturn = updateSnapshotEvent(list);
        }
        Py_DECREF(result);
        PyGILState_Release(gstate);
        return pvReturn->getPVStructure();
    } else if (functionName.compare("retrieveSnapshot")==0) {
        NTMultiChannelPtr pvReturn;
        PyObject * pyTuple = PyTuple_New(1);
        // put dictionary into the tuple
        PyTuple_SetItem(pyTuple, 0, pyDict);
        PyObject *result = PyEval_CallObject(prequest,pyTuple);
        Py_DECREF(pyTuple);
        if(result == NULL) {
            pvReturn = noDataMultiChannel("No data entry found in database.");
        } else {
            PyObject *list = 0;
            if(!PyArg_ParseTuple(result,"O!:dslPY", &PyList_Type,&list))
            {
               throw std::runtime_error("Wrong format for returned data from dslPY.");
            }
            pvReturn = retrieveSnapshot(list);
        }
        Py_DECREF(result);
        PyGILState_Release(gstate);
        return pvReturn->getPVStructure();
    } else if (functionName.compare("saveSnapshot")==0) {
        NTMultiChannelPtr pvReturn;
        // A tuple is needed to pass to Python as parameter.
        PyObject * pyTuple = PyTuple_New(1);
        // put dictionary into the tuple
        PyTuple_SetItem(pyTuple, 0, pyDict);
        PyObject *pchannelnames = PyEval_CallObject(pgetchannames, pyTuple);
        if(pchannelnames == NULL) {
            pvReturn = noDataMultiChannel("Failed to retrieve channel names.");
            Py_DECREF(pchannelnames);
        } else {
            Py_ssize_t list_len = PyList_Size(pchannelnames);

            shared_vector<string> channames(list_len);
            PyObject * name;
            for (ssize_t i = 0; i < list_len; i ++) {
                name = PyList_GetItem(pchannelnames, i);
                channames[i] = PyString_AsString(name);
            }
            if (channames.size() == 0)
                pvReturn = noDataMultiChannel("Failed to retrieve channel names.");
            else {
                shared_vector<const string> names(freeze(channames));
                Py_DECREF(pchannelnames);
                NTMultiChannelPtr data = getLiveMachine(names);
                PVStructurePtr pvStructure = data->getPVStructure();

                // create a tuple is needed to pass to Python as parameter.
                PyObject * pdata = PyCapsule_New(&pvStructure, "pvStructure", 0);
                PyObject * pyTuple2 = PyTuple_New(2);

                // first value is the data from live machine
                PyTuple_SetItem(pyTuple2, 0, pdata);
                // second value is the dictionary
                PyTuple_SetItem(pyTuple2, 1, pyDict);
                PyObject *result = PyEval_CallObject(prequest,pyTuple2);
                if(result == NULL) {
                    pvReturn = noDataMultiChannel("Failed to save snapshot.");
                } else {
                    pvReturn = saveSnapshot(result, data);
                    Py_DECREF(result);
                }
                Py_DECREF(pyTuple2);
            }
        }
        Py_DECREF(pyTuple);
        PyGILState_Release(gstate);
        return pvReturn->getPVStructure();
    } else {
        NTTablePtr pvReturn;
        // A tuple is needed to pass to Python as parameter.
        PyObject * pyTuple = PyTuple_New(1);
        // put dictionary into the tuple
        PyTuple_SetItem(pyTuple, 0, pyDict);

        PyObject *result = PyEval_CallObject(prequest,pyTuple);
        Py_DECREF(pyTuple);
        if(result == NULL) {
            pvReturn = noDataTable("No data entry found in database.");
        } else {
            PyObject *list = 0;
            if(!PyArg_ParseTuple(result,"O!:dslPY", &PyList_Type,&list))
            {
                throw std::runtime_error("Wrong format for returned data from dslPY.");
            }
            if (functionName.compare("retrieveServiceEvents")==0) {
                pvReturn = retrieveServiceConfigEvents(list, 2);
            } else if (functionName.compare("retrieveServiceConfigs")==0) {
                pvReturn = retrieveServiceConfigEvents(list, 1);
            } else if (functionName.compare("retrieveServiceConfigProps")==0) {
                pvReturn = retrieveServiceConfigEvents(list, 2);
            } else {
                pvReturn = noDataTable("Did not find data");
            }
            Py_DECREF(result);
        }
        PyGILState_Release(gstate);
        return pvReturn->getPVStructure();
    }
}

DSLPtr createDSL_RDB()
{
   DSL_RDBPtr dsl = DSL_RDBPtr(new DSL_RDB());
   if(!dsl->init()) return DSL_RDBPtr();
   return DSL_RDBPtr(dsl);
}

}}
