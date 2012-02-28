/*timeStampPy.cpp */
/*
 *Copyright - See the COPYRIGHT that is included with this distribution.
 *EPICS pvServiceCPP is distributed subject to a Software License Agreement found
 *in file LICENSE that is included with this distribution.
 */
/* Author:  Marty Kraimer Date: 2011.12 */

#undef _POSIX_C_SOURCE
#undef _XOPEN_SOURCE
#include <Python.h>


#include <pv/pvData.h>
#include <pv/timeStamp.h>
#include <pv/pvTimeStamp.h>
#include <stdexcept>

namespace epics { namespace pvData {

class TimeStampPvt {
public:
    TimeStampPvt();
    ~TimeStampPvt();
    void destroy();
    PyObject *get(){return pyObject;}
public:
    TimeStamp timeStamp;
    PyObject *pyObject;
};

TimeStampPvt::TimeStampPvt()
{
    pyObject = PyCapsule_New(&timeStamp,"timeStamp",0);
    Py_INCREF(pyObject);
}

TimeStampPvt::~TimeStampPvt()
{
}

void TimeStampPvt::destroy()
{
    Py_DECREF(pyObject);
}


static PyObject * _init(PyObject *willbenull, PyObject *args)
{
    TimeStampPvt *pvt = new TimeStampPvt();
    PyObject *pyObject = PyCapsule_New(pvt,"timeStampPvt",0);
    return pyObject;
}

static PyObject * _destroy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:timeStampPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"timeStampPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    TimeStampPvt *pvt = static_cast<TimeStampPvt *>(pvoid);
    pvt->destroy();
    delete pvt;
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getTimeStampPy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:timeStampPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"timeStampPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    TimeStampPvt *pvt = static_cast<TimeStampPvt *>(pvoid);
    return pvt->get();
}

static PyObject * _getSeconds(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:timeStampPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"timeStampPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    TimeStampPvt *pvt = static_cast<TimeStampPvt *>(pvoid);
    return Py_BuildValue("k",pvt->timeStamp.getSecondsPastEpoch());
}

static PyObject * _setSeconds(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    int64 value;
    if(!PyArg_ParseTuple(args,"OL:timeStampPy",
        &pcapsule,
        &value))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,seconds)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"timeStampPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    TimeStampPvt *pvt = static_cast<TimeStampPvt *>(pvoid);
    int32 nano = pvt->timeStamp.getNanoSeconds();
    pvt->timeStamp.put(value,nano);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getNano(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:timeStampPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"timeStampPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    TimeStampPvt *pvt = static_cast<TimeStampPvt *>(pvoid);
    return Py_BuildValue("i",pvt->timeStamp.getNanoSeconds());
}

static PyObject * _setNano(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    int32 value;
    if(!PyArg_ParseTuple(args,"Oi:timeStampPy",
        &pcapsule,
        &value))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,nanoSeconds)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"timeStampPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    TimeStampPvt *pvt = static_cast<TimeStampPvt *>(pvoid);
    int64 secs = pvt->timeStamp.getSecondsPastEpoch();
    pvt->timeStamp.put(secs,value);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getUserTag(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:timeStampPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"timeStampPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    TimeStampPvt *pvt = static_cast<TimeStampPvt *>(pvoid);
    return Py_BuildValue("i",pvt->timeStamp.getUserTag());
}

static char _initDoc[] = "_init timeStampPy.";
static char _destroyDoc[] = "_destroy timeStampPy.";
static char _getTimeStampDoc[] = "_getTimeStampPy timeStampPy.";
static char _getSecondsDoc[] = "_getSeconds timeStampPy.";
static char _setSecondsDoc[] = "_setSeconds timeStampPy.";
static char _getNanoDoc[] = "_getNano timeStampPy.";
static char _setNanoDoc[] = "_setNano timeStampPy.";
static char _getUserTagDoc[] = "_getUserTag timeStampPy.";

static PyMethodDef methods[] = {
    {"_init",_init,METH_VARARGS,_initDoc},
    {"_destroy",_destroy,METH_VARARGS,_destroyDoc},
    {"_getTimeStampPy",_getTimeStampPy,METH_VARARGS,_getTimeStampDoc},
    {"_getSeconds",_getSeconds,METH_VARARGS,_getSecondsDoc},
    {"_setSeconds",_setSeconds,METH_VARARGS,_setSecondsDoc},
    {"_getNano",_getNano,METH_VARARGS,_getNanoDoc},
    {"_setNano",_setNano,METH_VARARGS,_setNanoDoc},
    {"_getUserTag",_getUserTag,METH_VARARGS,_getUserTagDoc},
    {NULL,NULL,0,NULL}
};

PyMODINIT_FUNC inittimeStampPy(void)
{
    PyObject * m = Py_InitModule("timeStampPy",methods);
    if(m==NULL) printf("inittimeStampPy failed\n");
}

}}

