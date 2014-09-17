/* ntscalarPy.cpp */
/*
 *Copyright - See the COPYRIGHT that is included with this distribution.
 *EPICS pvServiceCPP is distributed subject to a Software License Agreement found
 *in file LICENSE that is included with this distribution.
 */
/* Author:  Marty Kraimer Date: 2011.12 */

#undef _POSIX_C_SOURCE
#undef _XOPEN_SOURCE
#include <Python.h>

#include <sstream>

#include <pv/convert.h>
#include <pv/nt.h>
#include <stdexcept>


namespace epics { namespace masar {

using namespace epics::pvData;
using namespace epics::nt;
using namespace std;
using std::tr1::static_pointer_cast;

class NTScalarPvt {
public:
    NTScalarPvt(
        NTScalar::shared_pointer ntscalar,
        PVStructurePtr const & pvStructure);
    ~NTScalarPvt();
    void destroy();
    PyObject *get(){return pyObject;}
public:
    NTScalar::shared_pointer ntscalar;
    PVStructurePtr pvStructure;
    PyObject *pyObject;
};

NTScalarPvt::NTScalarPvt(
    NTScalar::shared_pointer arg,
    PVStructurePtr const & pv)
: ntscalar(arg),
  pvStructure(pv),
  pyObject(0)
{
    pyObject = PyCapsule_New(&pvStructure,"pvStructure",0);
    Py_INCREF(pyObject);
}

NTScalarPvt::~NTScalarPvt()
{
}

void NTScalarPvt::destroy()
{
    Py_DECREF(pyObject);
    ntscalar.reset();
}

static PyObject * _init(PyObject *willbenull, PyObject *args)
{
    PyObject *capsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntscalarpy",
        &capsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvStructure)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(capsule,"pvStructure");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Must be pvStructure PyCapsule");
        return NULL;
    }
    PVStructurePtr *pv =
        static_cast<PVStructurePtr *>(pvoid);
    PVStructurePtr pvStructure = *pv;
    NTScalarPtr ntscalar = NTScalar::narrow(pvStructure);
    NTScalarPvt *pvt = new NTScalarPvt(ntscalar,pvStructure);
    return PyCapsule_New(pvt,"ntscalarPvt",0);
}

static PyObject * _create(PyObject *willbenull, PyObject *args)
{
    const char *type = 0;
    if(!PyArg_ParseTuple(args,"s:ntnamevaluepy",&type))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected scalarType");
        return NULL;
    }
    ScalarType scalarType(pvString);
    string stype(type);
    if(stype.compare("string")==0) {
    } else if(stype.compare("string")==0) {
        scalarType = pvString;
    } else if(stype.compare("boolean")==0) {
        scalarType = pvBoolean;
    } else if(stype.compare("byte")==0) {
        scalarType = pvByte;
    } else if(stype.compare("short")==0) {
        scalarType = pvShort;
    } else if(stype.compare("int")==0) {
        scalarType = pvInt;
    } else if(stype.compare("long")==0) {
        scalarType = pvLong;
    } else if(stype.compare("float")==0) {
        scalarType = pvFloat;
    } else if(stype.compare("double")==0) {
        scalarType = pvDouble;
    } else {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Illegal scalarType");
        return NULL;
    }

    NTScalarBuilderPtr builder = NTScalar::createBuilder();
    NTScalarPtr ntscalar = builder->
            value(scalarType)->
            addDescriptor()->
            addAlarm()->
            addTimeStamp()->
            addDisplay()->
            addControl()->
            create();

    NTScalarPvt *pvt = new NTScalarPvt(ntscalar,ntscalar->getPVStructure());
    return PyCapsule_New(pvt,"ntscalarPvt",0);
}


static PyObject * _destroy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntscalarPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntscalarPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTScalarPvt *pvt = static_cast<NTScalarPvt *>(pvoid);
    pvt->destroy();
    delete pvt;
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _str(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntscalarPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntscalarPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTScalarPvt *pvt = static_cast<NTScalarPvt *>(pvoid);
    std::stringstream buffer;
    buffer << *(pvt->ntscalar->getPVStructure());
    return Py_BuildValue("s",buffer.str().c_str());
}

static PyObject * _getNTScalarPy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntscalarPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntscalarPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTScalarPvt *pvt = static_cast<NTScalarPvt *>(pvoid);
    return pvt->get();
}

static PyObject * _getPVStructure(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntscalarPy",
        &pcapsule))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntscalarPy");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTScalarPvt *pvt = static_cast<NTScalarPvt *>(pvoid);
    pvt->pvStructure = pvt->ntscalar->getPVStructure();
    return PyCapsule_New(&pvt->pvStructure,"pvStructure",0);
}


static PyObject * _getTimeStamp(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    PyObject *ptimeStamp = 0;
    if(!PyArg_ParseTuple(args,"OO:ntscalarPy",
        &pcapsule,
        &ptimeStamp))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,ptimeStamp)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntscalarPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTScalarPvt *pvt = static_cast<NTScalarPvt *>(pvoid);
    pvoid = PyCapsule_GetPointer(ptimeStamp,"timeStamp");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "second argument is not a timeStamp capsule");
        return NULL;
    }
    TimeStamp *xxx = static_cast<TimeStamp *>(pvoid);
    PVStructurePtr pvStructure = pvt->ntscalar->getTimeStamp();
    //if(pvStructure!=0) {
    if(!pvStructure) {
        PVTimeStamp pvTimeStamp;
        pvTimeStamp.attach(pvStructure);
        pvTimeStamp.get(*xxx);
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getAlarm(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    PyObject *palarm = 0;
    if(!PyArg_ParseTuple(args,"OO:ntscalarPy",
        &pcapsule,
        &palarm))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,palarm)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntscalarPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTScalarPvt *pvt = static_cast<NTScalarPvt *>(pvoid);
    pvoid = PyCapsule_GetPointer(palarm,"alarm");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "second argument is not an alarm capsule");
        return NULL;
    }
    Alarm *xxx = static_cast<Alarm *>(pvoid);
    PVStructurePtr pvStructure = pvt->ntscalar->getAlarm();
    if(!pvStructure) {
        PVAlarm pvAlarm;
        pvAlarm.attach(pvStructure);
        pvAlarm.get(*xxx);
    }
    Py_INCREF(Py_None);
    return Py_None;
}



static PyObject * _getValue(PyObject *willbenull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntscalarPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntscalarPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTScalarPvt *pvt = static_cast<NTScalarPvt *>(pvoid);
    PVStructurePtr pvStructure = pvt->ntscalar->getPVStructure();
    PVScalarPtr pvScalar = pvStructure->getSubField<PVScalar>("value");
    ConvertPtr convert = getConvert();
    ScalarType scalarType = pvScalar->getScalar()->getScalarType();
    switch(scalarType) {
        case pvBoolean: {
            PVBooleanPtr pv =  static_pointer_cast<PVBoolean>(pvScalar);
            bool value = pv->get();
            int ivalue = (value ? 1 : 0);
            return Py_BuildValue("i",ivalue);
        }
        case pvByte:
        case pvShort:
        case pvInt:
        {
            int32 value = convert->toInt(pvScalar);
            return Py_BuildValue("i",value);
        }
        case pvUByte:
        case pvUShort:
        case pvUInt:
        {
            uint32 value = convert->toUInt(pvScalar);
            return Py_BuildValue("i",value);
        }
        case pvLong: {
            int64 value = convert->toLong(pvScalar);
            return Py_BuildValue("k",value);
        }
        case pvULong: {
            uint64 value = convert->toULong(pvScalar);
            return Py_BuildValue("k",value);
        }
        case pvFloat: {
            float value = convert->toFloat(pvScalar);
            return Py_BuildValue("f",value);
        }
        case pvDouble: {
            double value = convert->toDouble(pvScalar);
            return Py_BuildValue("d",value);
        }
        case pvString: {
            string value = convert->toString(pvScalar);
            return Py_BuildValue("s",value.c_str());
        }
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getDisplay(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    PyObject *pdisplay = 0;
    if(!PyArg_ParseTuple(args,"OO:ntscalarPy",
        &pcapsule,
        &pdisplay))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,pdisplay)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntscalarPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTScalarPvt *pvt = static_cast<NTScalarPvt *>(pvoid);
    pvoid = PyCapsule_GetPointer(pdisplay,"display");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "second argument is not an display capsule");
        return NULL;
    }
    Display *xxx = static_cast<Display *>(pvoid);
    PVStructurePtr pvStructure = pvt->ntscalar->getDisplay();
    if(!pvStructure) {
        PVDisplay pvDisplay;
        pvDisplay.attach(pvStructure);
        pvDisplay.get(*xxx);
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _getControl(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    PyObject *pcontrol = 0;
    if(!PyArg_ParseTuple(args,"OO:ntscalarPy",
        &pcapsule,
        &pcontrol))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,pcontrol)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntscalarPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTScalarPvt *pvt = static_cast<NTScalarPvt *>(pvoid);
    pvoid = PyCapsule_GetPointer(pcontrol,"control");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "second argument is not an control capsule");
        return NULL;
    }
    Control *xxx = static_cast<Control *>(pvoid);
    PVStructurePtr pvStructure = pvt->ntscalar->getControl();
    if(!pvStructure) {
        PVControl pvControl;
        pvControl.attach(pvStructure);
        pvControl.get(*xxx);
    }
    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject * _getDescriptor(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:ntscalarPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"ntscalarPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    NTScalarPvt *pvt = static_cast<NTScalarPvt *>(pvoid);
    PVStringPtr pvValue =
        pvt->ntscalar->getPVStructure()->getSubField<PVString>("descriptor");
    string value("");
    if(pvValue) value =  pvValue->get();
    return Py_BuildValue("s",value.c_str());
}


static char _initDoc[] = "_init ntscalarPy.";
static char _createDoc[] = "_create ntscalarPy.";
static char _destroyDoc[] = "_destroy ntscalarPy.";
static char _strDoc[] = "_str  ntscalarPy.";
static char _getNTScalarPyDoc[] = "_getNTScalarPy ntscalarPy.";
static char _getPVStructureDoc[] = "_getPVStructure.";
static char _getValueDoc[] = "_getValue.";
static char _getTimeStampDoc[] = "_getTimeStamp ntscalarPy.";
static char _getAlarmDoc[] = "_getAlarm ntscalarPy.";
static char _getDisplayDoc[] = "_getDisplay ntscalarPy.";
static char _getControlDoc[] = "_getControl ntscalarPy.";
static char _getDescriptorDoc[] = "_getDescriptor ntscalarPy.";

static PyMethodDef methods[] = {
    {"_init",_init,METH_VARARGS,_initDoc},
    {"_create",_create,METH_VARARGS,_createDoc},
    {"_destroy",_destroy,METH_VARARGS,_destroyDoc},
    {"_str",_str,METH_VARARGS,_strDoc},
    {"_getNTScalarPy",_getNTScalarPy,METH_VARARGS,_getNTScalarPyDoc},
    {"_getPVStructure",_getPVStructure,METH_VARARGS,_getPVStructureDoc},
    {"_getValue",_getValue,METH_VARARGS,_getValueDoc},
    {"_getTimeStamp",_getTimeStamp,METH_VARARGS,_getTimeStampDoc},
    {"_getAlarm",_getAlarm,METH_VARARGS,_getAlarmDoc},
    {"_getDisplay",_getDisplay,METH_VARARGS,_getDisplayDoc},
    {"_getControl",_getControl,METH_VARARGS,_getControlDoc},
    {"_getDescriptor",_getDescriptor,METH_VARARGS,_getDescriptorDoc},
    {NULL,NULL,0,NULL}
};

PyMODINIT_FUNC initntscalarPy(void)
{
    PyObject * m = Py_InitModule("ntscalarPy",methods);
    if(m==NULL) printf("initntscalarPy failed\n");
}

}}

