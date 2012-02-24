/* dsl.cpp */
/**
 * Copyright - See the COPYRIGHT that is included with this distribution.
 * This code is distributed subject to a Software License Agreement found
 * in file LICENSE that is included with this distribution.
 */

#undef _POSIX_C_SOURCE
#undef _XOPEN_SOURCE
#include <Python.h>
#include <numpy/arrayobject.h>

#include <string>
#include <stdexcept>
#include <memory>
#include <vector>

#include <pv/pvIntrospect.h>
#include <pv/pvData.h>
#include <pv/dsl.h>
#include <pv/nt.h>

#include <pv/gatherV3Data.h>

namespace epics { namespace masar { 

using namespace epics::pvData;
using namespace epics::pvAccess;

class DSL_RDB :
    public DSL,
    public std::tr1::enable_shared_from_this<DSL_RDB>
{
public:
    POINTER_DEFINITIONS(DSL_RDB);
    DSL_RDB();
    virtual ~DSL_RDB();
    virtual void destroy();
    virtual PVStructure::shared_pointer request(
        String functionName,int num,String *names,String *values);
    bool init();
private:
    DSL_RDB::shared_pointer getPtrSelf()
    {
        return shared_from_this();
    }

    PyObject * prequest;
    PyObject * pgetchannames;
};

DSL_RDB::DSL_RDB()
    : prequest(0), pgetchannames(0)
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
    PyObject * module = PyImport_ImportModule("dslPY");
    if(module==0) {
        String message("dslPY");
        message += " does not exist or is not a python module";
        printf("DSL_RDB::init %s\n",message.c_str());
        return false;
    }
    PyObject *pclass = PyObject_GetAttrString(module, "DSL");
    if(pclass==0) {
        String message("class DSL");
        message += " does not exist";
        printf("DSL_RDB::init %s\n",message.c_str());
        Py_XDECREF(module);
        return false;
    }
    PyObject *pargs = Py_BuildValue("()");
    if (pargs == NULL) {
        Py_DECREF(pclass);
        printf("Can't build arguments list\n");
        return false;
    }
    PyObject *pinstance = PyEval_CallObject(pclass,pargs);
    Py_DECREF(pargs);
    if(pinstance==0) {
        String message("class DSL");
        message += " constructor failed";
        printf("DSL_RDB::init %s\n",message.c_str());
        Py_XDECREF(pclass);
        Py_XDECREF(module);
        return false;
    }
    prequest = PyObject_GetAttrString(pinstance, "request");
    if(prequest==0) {
        String message("DSL::request");
        message += " could not attach to method";
        printf("DSL_RDB::init %s\n",message.c_str());
        Py_XDECREF(pinstance);
        Py_XDECREF(pclass);
        Py_XDECREF(module);
        return false;
    }
    pgetchannames = PyObject_GetAttrString(pinstance, "retrieveChannelNames");
    if(pgetchannames==0) {
        String message("DSL::request");
        message += " could not attach to method";
        printf("DSL_RDB::init %s\n",message.c_str());
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

static PVStructure::shared_pointer retrieveSnapshot(PyObject * list)
{
    Py_ssize_t top_len = PyList_Size(list);
    if (top_len != 2) {
        THROW_BASE_EXCEPTION("Wrong format for returned data from dslPY when retrieving masar data.");
    }
    size_t strFieldLen = 3; // pv name, s_value, and alarm message are stored as string.

    FieldCreate *fieldCreate = getFieldCreate();

    PyObject * head_array = PyList_GetItem(list, 0); // get head array
    PyObject * head = PyList_GetItem(head_array, 1); // get label array
    Py_ssize_t tuple_size = PyTuple_Size(head);

    // create fields
    // set label for each field
    // ('pv name', 'string value', 'double value', 'long value', 'dbr type', 'isConnected',
    //  'secondsPastEpoch', 'nanoSeconds', 'timeStampTag', 'alarmSeverity', 'alarmStatus', 'alarmMessage'
    //  'is_array', 'array_value')
    FieldConstPtr fields[tuple_size];
    for (ssize_t i = 0; i < tuple_size; i ++){
        if (i == 0 || i == 1 || i == 11) { // pv_name: 0, string value: 1, alarm message: 11
            fields[i] = fieldCreate->createScalarArray(PyString_AsString(PyTuple_GetItem(head, i)), pvString);
        } else if (i == 2) { // double value: 2
            fields[i] = fieldCreate->createScalarArray(PyString_AsString(PyTuple_GetItem(head, i)), pvDouble);
        } else if(i!=13) {
            // long value: 3, dbr type: 4, secondsPastEpoch: 6, nanoSeconds: 7, timeStampTag: 8,
            // alarmSeverity: 9, alarmStatus: 10, is_array: 12
            fields[i] = fieldCreate->createScalarArray(PyString_AsString(PyTuple_GetItem(head, i)), pvLong);
        } else {
            // for array value operation
            int naf = 3;
            FieldConstPtrArray arrfields = new FieldConstPtr[naf];
            arrfields[0] = fieldCreate->createScalarArray("stringValue",pvString);
            arrfields[1] = fieldCreate->createScalarArray("doubleValue",pvDouble);
            arrfields[2] = fieldCreate->createScalarArray("intValue",pvInt);
            StructureConstPtr arrStructure = fieldCreate->createStructure(
                 "arrayValue",naf,arrfields);
            fields[i] = fieldCreate->createStructureArray(PyString_AsString(PyTuple_GetItem(head, i)), arrStructure);
        }
    }

    // create NTTable
    PVStructure::shared_pointer pvStructure = NTTable::create(
        false,true,true,tuple_size,fields);
    NTTable ntTable(pvStructure);

    PyObject * data_array = PyList_GetItem(list, 1); // get data array
    // data length in each field
    // (the first row is a description instead of real data)
    Py_ssize_t numberChannels = PyList_Size(data_array) - 1;

    // initilize PVStructureArray for waveform/array record
    PVStructureArray *pvarrayValue = static_cast<PVStructureArray *>(ntTable.getPVField(13));
    pvarrayValue->setCapacity(numberChannels);
    pvarrayValue->setCapacityMutable(false);
    StructureArrayData structdata;
    pvarrayValue->get(0,numberChannels,&structdata);
    PVStructure ** ppPVStructure = structdata.data;
    StructureConstPtr pstructure = pvarrayValue->getStructureArray()->getStructure();
    PVDataCreate *pvDataCreate = getPVDataCreate();
    for (int i=0; i<numberChannels; i++) {
        ppPVStructure[i] = pvDataCreate->createPVStructure(0,pstructure);
    }
    pvarrayValue->setLength(numberChannels);

    if (numberChannels > 0) {
        std::vector<std::vector<String> > pvNames (strFieldLen);
        for (size_t i = 0; i < pvNames.size(); i++){
            pvNames[i].resize(numberChannels);
        }
        std::vector<double> dVals(numberChannels);
        std::vector<std::vector<int64> > lVals(tuple_size-strFieldLen-1); //[dataLen];
        for(size_t i=0; i<lVals.size(); i++) {
            lVals[i].resize(numberChannels);
        }

        // Get values for each fields from list
        PyObject * sublist;

        pvarrayValue->get(0,numberChannels,&structdata);

        for (int index = 0; index < numberChannels; index++ ){
            sublist = PyList_GetItem(data_array, index+1);
            for (int i = 0; i < tuple_size-1; i ++) { // tuple_size -1: do not parse waveform tuple directly.
                PyObject * temp = PyTuple_GetItem(sublist, i);
                // ('pv name', 'string value', 'double value', 'long value', 'dbr type', 'isConnected',
                //  'secondsPastEpoch', 'nanoSeconds', 'timeStampTag', 'alarmSeverity', 'alarmStatus', 'alarmMessage'
                //  'is_array', 'array_value')
                if (i == 0 ) { // pv_name: 0
                    // PyString_Check for type check?
                    if (PyString_AsString (temp) == NULL) {
                        pvNames[0][index] = "";
                    } else {
                        pvNames[0][index] = PyString_AsString (temp);
                    }
                } else if (i == 1 ) { // string value: 1
                    // PyString_Check for type check?
                    if (PyString_AsString (temp) == NULL) {
                        pvNames[1][index] = "";
                    } else {
                        pvNames[1][index] = PyString_AsString (temp);
                    }
                } else if (i == 11 ) { // alarm message: 11
                    // PyString_Check for type check?
                    if (PyString_AsString (temp) == NULL) {
                        pvNames[2][index] = "";
                    } else {
                        pvNames[2][index] = PyString_AsString (temp);
                    }
                } else if (i == 2) { // double value: 2
                    // PyDouble_Check for type check?
                    dVals[index] = PyFloat_AsDouble (temp);
                } else if (i!=13){
                    // long value: 3, dbr type: 4, isConnected: 5, secondsPastEpoch: 6, nanoSeconds: 7,
                    // timeStampTag: 8, alarmSeverity: 9, alarmStatus: 10, is_array: 12
                    // PyLong_Check for type check?
                    if (i == 12) {
                        lVals[i-4][index] = PyLong_AsLongLong (temp);
                    } else {
                        lVals[i-3][index] = PyLong_AsLongLong (temp);
                    }
                }
            }

            PVStructure * pvStructure = structdata.data[index];
            if (lVals[8][index] == 1) {
                // EPICS DBR type
                //#define    DBF_STRING  0
                //#define    DBF_INT     1
                //#define    DBF_SHORT   1
                //#define    DBF_FLOAT   2
                //#define    DBF_ENUM    3
                //#define    DBF_CHAR    4
                //#define    DBF_LONG    5
                //#define    DBF_DOUBLE  6
                // check EPICS dbr type
                PyObject * arrayValueList = PyTuple_GetItem(sublist, 13);
                PVFieldPtrArray pvfields = pvStructure->getPVFields();

                if (lVals[1][index] == 1 || lVals[1][index] == 4 || lVals[1][index] == 5){
                    // integer type
                    IntArrayData intdata;
                    PVIntArray *pvintarray = static_cast<PVIntArray *>(pvfields[2]);
                    if (PyList_Check(arrayValueList)) {
                        size_t array_len = (size_t)PyList_Size(arrayValueList);
                        pvintarray->setLength(array_len);
                        pvintarray->get(0,array_len,&intdata);
                        int32 * pvalue = intdata.data;
                        for (size_t array_index = 0; array_index < array_len; array_index++){
                            pvalue[array_index] = PyLong_AsLong(PyList_GetItem(arrayValueList, array_index));
                        }
                    } else if (PyTuple_Check(arrayValueList)) {
                        size_t array_len = (size_t)PyTuple_Size(arrayValueList);
                        pvintarray->setLength(array_len);
                        pvintarray->get(0,array_len,&intdata);
                        int32 * pvalue = intdata.data;
                        for (size_t array_index = 0; array_index < array_len; array_index++){
                            pvalue[array_index] = PyLong_AsLong(PyTuple_GetItem(arrayValueList, array_index));
                        }
                    }
                } else if (lVals[1][index] == 0) {
                    // string
                    StringArrayData stringdata;
                    PVStringArray *pvstringarray = static_cast<PVStringArray *>(pvfields[0]);
                    if (PyList_Check(arrayValueList)) {
                        size_t array_len = (size_t )PyList_Size(arrayValueList);
                        pvstringarray->setLength(array_len);
                        pvstringarray->get(0,array_len,&stringdata);
                        String * pvalue = stringdata.data;
                        for (size_t array_index = 0; array_index < array_len; array_index++){
                            pvalue[array_index] = PyString_AsString(PyList_GetItem(arrayValueList, array_index));
                        }
                    } else if (PyTuple_Check(arrayValueList)) {
                        size_t array_len = (size_t )PyTuple_Size(arrayValueList);
                        pvstringarray->setLength(array_len);
                        pvstringarray->get(0,array_len,&stringdata);
                        String * pvalue = stringdata.data;
                        for (size_t array_index = 0; array_index < array_len; array_index++){
                            pvalue[array_index] = PyString_AsString(PyTuple_GetItem(arrayValueList, array_index));
                        }
                    }
                } else if (lVals[1][index] == 2 || lVals[1][index] == 6) {
                    // float or double
                    DoubleArrayData doubledata;
                    PVDoubleArray *pvdoublearray = static_cast<PVDoubleArray *>(pvfields[1]);
                    if (PyList_Check(arrayValueList)) {
                        size_t array_len = (size_t )PyList_Size(arrayValueList);
                        pvdoublearray->setLength(array_len);
                        pvdoublearray->get(0,array_len,&doubledata);
                        double * pvalue = doubledata.data;
                        for (size_t array_index = 0; array_index < array_len; array_index++){
                            pvalue[array_index] = PyFloat_AsDouble(PyList_GetItem(arrayValueList, array_index));
                        }
                    } else if (PyTuple_Check(arrayValueList)) {
                        size_t array_len = (size_t )PyTuple_Size(arrayValueList);
                        pvdoublearray->setLength(array_len);
                        pvdoublearray->get(0,array_len,&doubledata);
                        double * pvalue = doubledata.data;
                        for (size_t array_index = 0; array_index < array_len; array_index++){
                            pvalue[array_index] = PyFloat_AsDouble(PyTuple_GetItem(arrayValueList, array_index));
                        }
                    }
                }
            }
        }

        // set value to each field
        PVStringArray *pvStr;
        PVDoubleArray * pvDVal;
        PVLongArray * pvLVal;
        for (int i = 0; i < tuple_size; i ++) {
            if (i == 0 ) { // pv_name: 0
                pvStr = static_cast<PVStringArray *>(ntTable.getPVField(i));
                pvStr -> put (0, numberChannels, &(pvNames[0])[0], 0);
            } else if (i == 1) { // string value: 1
                pvStr = static_cast<PVStringArray *>(ntTable.getPVField(i));
                pvStr -> put (0, numberChannels, &(pvNames[1])[0], 0);
            } else if (i == 11 ) { // alarm message: 11
                pvStr = static_cast<PVStringArray *>(ntTable.getPVField(11));
                pvStr -> put (0, numberChannels, &(pvNames[2])[0], 0);
            }else if (i == 2) { // double value: 2
                pvDVal = static_cast<PVDoubleArray *>(ntTable.getPVField(i));
                pvDVal -> put (0, numberChannels, &dVals[0], 0);
            } else if (i!=13){
                // long value: 3, dbr type: 4, isConnected: 5, secondsPastEpoch: 6, nanoSeconds: 7,
                // timeStampTag: 8, alarmSeverity: 9, alarmStatus: 10, is_array: 12
                pvLVal = static_cast<PVLongArray *>(ntTable.getPVField(i));
                if (i == 12)
                    pvLVal -> put (0, numberChannels, &(lVals[i-4])[0], 0);
                else
                    pvLVal -> put (0, numberChannels, &(lVals[i-3])[0], 0);
            } else {
            }
        }
    }

    // set label strings
    std::vector<String> labelVals (tuple_size);
    for (int i = 0; i < tuple_size; i ++) {
        labelVals[i] = fields[i]->getFieldName();
    }
    PVStringArray *label = ntTable.getLabel();
    label->put(0,tuple_size,&(labelVals)[0],0);

    // set time stamp
    PVTimeStamp pvTimeStamp;
    ntTable.attachTimeStamp(pvTimeStamp);
    TimeStamp timeStamp;
    timeStamp.getCurrent();
    timeStamp.setUserTag(0);
    pvTimeStamp.set(timeStamp);

    return pvStructure;
}

static PVStructure::shared_pointer retrieveServiceConfigEvents(PyObject * list, long numeric)
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
    int fieldLen = list_len - 1; // length - label header

    FieldCreate *fieldCreate = getFieldCreate();

    // create fields
    // set label for each field
    FieldConstPtr fields[tuple_size];
    for (int i = 0; i < numeric; i ++){
        fields[i] = fieldCreate->createScalarArray(PyString_AsString(PyTuple_GetItem(labelList, i)), pvLong);
    }
    for (int i = numeric; i < tuple_size; i ++){
        fields[i] = fieldCreate->createScalarArray(PyString_AsString(PyTuple_GetItem(labelList, i)), pvString);
    }

    // create NTTable
    PVStructure::shared_pointer pvStructure = NTTable::create(
        false,true,true,tuple_size,fields);
    NTTable ntTable(pvStructure);

    std::vector<std::vector<int64> > scIdVals(numeric);
    for(size_t i=0; i<scIdVals.size(); i++) {
        scIdVals[i].resize(list_len-1);
    }

    std::vector<std::vector<String> > vals (tuple_size-numeric);
    for (size_t i = 0; i < vals.size(); i++){
        vals[i].resize(fieldLen);
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
    PVLongArray *pvSCIds;
    for (int i = 0; i < numeric; i ++) {
        pvSCIds = static_cast<PVLongArray *>(ntTable.getPVField(i));
        pvSCIds -> put (0, fieldLen, &(scIdVals[i])[0], 0);
    }
    // set value to each string field
    PVStringArray * pvStrVal;
    for (int i = numeric; i < tuple_size; i ++) {
        pvStrVal = static_cast<PVStringArray *>(ntTable.getPVField(i));
        pvStrVal -> put (0, fieldLen, &(vals[i-numeric])[0], 0);
    }

    // set label strings
    std::vector<String> labelVals(tuple_size);
    for (int i = 0; i < tuple_size; i ++) {
        labelVals[i] = fields[i]->getFieldName();
    }
    PVStringArray *label = ntTable.getLabel();
    label->put(0,tuple_size, &(labelVals)[0],0);

    PVTimeStamp pvTimeStamp;
    ntTable.attachTimeStamp(pvTimeStamp);
    TimeStamp timeStamp;
    timeStamp.getCurrent();
    timeStamp.setUserTag(0);
    pvTimeStamp.set(timeStamp);

    return pvStructure;
}

static PVStructure::shared_pointer saveSnapshot(PyObject * list, PVStructure::shared_pointer data, String message)
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
        printf("updateSnapshotEvent return: not a tuple, nor list\n");
        THROW_BASE_EXCEPTION("Wrong format for returned data from dslPY.");
    }

    if (eid == -1) {
        FieldCreate *fieldCreate = getFieldCreate();

        FieldConstPtr fields = fieldCreate->createScalarArray("status",pvBoolean);
        PVStructure::shared_pointer pvStructure = NTTable::create(
            false,true,true,1, &fields);

        NTTable ntTable(pvStructure);

        PVBooleanArray * pvBoolVal = static_cast<PVBooleanArray *>(ntTable.getPVField(0));
        bool temp [] = {false};
        pvBoolVal -> put (0, 1, temp, 0);

        // set label strings
        String labelVals  = fields->getFieldName();
        PVStringArray *label = ntTable.getLabel();
        label->put(0,1,&labelVals,0);

        // Set alarm and severity
        PVAlarm pvAlarm;
        Alarm alarm;
        ntTable.attachAlarm(pvAlarm);

        alarm.setMessage("Machine preview failed. " + message);
        alarm.setSeverity(majorAlarm);
        alarm.setStatus(clientStatus);
        pvAlarm.set(alarm);

        // set time stamp
        PVTimeStamp pvTimeStamp;
        ntTable.attachTimeStamp(pvTimeStamp);
        TimeStamp timeStamp;
        timeStamp.getCurrent();
        timeStamp.setUserTag(0);
        // bool result = pvTimeStamp.set(timeStamp);
        pvTimeStamp.set(timeStamp);

        return pvStructure;
    } else {
        NTTable ntTable(data);

        // Set alarm and severity
        PVAlarm pvAlarm;
        Alarm alarm;
        ntTable.attachAlarm(pvAlarm);

        alarm.setMessage("Machine preview Successed. " + message);
        alarm.setSeverity(majorAlarm);
        alarm.setStatus(clientStatus);
        pvAlarm.set(alarm);

        // set time stamp
        PVTimeStamp pvTimeStamp;
        ntTable.attachTimeStamp(pvTimeStamp);
        TimeStamp timeStamp;
        timeStamp.getCurrent();
        timeStamp.setUserTag(eid);
        // bool result = pvTimeStamp.set(timeStamp);
        pvTimeStamp.set(timeStamp);

        return data;
    }
}


static PVStructure::shared_pointer updateSnapshotEvent(PyObject * list)
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
        printf("updateSnapshotEvent return: not a tuple, nor list\n");
        THROW_BASE_EXCEPTION("updateSnapshotEvent return: not a tuple, nor list.");
    }

    FieldCreate *fieldCreate = getFieldCreate();

    FieldConstPtr fields = fieldCreate->createScalarArray("status",pvBoolean);
    PVStructure::shared_pointer pvStructure = NTTable::create(
            false,true,true,1, &fields);

    NTTable ntTable(pvStructure);

    PVBooleanArray * pvBoolVal = static_cast<PVBooleanArray *>(ntTable.getPVField(0));
    bool temp = false;
    if (eid >= 0) {
        temp = true;
        pvBoolVal -> put (0, 1, &temp, 0);
    } else {
        pvBoolVal -> put (0, 1, &temp, 0);
    }

    // set label strings
    String labelVals  = fields->getFieldName();
    PVStringArray *label = ntTable.getLabel();
    label->put(0,1,&labelVals,0);

    // Set alarm and severity
    PVAlarm pvAlarm;
    Alarm alarm;
    ntTable.attachAlarm(pvAlarm);

    if (eid >= 0) {
        alarm.setMessage("Falied to save snapshot preview.");
    } else {
        alarm.setMessage("Success to save snapshot preview.");
    }
    alarm.setSeverity(majorAlarm);
    alarm.setStatus(clientStatus);
    pvAlarm.set(alarm);

    // set time stamp
    PVTimeStamp pvTimeStamp;
    ntTable.attachTimeStamp(pvTimeStamp);
    TimeStamp timeStamp;
    timeStamp.getCurrent();
    timeStamp.setUserTag(0);
    // bool result = pvTimeStamp.set(timeStamp);
    pvTimeStamp.set(timeStamp);

    return pvStructure;
}

static PVStructure::shared_pointer createResult(
    PyObject *result, String functionName)
{
    PVStructure::shared_pointer pvStructure;
    pvStructure.reset();
    {
        PyObject *list = 0;
        if(!PyArg_ParseTuple(result,"O!:dslPY", &PyList_Type,&list))
        {
            printf("Wrong format for returned data from dslPY.\n");
            //THROW_BASE_EXCEPTION("Wrong format for returned data from dslPY.");
            return pvStructure;
        }

        if (functionName.compare("retrieveSnapshot")==0) {
    //    if (functionName == "retrieveSnapshot") {
            pvStructure = retrieveSnapshot(list);
        } else if (functionName.compare("retrieveServiceEvents")==0) {
    //        if (functionName == "retrieveServiceEvents") {
            pvStructure = retrieveServiceConfigEvents(list, 2);
        } else if (functionName.compare("retrieveServiceConfigs")==0) {
    //        if ( functionName == "retrieveServiceConfigs") {
            pvStructure = retrieveServiceConfigEvents(list, 1);
        } else if (functionName.compare("retrieveServiceConfigProps")==0) {
            pvStructure = retrieveServiceConfigEvents(list, 2);
        } else if (functionName.compare("updateSnapshotEvent")==0) {
            pvStructure = updateSnapshotEvent(list);
        }
    }
    return pvStructure;
}

static PVStructure::shared_pointer getLiveMachine(
        String channelName [], int numberChannels, String * message)
{
    GatherV3Data::shared_pointer gather = GatherV3Data::shared_pointer(
        new GatherV3Data(channelName,numberChannels));

    // wait one second, which is a magic number for now.
    // The waiting time might be removed later after stability test.
    bool result = gather->connect(1.0);
    * message = gather->getMessage();
    if(!result) {
        printf("connect failed\n%s\n",gather->getMessage().c_str());
    }
    if((*message).length() == 0) {
        *message = "All channels are connected.";
    }
    result = gather->get();

    PVStructure::shared_pointer nttable = gather->getNTTable();

    return nttable;
}

PVStructure::shared_pointer DSL_RDB::request(
    String functionName,int num,String *names,String *values)
{
    if (functionName.compare("getLiveMachine")==0) {
        String message;
        PVStructure::shared_pointer data = getLiveMachine(values, num, &message);

        NTTable ntTable(data);

        // Set alarm and severity
        PVAlarm pvAlarm;
        Alarm alarm;
        ntTable.attachAlarm(pvAlarm);

        alarm.setMessage("Live machine: " + message);
        alarm.setSeverity(majorAlarm);
        alarm.setStatus(clientStatus);
        pvAlarm.set(alarm);

        // set time stamp
        PVTimeStamp pvTimeStamp;
        ntTable.attachTimeStamp(pvTimeStamp);
        TimeStamp timeStamp;
        timeStamp.getCurrent();
        timeStamp.setUserTag(0);
        // bool result = pvTimeStamp.set(timeStamp);
        pvTimeStamp.set(timeStamp);

        return data;
    }

    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject *pyDict = PyDict_New();
    for (int i = 0; i < num; i ++) {
        PyObject *pyValue = Py_BuildValue("s",values[i].c_str());
        PyDict_SetItemString(pyDict,names[i].c_str(),pyValue);
    }
    PyObject *pyValue = Py_BuildValue("s",functionName.c_str());
    PyDict_SetItemString(pyDict,"function",pyValue);
    PVStructure::shared_pointer pvReturn;
    if (functionName.compare("saveSnapshot")==0) {
        // A tuple is needed to pass to Python as parameter.
        PyObject * pyTuple = PyTuple_New(1);
        // put dictionary into the tuple
        PyTuple_SetItem(pyTuple, 0, pyDict);
        PyObject *pchannelnames = PyEval_CallObject(pgetchannames,pyTuple);
        Py_ssize_t list_len = PyList_Size(pchannelnames);

        String channames[list_len];
        PyObject * name;
        for (ssize_t i = 0; i < list_len; i ++) {
            name = PyList_GetItem(pchannelnames, i);
            channames[i] = PyString_AsString(name);
        }
        Py_DECREF(pchannelnames);
        String message;
        PVStructure::shared_pointer data = getLiveMachine(channames, list_len, &message);

        // create a tuple is needed to pass to Python as parameter.
        PyObject * pdata = PyCapsule_New(&data,"pvStructure",0);
        PyObject * pyTuple2 = PyTuple_New(2);

        // first value is the data from live machine
        PyTuple_SetItem(pyTuple2, 0, pdata);
        // second value is the dictionary
        PyTuple_SetItem(pyTuple2, 1, pyDict);
        PyObject *result = PyEval_CallObject(prequest,pyTuple2);
        pvReturn = saveSnapshot(result, data, message);
        Py_DECREF(result);
    } else {
        // A tuple is needed to pass to Python as parameter.
        PyObject * pyTuple = PyTuple_New(1);
        // put dictionary into the tuple
        PyTuple_SetItem(pyTuple, 0, pyDict);

        PyObject *result = PyEval_CallObject(prequest,pyTuple);
        pvReturn = createResult(result,functionName);
        Py_DECREF(result);
    }

    PyGILState_Release(gstate);
    return pvReturn;
}

DSL::shared_pointer createDSL_RDB()
{
   DSL_RDB *dsl = new DSL_RDB();
   if(!dsl->init()) {
        delete dsl;
        return DSL_RDB::shared_pointer();
        
   }
   return DSL_RDB::shared_pointer(dsl);
}

}}
