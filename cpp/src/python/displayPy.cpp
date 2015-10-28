/*displayPy.cpp */
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
#include <pv/display.h>
#include <pv/pvDisplay.h>
#include <stdexcept>

namespace epics { namespace masar {

using namespace epics::pvData;
using namespace std;

class DisplayPvt {
public:
    DisplayPvt();
    ~DisplayPvt();
    void destroy();
    PyObject *get(){return pyObject;}
public:
    Display display;
    PyObject *pyObject;
};

DisplayPvt::DisplayPvt()
{
    pyObject = PyCapsule_New(&display,"display",0);
    Py_INCREF(pyObject);
}

DisplayPvt::~DisplayPvt()
{
}

void DisplayPvt::destroy()
{
    Py_DECREF(pyObject);
}


static PyObject * _init(PyObject *willbenull, PyObject *args)
{
    DisplayPvt *pvt = new DisplayPvt();
    PyObject *pyObject = PyCapsule_New(pvt,"displayPvt",0);
    return pyObject;
}

static PyObject * _destroy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:displayPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"displayPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    DisplayPvt *pvt = static_cast<DisplayPvt *>(pvoid);
    pvt->destroy();
    delete pvt;
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _str(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:displayPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"displayPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    DisplayPvt *pvt = static_cast<DisplayPvt *>(pvoid);
    char buffer[256];
    double limitLow = pvt->display.getLow();
    double limitHigh = pvt->display.getHigh();
    string description = pvt->display.getDescription();
    string format = pvt->display.getFormat();
    string units = pvt->display.getUnits();
    sprintf(buffer,"limitLow %e limitHigh %e description %s format %s units %s",
        limitLow,limitHigh,description.c_str(),format.c_str(),units.c_str());
    return Py_BuildValue("s",buffer);
}


static PyObject * _getDisplayPy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:displayPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"displayPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    DisplayPvt *pvt = static_cast<DisplayPvt *>(pvoid);
    return pvt->get();
}

static PyObject * _getLimitLow(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:displayPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"displayPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    DisplayPvt *pvt = static_cast<DisplayPvt *>(pvoid);
    return Py_BuildValue("d",pvt->display.getLow());
}

static PyObject * _setLimitLow(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    double value;
    if(!PyArg_ParseTuple(args,"Od:displayPy",
        &pcapsule,
        &value))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,limitLow)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"displayPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    DisplayPvt *pvt = static_cast<DisplayPvt *>(pvoid);
    pvt->display.setLow(value);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getLimitHigh(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:displayPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"displayPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    DisplayPvt *pvt = static_cast<DisplayPvt *>(pvoid);
    return Py_BuildValue("d",pvt->display.getHigh());
}

static PyObject * _setLimitHigh(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    double value;
    if(!PyArg_ParseTuple(args,"Od:displayPy",
        &pcapsule,
        &value))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,limitHigh)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"displayPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    DisplayPvt *pvt = static_cast<DisplayPvt *>(pvoid);
    pvt->display.setHigh(value);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getDescription(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:displayPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"displayPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    DisplayPvt *pvt = static_cast<DisplayPvt *>(pvoid);
    return Py_BuildValue("s",pvt->display.getDescription().c_str());
}

static PyObject * _setDescription(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    char *buffer;
    if(!PyArg_ParseTuple(args,"Os:displayPy",
        &pcapsule,
        &buffer))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,string)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"displayPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    DisplayPvt *pvt = static_cast<DisplayPvt *>(pvoid);
    pvt->display.setDescription(buffer);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getFormat(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:displayPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"displayPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    DisplayPvt *pvt = static_cast<DisplayPvt *>(pvoid);
    return Py_BuildValue("s",pvt->display.getFormat().c_str());
}

static PyObject * _setFormat(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    char *buffer;
    if(!PyArg_ParseTuple(args,"Os:displayPy",
        &pcapsule,
        &buffer))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,string)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"displayPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    DisplayPvt *pvt = static_cast<DisplayPvt *>(pvoid);
    pvt->display.setFormat(buffer);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getUnits(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:displayPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"displayPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    DisplayPvt *pvt = static_cast<DisplayPvt *>(pvoid);
    return Py_BuildValue("s",pvt->display.getUnits().c_str());
}

static PyObject * _setUnits(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    char *buffer;
    if(!PyArg_ParseTuple(args,"Os:displayPy",
        &pcapsule,
        &buffer))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,string)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"displayPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    DisplayPvt *pvt = static_cast<DisplayPvt *>(pvoid);
    pvt->display.setUnits(buffer);
    Py_INCREF(Py_None);
    return Py_None;
}



static char _initDoc[] = "_init displayPy.";
static char _destroyDoc[] = "_destroy displayPy.";
static char _strDoc[] = "_str displayPy.";
static char _getDisplayDoc[] = "_getDisplayPy displayPy.";
static char _getLimitLowDoc[] = "_getLimitLow displayPy.";
static char _setLimitLowDoc[] = "_setLimitLow displayPy.";
static char _getLimitHighDoc[] = "_getLimitHigh displayPy.";
static char _setLimitHighDoc[] = "_setLimitHigh displayPy.";
static char _getDescriptionDoc[] = "_getDescription displayPy.";
static char _setDescriptionDoc[] = "_setDescription displayPy.";
static char _getFormatDoc[] = "_getFormat displayPy.";
static char _setFormatDoc[] = "_setFormat displayPy.";
static char _getUnitsDoc[] = "_getUnits displayPy.";
static char _setUnitsDoc[] = "_setUnits displayPy.";

static PyMethodDef methods[] = {
    {"_init",_init,METH_VARARGS,_initDoc},
    {"_destroy",_destroy,METH_VARARGS,_destroyDoc},
    {"_str",_str,METH_VARARGS,_strDoc},
    {"_getDisplayPy",_getDisplayPy,METH_VARARGS,_getDisplayDoc},
    {"_getLimitLow",_getLimitLow,METH_VARARGS,_getLimitLowDoc},
    {"_setLimitLow",_setLimitLow,METH_VARARGS,_setLimitLowDoc},
    {"_getLimitHigh",_getLimitHigh,METH_VARARGS,_getLimitHighDoc},
    {"_setLimitHigh",_setLimitHigh,METH_VARARGS,_setLimitHighDoc},
    {"_getDescription",_getDescription,METH_VARARGS,_getDescriptionDoc},
    {"_setDescription",_setDescription,METH_VARARGS,_setDescriptionDoc},
    {"_getFormat",_getFormat,METH_VARARGS,_getFormatDoc},
    {"_setFormat",_setFormat,METH_VARARGS,_setFormatDoc},
    {"_getUnits",_getUnits,METH_VARARGS,_getUnitsDoc},
    {"_setUnits",_setUnits,METH_VARARGS,_setUnitsDoc},
    {NULL,NULL,0,NULL}
};

PyMODINIT_FUNC initdisplayPy(void)
{
    PyObject * m = Py_InitModule("displayPy",methods);
    if(m==NULL) printf("initdisplayPy failed\n");
}

}}

