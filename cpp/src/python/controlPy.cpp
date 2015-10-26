/*controlPy.cpp */
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
#include <pv/control.h>
#include <pv/pvControl.h>
#include <stdexcept>

namespace epics { namespace masar {

using namespace epics::pvData;
using namespace std;

class ControlPvt {
public:
    ControlPvt();
    ~ControlPvt();
    void destroy();
    PyObject *get(){return pyObject;}
public:
    Control control;
    PyObject *pyObject;
};

ControlPvt::ControlPvt()
{
    pyObject = PyCapsule_New(&control,"control",0);
    Py_INCREF(pyObject);
}

ControlPvt::~ControlPvt()
{
}

void ControlPvt::destroy()
{
    Py_DECREF(pyObject);
}


static PyObject * _init(PyObject *willbenull, PyObject *args)
{
    ControlPvt *pvt = new ControlPvt();
    PyObject *pyObject = PyCapsule_New(pvt,"controlPvt",0);
    return pyObject;
}

static PyObject * _destroy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:controlPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"controlPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    ControlPvt *pvt = static_cast<ControlPvt *>(pvoid);
    pvt->destroy();
    delete pvt;
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _str(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:controlPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"controlPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    ControlPvt *pvt = static_cast<ControlPvt *>(pvoid);
    char buffer[256];
    double limitLow = pvt->control.getLow();
    double limitHigh = pvt->control.getHigh();
    double minStep = pvt->control.getMinStep();
    sprintf(buffer,"limitLow %e limitHigh %e minStep %e",limitLow,limitHigh,minStep);
    return Py_BuildValue("s",buffer);
}


static PyObject * _getControlPy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:controlPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"controlPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    ControlPvt *pvt = static_cast<ControlPvt *>(pvoid);
    return pvt->get();
}

static PyObject * _getLimitLow(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:controlPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"controlPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    ControlPvt *pvt = static_cast<ControlPvt *>(pvoid);
    return Py_BuildValue("d",pvt->control.getLow());
}

static PyObject * _setLimitLow(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    double value;
    if(!PyArg_ParseTuple(args,"Od:controlPy",
        &pcapsule,
        &value))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,limitLow)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"controlPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    ControlPvt *pvt = static_cast<ControlPvt *>(pvoid);
    pvt->control.setLow(value);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getLimitHigh(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:controlPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"controlPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    ControlPvt *pvt = static_cast<ControlPvt *>(pvoid);
    return Py_BuildValue("d",pvt->control.getHigh());
}

static PyObject * _setLimitHigh(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    double value;
    if(!PyArg_ParseTuple(args,"Od:controlPy",
        &pcapsule,
        &value))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,limitHigh)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"controlPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    ControlPvt *pvt = static_cast<ControlPvt *>(pvoid);
    pvt->control.setHigh(value);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getMinStep(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:controlPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"controlPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    ControlPvt *pvt = static_cast<ControlPvt *>(pvoid);
    return Py_BuildValue("d",pvt->control.getMinStep());
}

static PyObject * _setMinStep(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    double value;
    if(!PyArg_ParseTuple(args,"Od:controlPy",
        &pcapsule,
        &value))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,minStep)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"controlPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    ControlPvt *pvt = static_cast<ControlPvt *>(pvoid);
    pvt->control.setMinStep(value);
    Py_INCREF(Py_None);
    return Py_None;
}

static char _initDoc[] = "_init controlPy.";
static char _destroyDoc[] = "_destroy controlPy.";
static char _strDoc[] = "_str controlPy.";
static char _getControlDoc[] = "_getControlPy controlPy.";
static char _getLimitLowDoc[] = "_getLimitLow controlPy.";
static char _setLimitLowDoc[] = "_setLimitLow controlPy.";
static char _getLimitHighDoc[] = "_getLimitHigh controlPy.";
static char _setLimitHighDoc[] = "_setLimitHigh controlPy.";
static char _getMinStepDoc[] = "_getMinStep controlPy.";
static char _setMinStepDoc[] = "_setMinStep controlPy.";

static PyMethodDef methods[] = {
    {"_init",_init,METH_VARARGS,_initDoc},
    {"_destroy",_destroy,METH_VARARGS,_destroyDoc},
    {"_str",_str,METH_VARARGS,_strDoc},
    {"_getControlPy",_getControlPy,METH_VARARGS,_getControlDoc},
    {"_getLimitLow",_getLimitLow,METH_VARARGS,_getLimitLowDoc},
    {"_setLimitLow",_setLimitLow,METH_VARARGS,_setLimitLowDoc},
    {"_getLimitHigh",_getLimitHigh,METH_VARARGS,_getLimitHighDoc},
    {"_setLimitHigh",_setLimitHigh,METH_VARARGS,_setLimitHighDoc},
    {"_getMinStep",_getMinStep,METH_VARARGS,_getMinStepDoc},
    {"_setMinStep",_setMinStep,METH_VARARGS,_setMinStepDoc},
    {NULL,NULL,0,NULL}
};

PyMODINIT_FUNC initcontrolPy(void)
{
    PyObject * m = Py_InitModule("controlPy",methods);
    if(m==NULL) printf("initcontrolPy failed\n");
}

}}

