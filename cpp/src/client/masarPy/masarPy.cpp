/* gatherDataPy.cpp */
/*
 *Copyright - See the COPYRIGHT that is included with this distribution.
 *This code is distributed subject to a Software License Agreement found
 *in file LICENSE that is included with this distribution.
 */
/* Author:  Marty Kraimer Date: 2011.11 */

#include "gatherDataPy.h"

namespace epics { namespace masar {

using namespace epics::pvData;
using namespace epics::pvAccess;

GatherDataPy::GatherDataPy(GatherData::shared_pointer gatherData)
: gatherData(gatherData),
  pyTrue(0),
  pyFalse(0),
  pySev0(0),
  pySev1(0),
  pySev2(0),
  pySev3(0)
{
    pyTrue = Py_BuildValue("b",1);
    pyFalse = Py_BuildValue("b",0);
    pySev0 = Py_BuildValue("i",0);
    pySev1 = Py_BuildValue("i",1);
    pySev2 = Py_BuildValue("i",2);
    pySev3 = Py_BuildValue("i",3);
}

GatherDataPy::~GatherDataPy()
{
    Py_DECREF(pySev3);
    Py_DECREF(pySev2);
    Py_DECREF(pySev1);
    Py_DECREF(pySev0);
    Py_DECREF(pyFalse);
    Py_DECREF(pyTrue);
    gatherData.reset();
}

PyObject *GatherDataPy::getAlarm(PyObject *pyAlarm)
{
    Alarm alarm = gatherData->getAlarm();
    String message = alarm.getMessage();
    AlarmSeverity alarmSeverity = alarm.getSeverity();
    char *methodName0 = const_cast<char *>("setMessage");
    char *format0 = const_cast<char *>("s");
    char *mess = const_cast<char *>(message.c_str());
    PyObject * result =
        PyObject_CallMethod(pyAlarm,methodName0,format0,mess);
    if(result==NULL) {
        throw std::logic_error("GatherDataPy::getAlarm PyObject_CallMethod");
    }
    Py_DECREF(result);
    char *methodName1 = const_cast<char *>("setSeverity");
    char *format1 = const_cast<char *>("h");
    result =
        PyObject_CallMethod(pyAlarm,methodName1,format1,(short)alarmSeverity);
    if(result==NULL) {
        throw std::logic_error("GatherDataPy::getAlarm PyObject_CallMethod");
    }
    Py_DECREF(result);
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *GatherDataPy::getTimeStamp(PyObject *pyTimeStamp)
{
    TimeStamp timeStamp = gatherData->getTimeStamp();
    int64 secs = timeStamp.getSecondsPastEpoch();
    int32 nano = timeStamp.getNanoSeconds();
    char *methodName = const_cast<char *>("put");
    char *format = const_cast<char *>("Ll");
    PyObject * result =
        PyObject_CallMethod(pyTimeStamp,methodName,format,secs,nano);
    if(result==NULL) {
        throw std::logic_error("GatherDataPy::getTimeStamp PyObject_CallMethod");
    }
    Py_DECREF(result);
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *GatherDataPy::getNumberChannels()
{
    return  Py_BuildValue("i",gatherData->getNumberChannels());
}

PyObject *GatherDataPy::anyBad()
{
    if(gatherData->anyBad()) {
        Py_INCREF(pyTrue);
        return pyTrue;
    }
    Py_INCREF(pyFalse);
    return pyFalse;
}

PyObject *GatherDataPy::isBad(int index)
{
    bool isBad = gatherData->isBad(index);
    if(isBad) {
        Py_INCREF(pyTrue);
        return pyTrue;
    }
    Py_INCREF(pyFalse);
    return pyFalse;
}

PyObject *GatherDataPy::badChange()
{
    if(gatherData->badChange()) {
        Py_INCREF(pyTrue);
        return pyTrue;
    }
    Py_INCREF(pyFalse);
    return pyFalse;
}

PyObject *GatherDataPy::allConnected()
{
    if(gatherData->allConnected()) {
        Py_INCREF(pyTrue);
        return pyTrue;
    }
    Py_INCREF(pyFalse);
    return pyFalse;
}

PyObject *GatherDataPy::isConnected(int index)
{
    bool isConnected = gatherData->isConnected(index);
    if(isConnected) {
        Py_INCREF(pyTrue);
        return pyTrue;
    }
    Py_INCREF(pyFalse);
    return pyFalse;
}

PyObject *GatherDataPy::connectionChange()
{
    if(gatherData->connectionChange()) {
        Py_INCREF(pyTrue);
        return pyTrue;
    }
    Py_INCREF(pyFalse);
    return pyFalse;
}

PyObject *GatherDataPy::severityChange()
{
    if(gatherData->severityChange()) {
        Py_INCREF(pyTrue);
        return pyTrue;
    }
    Py_INCREF(pyFalse);
    return pyFalse;
}

PyObject *GatherDataPy::getSeverity(int index)
{
    int severity = gatherData->getSeverity(index);
    switch(severity) {
    case 0: Py_INCREF(pySev0); return pySev0;
    case 1: Py_INCREF(pySev1); return pySev1;
    case 2: Py_INCREF(pySev2); return pySev2;
    case 3: Py_INCREF(pySev3); return pySev3;
    default:
        throw std::logic_error("GatherDataPy::getSeverity");
    }
}

GatherDataScalarPy::GatherDataScalarPy(
    GatherDataScalar::shared_pointer gatherDataScalar)
: GatherDataPy(gatherDataScalar),
  gatherDataScalar(gatherDataScalar),
  value(0)
{
    int length = gatherData->getNumberChannels();
    double *from = gatherDataScalar->getValue();
    int nd = 1;
    npy_intp dims[nd];
    dims[0] = length;
    value = PyArray_SimpleNewFromData(nd,dims,NPY_DOUBLE,from);
    if(value==0) {
        throw std::logic_error("GatherDataScalarPy PyArray_SimpleNew failed\n");
    }
}

GatherDataScalarPy::~GatherDataScalarPy()
{
    Py_DECREF(value);
}

PyObject *GatherDataScalarPy::getValue()
{
    void *pdata = PyArray_DATA(value);
    npy_intp *dims = PyArray_DIMS(value);
    int length = gatherData->getNumberChannels();
    double *from = gatherDataScalar->getValue();
    if(pdata!=from) {
        Py_DECREF(value);
        int nd = 1;
        npy_intp dims[nd];
        dims[0] = length;
        value = PyArray_SimpleNewFromData(nd,dims,NPY_DOUBLE,from);
        if(value==0) {
            throw std::logic_error(
                "GatherDataScalarPy PyArray_SimpleNew failed\n");
        }
    }
    Py_INCREF(value);
    return  value;
}

PyObject *GatherDataScalarPy::setValue(PyArrayObject *value)
{
    void *pvoid = PyArray_DATA(value);
    double *from = static_cast<double *>(pvoid);
    gatherDataScalar->setValue(from,gatherData->getNumberChannels());
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *createGatherDataScalarPy(
    GatherDataScalar::shared_pointer gatherDataScalar)
{
    GatherDataScalarPy *pvt =
         new GatherDataScalarPy(gatherDataScalar);
    int nd = 1;
    npy_intp dims[nd];
    dims[0] = 1;
    /* I tried NPY_VOID but it did not work. Thus hack*/
    PyObject *pyObject = PyArray_SimpleNew(1,dims,NPY_ULONGLONG);
    if(pyObject==0) {
        throw std::logic_error(
            "createGatherDataScalarPy PyArray_SimpleNew failed\n");
    }
    void *addr = PyArray_DATA(pyObject);
    GatherDataScalarPy **ppGatherDataScalarPy
        = static_cast< GatherDataScalarPy **>(addr);
    *ppGatherDataScalarPy = pvt;
    return pyObject;
}

static char _destroyDoc[] = "destroy gatherDataPy.";
static char _getAlarmDoc[] = "C++ method for getAlarm.";
static char _getTimeStampDoc[] = "C++ method for getTimeStamp.";
static char _getNumberChannelsDoc[] = "C++ method for getNumberChannels.";
static char _anyBadDoc[] = "C++ method for anyBad.";
static char _isBadDoc[] = "C++ method for isBad.";
static char _badChangeDoc[] = "C++ method for badChange.";
static char _allConnectedDoc[] = "C++ method for allConnected.";
static char _isConnectedDoc[] = "C++ method for isConnected.";
static char _connectionChangeDoc[] = "C++ method for connectionChange.";
static char _severityChangeDoc[] = "C++ method for severityChange.";
static char _getSeverityDoc[] = "C++ method for getSeverity.";
static char _setScalarValueDoc[] = "C++ method for setScalarValue.";
static char _getScalarValueDoc[] = "C++ method for getScalarValue.";

static PyObject * _destroy(PyObject *willBeNull, PyObject *args)
{
    PyArrayObject *pcppPvt = 0;
    if(!PyArg_ParseTuple(args,"O!:gatherDataPy",
        &PyArray_Type,&pcppPvt))
    {
        return NULL;
    }
    void *pvoid = PyArray_DATA(pcppPvt);
    GatherDataPy **ppGatherDataPy = static_cast< GatherDataPy **>(pvoid);
    GatherDataPy *gatherDataPy = *ppGatherDataPy;
    delete gatherDataPy;
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getAlarm(PyObject *willBeNull, PyObject *args)
{
    PyArrayObject *pcppPvt = 0;
    PyObject *pyAlarm = 0;
    if(!PyArg_ParseTuple(args,"O!O:gatherDataPy",
        &PyArray_Type,&pcppPvt,&pyAlarm))
    {
        return NULL;
    }
    void *pvoid = PyArray_DATA(pcppPvt);
    GatherDataPy **ppGatherDataPy = static_cast< GatherDataPy **>(pvoid);
    GatherDataPy *gatherDataPy = *ppGatherDataPy;
    return gatherDataPy->getAlarm(pyAlarm);
}

static PyObject * _getTimeStamp(PyObject *willBeNull, PyObject *args)
{
    PyArrayObject *pcppPvt = 0;
    PyObject *pyTimeStamp = 0;
    if(!PyArg_ParseTuple(args,"O!O:gatherDataPy",
        &PyArray_Type,&pcppPvt,&pyTimeStamp))
    {
        return NULL;
    }
    void *pvoid = PyArray_DATA(pcppPvt);
    GatherDataPy **ppGatherDataPy = static_cast< GatherDataPy **>(pvoid);
    GatherDataPy *gatherDataPy = *ppGatherDataPy;
    return gatherDataPy->getTimeStamp(pyTimeStamp);
}

static PyObject * _getNumberChannels(PyObject *willBeNull, PyObject *args)
{
    PyArrayObject *pcppPvt = 0;
    if(!PyArg_ParseTuple(args,"O!:gatherDataPy",
        &PyArray_Type,&pcppPvt))
    {
        return NULL;
    }
    void *pvoid = PyArray_DATA(pcppPvt);
    GatherDataPy **ppGatherDataPy = static_cast< GatherDataPy **>(pvoid);
    GatherDataPy *gatherDataPy = *ppGatherDataPy;
    return gatherDataPy->getNumberChannels();
}

static PyObject * _anyBad(PyObject *willBeNull, PyObject *args)
{
    PyArrayObject *pcppPvt = 0;
    if(!PyArg_ParseTuple(args,"O!:gatherDataPy",
        &PyArray_Type,&pcppPvt))
    {
        return NULL;
    }
    void *pvoid = PyArray_DATA(pcppPvt);
    GatherDataPy **ppGatherDataPy = static_cast< GatherDataPy **>(pvoid);
    GatherDataPy *gatherDataPy = *ppGatherDataPy;
    return gatherDataPy->anyBad();
}

static PyObject * _isBad(PyObject *willBeNull, PyObject *args)
{
    PyArrayObject *pcppPvt = 0;
    int index;
    if(!PyArg_ParseTuple(args,"O!i:gatherDataPy",
        &PyArray_Type,&pcppPvt,&index))
    {
        return NULL;
    }
    void *pvoid = PyArray_DATA(pcppPvt);
    GatherDataPy **ppGatherDataPy = static_cast< GatherDataPy **>(pvoid);
    GatherDataPy *gatherDataPy = *ppGatherDataPy;
    return gatherDataPy->isBad(index);
}

static PyObject * _badChange(PyObject *willBeNull, PyObject *args)
{
    PyArrayObject *pcppPvt = 0;
    if(!PyArg_ParseTuple(args,"O!:gatherDataPy",
        &PyArray_Type,&pcppPvt))
    {
        return NULL;
    }
    void *pvoid = PyArray_DATA(pcppPvt);
    GatherDataPy **ppGatherDataPy = static_cast< GatherDataPy **>(pvoid);
    GatherDataPy *gatherDataPy = *ppGatherDataPy;
    return gatherDataPy->badChange();
}

static PyObject * _allConnected(PyObject *willBeNull, PyObject *args)
{
    PyArrayObject *pcppPvt = 0;
    if(!PyArg_ParseTuple(args,"O!:gatherDataPy",
        &PyArray_Type,&pcppPvt))
    {
        return NULL;
    }
    void *pvoid = PyArray_DATA(pcppPvt);
    GatherDataPy **ppGatherDataPy = static_cast< GatherDataPy **>(pvoid);
    GatherDataPy *gatherDataPy = *ppGatherDataPy;
    return gatherDataPy->allConnected();
}

static PyObject * _isConnected(PyObject *willBeNull, PyObject *args)
{
    PyArrayObject *pcppPvt = 0;
    int index;
    if(!PyArg_ParseTuple(args,"O!i:gatherDataPy",
        &PyArray_Type,&pcppPvt,&index))
    {
        return NULL;
    }
    void *pvoid = PyArray_DATA(pcppPvt);
    GatherDataPy **ppGatherDataPy = static_cast< GatherDataPy **>(pvoid);
    GatherDataPy *gatherDataPy = *ppGatherDataPy;
    return gatherDataPy->isConnected(index);
}

static PyObject * _connectionChange(PyObject *willBeNull, PyObject *args)
{
    PyArrayObject *pcppPvt = 0;
    if(!PyArg_ParseTuple(args,"O!:gatherDataPy",
        &PyArray_Type,&pcppPvt))
    {
        return NULL;
    }
    void *pvoid = PyArray_DATA(pcppPvt);
    GatherDataPy **ppGatherDataPy = static_cast< GatherDataPy **>(pvoid);
    GatherDataPy *gatherDataPy = *ppGatherDataPy;
    return gatherDataPy->connectionChange();
}

static PyObject * _severityChange(PyObject *willBeNull, PyObject *args)
{
    PyArrayObject *pcppPvt = 0;
    if(!PyArg_ParseTuple(args,"O!:gatherDataPy",
        &PyArray_Type,&pcppPvt))
    {
        return NULL;
    }
    void *pvoid = PyArray_DATA(pcppPvt);
    GatherDataPy **ppGatherDataPy = static_cast< GatherDataPy **>(pvoid);
    GatherDataPy *gatherDataPy = *ppGatherDataPy;
    return gatherDataPy->severityChange();
}

static PyObject * _getSeverity(PyObject *willBeNull, PyObject *args)
{
    PyArrayObject *pcppPvt = 0;
    int index;
    if(!PyArg_ParseTuple(args,"O!i:gatherDataPy",
        &PyArray_Type,&pcppPvt,&index))
    {
        return NULL;
    }
    void *pvoid = PyArray_DATA(pcppPvt);
    GatherDataPy **ppGatherDataPy = static_cast< GatherDataPy **>(pvoid);
    GatherDataPy *gatherDataPy = *ppGatherDataPy;
    return gatherDataPy->getSeverity(index);
}

static PyObject * _setScalarValue(PyObject *willBeNull, PyObject *args)
{
    PyArrayObject *pcppPvt = 0;
    PyArrayObject *pyArray;
    if(!PyArg_ParseTuple(args,"O!O!:gatherDataPy",
        &PyArray_Type,&pcppPvt,
        &PyArray_Type,&pyArray))
    {
        return NULL;
    }
    void *pvoid = PyArray_DATA(pcppPvt);
    GatherDataScalarPy **ppGatherDataScalarPy = static_cast< GatherDataScalarPy **>(pvoid);
    GatherDataScalarPy *gatherDataScalarPy = *ppGatherDataScalarPy;
    return gatherDataScalarPy->setValue(pyArray);
}

static PyObject * _getScalarValue(PyObject *willBeNull, PyObject *args)
{
    PyArrayObject *pcppPvt = 0;
    if(!PyArg_ParseTuple(args,"O!:gatherDataPy",
        &PyArray_Type,&pcppPvt))
    {
        return NULL;
    }
    void *pvoid = PyArray_DATA(pcppPvt);
    GatherDataScalarPy **ppGatherDataScalarPy = static_cast< GatherDataScalarPy **>(pvoid);
    GatherDataScalarPy *gatherDataScalarPy = *ppGatherDataScalarPy;
    return gatherDataScalarPy->getValue();
}


static PyMethodDef methods[] = {
    {"_destroy",_destroy,METH_VARARGS,_destroyDoc},
    {"_getAlarm",_getAlarm,METH_VARARGS,_getAlarmDoc},
    {"_getTimeStamp",_getTimeStamp,METH_VARARGS,_getTimeStampDoc},
    {"_getNumberChannels",_getNumberChannels,METH_VARARGS,_getNumberChannelsDoc},
    {"_anyBad",_anyBad,METH_VARARGS,_anyBadDoc},
    {"_isBad",_isBad,METH_VARARGS,_isBadDoc},
    {"_badChange",_badChange,METH_VARARGS,_badChangeDoc},
    {"_allConnected",_allConnected,METH_VARARGS,_allConnectedDoc},
    {"_isConnected",_isConnected,METH_VARARGS,_isConnectedDoc},
    {"_connectionChange",_connectionChange,METH_VARARGS,_connectionChangeDoc},
    {"_severityChange",_severityChange,METH_VARARGS,_severityChangeDoc},
    {"_getSeverity",_getSeverity,METH_VARARGS,_getSeverityDoc},
    {"_setScalarValue",_setScalarValue,METH_VARARGS,_setScalarValueDoc},
    {"_getScalarValue",_getScalarValue,METH_VARARGS,_getScalarValueDoc},
    {NULL,NULL,0,NULL}
};

PyMODINIT_FUNC initgatherDataPy(void)
{
    PyObject * m = Py_InitModule("gatherDataPy",methods);
    if(m==NULL) printf("initgatherDataPy failed\n");
    import_array();
}
}}
