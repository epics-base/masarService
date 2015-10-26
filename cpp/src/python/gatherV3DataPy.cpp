/* gatherV3DataPy.cpp */
/*
 *Copyright - See the COPYRIGHT that is included with this distribution.
 *EPICS pvServiceCPP is distributed subject to a Software License Agreement found
 *in file LICENSE that is included with this distribution.
 */
/* Author:  Marty Kraimer Date: 2011.12 */

#undef _POSIX_C_SOURCE
#undef _XOPEN_SOURCE
#include <Python.h>

#include <pv/gatherV3Data.h>
#include <stdexcept>

namespace epics { namespace masar {

using namespace epics::pvData;
using namespace epics::nt;
using namespace std;
typedef std::tr1::shared_ptr<NTMultiChannel> NTMultiChannelPtr;

class GatherV3DataPyPvt {
public:
    GatherV3DataPyPvt(
        shared_vector<const std::string> const & channelNames);
    ~GatherV3DataPyPvt();
public:
    GatherV3DataPtr gatherV3Data;
    PVStructurePtr pvStructure;
};

GatherV3DataPyPvt::GatherV3DataPyPvt(
    shared_vector<const std::string> const & channelNames)
: gatherV3Data(GatherV3Data::create(channelNames))
{
}


GatherV3DataPyPvt::~GatherV3DataPyPvt()
{
}

static PyObject * _init(PyObject *willBeNull, PyObject *args)
{
    PyObject *pytuple = 0;
    if(!PyArg_ParseTuple(args,"O:gatherV3DataPy",
        &pytuple))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (channelNames)");
        return NULL;
    }
    if(!PyTuple_Check(pytuple)) {
        PyErr_SetString(PyExc_SyntaxError,
           "argument is not a tuple of channelNames");
        return NULL;
    }
    Py_ssize_t num = PyTuple_GET_SIZE(pytuple);
    shared_vector<string> names(num);
    for(Py_ssize_t i=0; i<num; i++) {
        PyObject *pyobject = PyTuple_GetItem(pytuple,i);
        if(pyobject==NULL) {
            PyErr_SetString(PyExc_SyntaxError,
               "a channelName is null");
            return NULL;
        }
        char *sval =  PyString_AsString(pyobject);
        if(sval==NULL) {
            PyErr_SetString(PyExc_SyntaxError,
               "a channelName is not a string");
            return NULL;
        }
        names[i] = string(sval);
    }
    shared_vector<const string> name(freeze(names));
    GatherV3DataPyPvt *pvt = new GatherV3DataPyPvt(name);
    return PyCapsule_New(pvt,"gatherV3DataPvt",0);
}


static PyObject * _destroy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:gatherV3DataPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"gatherV3DataPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    GatherV3DataPyPvt *pvt = static_cast<GatherV3DataPyPvt *>(pvoid);
    GatherV3DataPtr const & gatherV3Data = pvt->gatherV3Data;
    Py_BEGIN_ALLOW_THREADS
        gatherV3Data->destroy();
        delete pvt;
    Py_END_ALLOW_THREADS
    Py_RETURN_NONE;
}

static PyObject * _connect(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    double timeout = 1.0;
    if(!PyArg_ParseTuple(args,"Od:gatherV3DataPy",
        &pcapsule,
        &timeout))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,timeout)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"gatherV3DataPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    GatherV3DataPyPvt *pvt = static_cast<GatherV3DataPyPvt *>(pvoid);
    GatherV3DataPtr const & gatherV3Data = pvt->gatherV3Data;
    bool result = false;
    Py_BEGIN_ALLOW_THREADS
        result = gatherV3Data->connect(timeout);
    Py_END_ALLOW_THREADS
    if(result) {
         Py_RETURN_TRUE;
    }
    Py_RETURN_FALSE;
}

static PyObject * _get(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:gatherV3DataPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"gatherV3DataPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "arg must be return from _init");
        return NULL;
    }
    GatherV3DataPyPvt *pvt = static_cast<GatherV3DataPyPvt *>(pvoid);
    GatherV3DataPtr const & gatherV3Data = pvt->gatherV3Data;
    bool result = true;
    Py_BEGIN_ALLOW_THREADS
        result = gatherV3Data->get();
    Py_END_ALLOW_THREADS
    if(result) {
        Py_RETURN_TRUE;
    }
    Py_RETURN_FALSE;
}

static PyObject * _put(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:gatherV3DataPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"gatherV3DataPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "arg must be return from _init");
        return NULL;
    }
    GatherV3DataPyPvt *pvt = static_cast<GatherV3DataPyPvt *>(pvoid);
    GatherV3DataPtr const & gatherV3Data = pvt->gatherV3Data;
    bool result = true;
    Py_BEGIN_ALLOW_THREADS
        result = gatherV3Data->put();
    Py_END_ALLOW_THREADS
    if(result) {
        Py_RETURN_TRUE;
    }
    Py_RETURN_FALSE;
}

static PyObject * _getMessage(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:gatherV3DataPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"gatherV3DataPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    GatherV3DataPyPvt *pvt = static_cast<GatherV3DataPyPvt *>(pvoid);
    string message = pvt->gatherV3Data->getMessage();
    PyObject *pyObject = Py_BuildValue("s",message.c_str());
    return pyObject;
}

static PyObject * _getPVStructure(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:gatherV3DataPy",
        &pcapsule))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"gatherV3DataPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    GatherV3DataPyPvt *pvt = static_cast<GatherV3DataPyPvt *>(pvoid);
    pvt->pvStructure = pvt->gatherV3Data->getNTMultiChannel()->getPVStructure();
    return PyCapsule_New(&pvt->pvStructure,"pvStructure",0);
}

static char _initDoc[] = "_init gatherV3DataPy.";
static char _destroyDoc[] = "_destroy gatherV3DataPy.";
static char _connectDoc[] = "_connect.";
static char _getDoc[] = "_get.";
static char _putDoc[] = "_put.";
static char _getMessageDoc[] = "_getMessage.";
static char _getPVStructureDoc[] = "_getPVStructure.";

static PyMethodDef methods[] = {
    {"_init",_init,METH_VARARGS,_initDoc},
    {"_destroy",_destroy,METH_VARARGS,_destroyDoc},
    {"_connect",_connect,METH_VARARGS,_connectDoc},
    {"_get",_get,METH_VARARGS,_getDoc},
    {"_put",_put,METH_VARARGS,_putDoc},
    {"_getMessage",_getMessage,METH_VARARGS,_getMessageDoc},
    {"_getPVStructure",_getPVStructure,METH_VARARGS,_getPVStructureDoc},
    {NULL,NULL,0,NULL}
};

PyMODINIT_FUNC initgatherV3DataPy(void)
{
    PyObject * m = Py_InitModule("gatherV3DataPy",methods);
    if(m==NULL) printf("initgatherV3DataPy failed\n");
}

}}
