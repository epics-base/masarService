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
#include <pv/pvIntrospect.h>
#include <pv/pvData.h>
#include <pv/dsl.h>
#include <pv/nt.h>


namespace epics { namespace masar { 

using namespace epics::pvData;

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
};

DSL_RDB::DSL_RDB()
: prequest(0)
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
        Py_XDECREF(pinstance);
        Py_XDECREF(pclass);
        Py_XDECREF(module);
    PyGILState_Release(gstate);
    return true;
}

void DSL_RDB::destroy() {}

static PVStructure::shared_pointer retrieveMasar(PyObject * list)
{
    Py_ssize_t top_len = PyList_Size(list);
    if (top_len != 2) {
        THROW_BASE_EXCEPTION("Wrong format for returned data from dslPY when retrieving masar data.");
    }
    size_t strFieldLen = 2; // pv name and s_value are stored as string.

    FieldCreate *fieldCreate = getFieldCreate();

    PyObject * head_array = PyList_GetItem(list, 0); // get head array
    PyObject * head = PyList_GetItem(head_array, 1); // get label array
    Py_ssize_t tuple_size = PyTuple_Size(head);

    // create fields
    // set label for each field
    FieldConstPtr fields[tuple_size];
    for (size_t i = 0; i < tuple_size; i ++){
        if (i == 0 || i == 2) { // pv_name: 0, string value: 2
            fields[i] = fieldCreate->createScalarArray(PyString_AsString(PyTuple_GetItem(head, i)), pvString);
        } else if (i == 4) { // double value: 4
            fields[i] = fieldCreate->createScalarArray(PyString_AsString(PyTuple_GetItem(head, i)), pvDouble);
        } else { // dbr_type: 1, i_value: 3, status: 5, severity: 6, ioc_timestamp: 7, ioc_timestamp_nano: 8
            fields[i] = fieldCreate->createScalarArray(PyString_AsString(PyTuple_GetItem(head, i)), pvLong);
        }
    }

    // create NTTable
    PVStructure::shared_pointer pvStructure = NTTable::create(
        false,true,true,tuple_size,fields);
    NTTable ntTable(pvStructure);

    PyObject * data_array = PyList_GetItem(list, 1); // get data array
    Py_ssize_t dataLen = PyList_Size(data_array) - 1; // data length in each field

    if (dataLen > 0) {
        String pvNames [strFieldLen][dataLen];
        double dVals [dataLen];
        long long lVals [tuple_size-strFieldLen-1][dataLen];

        // Get values for each fields from list
        PyObject * sublist;
        for (int index = 0; index < dataLen; index++ ){
            sublist = PyList_GetItem(data_array, index+1);
            for (int i = 0; i < tuple_size; i ++) {
                PyObject * temp = PyTuple_GetItem(sublist, i);
                // (pv_name, dbr_type, s_value, i_value, d_value, status, severity, ioc_timestamp, ioc_timestamp_nano)
                if (i == 0 ) { // pv_name: 0
                    if (PyString_AsString (temp) == NULL) {
                        pvNames[0][index] = "";
                    } else {
                        pvNames[0][index] = PyString_AsString (temp);
                    }
                } else if (i == 2) { // string value: 2
                    if (PyString_AsString (temp) == NULL) {
                        pvNames[1][index] = "";
                    } else {
                        pvNames[1][index] = PyString_AsString (temp);
                    }
                } else if (i == 4) { // double value: 4
                    dVals[index] = PyFloat_AsDouble (temp);
                } else {  // dbr_type: 1, i_value: 3, status: 5, severity: 6, ioc_timestamp: 7, ioc_timestamp_nano: 8
                    if (i == 1) {
                        lVals[0][index] = PyLong_AsLong (temp);
                    } else if (i == 3) {
                        lVals[1][index] = PyLong_AsLong (temp);
                    } else {
                        lVals[i-3][index] = PyLong_AsLong (temp);
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
                // pvName
                pvStr = static_cast<PVStringArray *>(ntTable.getPVField(i));
                pvStr -> put (0, dataLen, pvNames[0], 0);
            } else if (i == 2) { // string value: 2
                // s_value
                pvStr = static_cast<PVStringArray *>(ntTable.getPVField(i));
                pvStr -> put (0, dataLen, pvNames[1], 0);
            } else if (i == 4) { // double value: 4
                // d_double
                pvDVal = static_cast<PVDoubleArray *>(ntTable.getPVField(i));
                pvDVal -> put (0, dataLen, dVals, 0);
            } else {  // dbr_type: 1, i_value: 3, status: 5, severity: 6, ioc_timestamp: 7, ioc_timestamp_nano: 8
                pvLVal = static_cast<PVLongArray *>(ntTable.getPVField(i));
                if (i == 1) {
                    pvLVal -> put (0, dataLen, lVals[0], 0);
                } else if (i == 3) {
                    pvLVal -> put (0, dataLen, lVals[1], 0);
                } else {
                    pvLVal -> put (0, dataLen, lVals[i-3], 0);
                }
            }
        }
    }

    // set label strings
    String labelVals [tuple_size];
    for (int i = 0; i < tuple_size; i ++) {
        labelVals[i] = fields[i]->getFieldName();
    }
    PVStringArray *label = ntTable.getLabel();
    label->put(0,tuple_size,labelVals,0);

//    PVAlarm pvAlarm;
//    Alarm alarm;
//    PVStructurePtr palarms[n];
//    for(int i=0; i<n; i++) {
//        palarms[i] = pvntField->createAlarm(0);
//        pvAlarm.attach(palarms[i]);
//        alarm.setMessage("test");
//        alarm.setSeverity(majorAlarm);
//        alarm.setStatus(clientStatus);
//        pvAlarm.set(alarm);
//    }
//    pvAlarms->put(0,n,palarms,0);
//    ntTable.attachAlarm(pvAlarm);
//    alarm.setMessage("test alarm");
//    alarm.setSeverity(majorAlarm);
//    alarm.setStatus(clientStatus);
//    pvAlarm.set(alarm);

    // set time stamp
    PVTimeStamp pvTimeStamp;
    ntTable.attachTimeStamp(pvTimeStamp);
    TimeStamp timeStamp;
    timeStamp.getCurrent();
    timeStamp.setUserTag(0);
//    bool result = pvTimeStamp.set(timeStamp);
    pvTimeStamp.set(timeStamp);

    return pvStructure;
}

//static PVStructure::shared_pointer retrieveServiceEvents(PyObject * list)
//{
//}
//static PVStructure::shared_pointer retrieveServiceConfigProps(
//        PyObject * list)
//{
//}

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
    //    NTField *ntField = NTField::get();
    //    PVNTField *pvntField = PVNTField::get();

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

    long long scIdVals [numeric][list_len-1];
    String vals [tuple_size-numeric][fieldLen];

    // Get values for each fields from list
    PyObject * sublist;
    for (int index = 1; index < list_len; index++ ){
        sublist = PyList_GetItem(list, index);
        for (int i = 0; i < tuple_size; i ++) {
            PyObject * temp = PyTuple_GetItem(sublist, i);
            if (i < numeric){
                if (PyLong_AsLong(temp) == NULL) {
                    scIdVals[i][index-1] = -1;
                } else {
                    scIdVals[i][index-1] = PyLong_AsLong(temp);
                }
            } else {
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
        pvSCIds -> put (0, fieldLen, scIdVals[i], 0);
    }
    // set value to each string field
    PVStringArray * pvStrVal;
    for (int i = numeric; i < tuple_size; i ++) {
        pvStrVal = static_cast<PVStringArray *>(ntTable.getPVField(i));
        pvStrVal -> put (0, fieldLen, vals[i-numeric], 0);
    }

    // set label strings
    String labelVals [tuple_size];
    for (int i = 0; i < tuple_size; i ++) {
        labelVals[i] = fields[i]->getFieldName();
    }
    PVStringArray *label = ntTable.getLabel();
    label->put(0,tuple_size,labelVals,0);

//    Set alarm and severity
//    PVStructureArray *pvAlarms
//        = static_cast<PVStructureArray *>(ntTable.getPVField(1));
//    PVAlarm pvAlarm;
//    Alarm alarm;
//    PVStructurePtr palarms[n];
//    for(int i=0; i<n; i++) {
//        palarms[i] = pvntField->createAlarm(0);
//        pvAlarm.attach(palarms[i]);
//        alarm.setMessage("test");
//        alarm.setSeverity(majorAlarm);
//        alarm.setStatus(clientStatus);
//        pvAlarm.set(alarm);
//    }
//    pvAlarms->put(0,n,palarms,0);
//    ntTable.attachAlarm(pvAlarm);
//    alarm.setMessage("test alarm");
//    alarm.setSeverity(majorAlarm);
//    alarm.setStatus(clientStatus);
//    pvAlarm.set(alarm);
    PVTimeStamp pvTimeStamp;
    ntTable.attachTimeStamp(pvTimeStamp);
    TimeStamp timeStamp;
    timeStamp.getCurrent();
    timeStamp.setUserTag(0);
//    bool result = pvTimeStamp.set(timeStamp);
    pvTimeStamp.set(timeStamp);

    return pvStructure;
}

static PVStructure::shared_pointer saveMasar(PyObject * list)
{
    FieldCreate *fieldCreate = getFieldCreate();
    NTField *ntField = NTField::get();
    PVNTField *pvntField = PVNTField::get();
//String builder;
//GUIBAO MUST CREATE fields based on result and functionName.
    int n = 2;
    FieldConstPtr fields[2];
    fields[0] = fieldCreate->createScalarArray("position",pvDouble);
    fields[1] = ntField->createAlarmArray("alarms");
    PVStructure::shared_pointer pvStructure = NTTable::create(
        false,true,true,n,fields);

    return pvStructure;
}

static PVStructure::shared_pointer createResult(
    PyObject *result, String functionName)
{
    PyObject *list = 0;
    if(!PyArg_ParseTuple(result,"O!:dslPY", &PyList_Type,&list))
    {
        printf("exception in createResult\n");
        THROW_BASE_EXCEPTION("Wrong format for returned data from dslPY.");
    }

    PVStructure::shared_pointer pvStructure;
    pvStructure.reset();

    if (functionName == "retrieveMasar") {
        pvStructure = retrieveMasar(list);
    } else if  (functionName == "retrieveServiceEvents") {
        pvStructure = retrieveServiceConfigEvents(list, 2);
    } else if ( functionName == "retrieveServiceConfigs") {
        pvStructure = retrieveServiceConfigEvents(list, 1);
    } else if ( functionName == "retrieveServiceConfigProps") {
        pvStructure = retrieveServiceConfigEvents(list, 2);
    } else {
        pvStructure = saveMasar(list);
    }
    return pvStructure;
}

PVStructure::shared_pointer DSL_RDB::request(
    String functionName,int num,String *names,String *values)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
        PyObject *pyDict = PyDict_New();
        for (int i = 0; i < num; i ++) {
            PyObject *pyValue = Py_BuildValue("s",values[i].c_str());
            PyDict_SetItemString(pyDict,names[i].c_str(),pyValue);
        }
        PyObject *pyValue = Py_BuildValue("s",functionName.c_str());
        PyDict_SetItemString(pyDict,"function",pyValue);

        // A tuple is needed to pass to Python as parameter.
        PyObject * pyTuple = PyTuple_New(1);
        PyTuple_SetItem(pyTuple, 0, pyDict);
        PyObject *result = PyEval_CallObject(prequest,pyTuple);

        PVStructure::shared_pointer pvReturn =
            createResult(result,functionName);
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
