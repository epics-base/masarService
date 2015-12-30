/* channelRPCPy.cpp */
/*
 *Copyright - See the COPYRIGHT that is included with this distribution.
 *EPICS pvServiceCPP is distributed subject to a Software License Agreement found
 *in file LICENSE that is included with this distribution.
 */
/* Author:  Marty Kraimer Date: 2011.12 */

#undef _POSIX_C_SOURCE
#undef _XOPEN_SOURCE
#include <Python.h>

#include <iostream>
#include <stdexcept>

#include <epicsExit.h>

#include <pv/event.h>
#include <pv/rpcClient.h>
#include <pv/pvAccess.h>
#include <pv/clientFactory.h>

namespace epics { namespace masar {

using namespace epics::pvData;
using namespace epics::pvAccess;
using namespace std;

struct PyAllowThreads {
   PyThreadState *save;
   PyAllowThreads() :save(PyEval_SaveThread()) {}
   ~PyAllowThreads() { PyEval_RestoreThread(save); }
};

typedef std::tr1::shared_ptr<RPCClient> RPCClientPtr;
class ChannelRPCPyPvt {
public:
    ChannelRPCPyPvt(string const &serviceName);
    ~ChannelRPCPyPvt();
    void destroy();
    RPCClientPtr getChannelRPC(){
        return channelRPC;
    }
    PVStructurePtr pvResponse;
private:
    RPCClientPtr channelRPC;
};

ChannelRPCPyPvt::ChannelRPCPyPvt(
    string const &channelName)
: channelRPC(RPCClient::create(channelName))
{
     ClientFactory::start();
}

ChannelRPCPyPvt::~ChannelRPCPyPvt()
{
     //ClientFactory::stop();
}

void ChannelRPCPyPvt::destroy()
{
   channelRPC->destroy();
   channelRPC.reset();
}

static PyObject * _init(PyObject *willBeNull, PyObject *args)
{
    const char *serverName = 0;
    if(!PyArg_ParseTuple(args,"s:channelRPCPy",
        &serverName))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (serverName)");
        return NULL;
    }
    ChannelRPCPyPvt *pvt = new ChannelRPCPyPvt(serverName);
    PyObject *pyObject = PyCapsule_New(pvt,"channelRPCPyPvt",0);
    return pyObject;
}


static PyObject * _destroy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:channelRPCPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"channelRPCPyPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    ChannelRPCPyPvt *pvt = static_cast<ChannelRPCPyPvt *>(pvoid);
    Py_BEGIN_ALLOW_THREADS
         pvt->destroy();
    Py_END_ALLOW_THREADS
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _connect(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    double timeout = 1.0;
    if(!PyArg_ParseTuple(args,"Od:channelRPCPy",
        &pcapsule,
        &timeout))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,timeout)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"channelRPCPyPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    ChannelRPCPyPvt *pvt = static_cast<ChannelRPCPyPvt *>(pvoid);
    RPCClientPtr const & channelRPC = pvt->getChannelRPC();
    bool result = false;
    try {
        PyAllowThreads x;
        result = channelRPC->connect(timeout);
    } catch (epics::pvAccess::RPCRequestException & e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    } catch (std::runtime_error & e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    }

    if(result) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    PyErr_SetString(PyExc_RuntimeError, "timeout");
    return NULL;
}

static PyObject * _issueConnect(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:channelRPCPy",
        &pcapsule))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"channelRPCPyPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    ChannelRPCPyPvt *pvt = static_cast<ChannelRPCPyPvt *>(pvoid);
    RPCClientPtr const & channelRPC = pvt->getChannelRPC();

    try {
        PyAllowThreads x;
        channelRPC->issueConnect();
    } catch (std::runtime_error & e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _waitConnect(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    double timeout = 1.0;
    if(!PyArg_ParseTuple(args,"Od:channelRPCPy",
        &pcapsule,
        &timeout))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,timeout)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"channelRPCPyPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    ChannelRPCPyPvt *pvt = static_cast<ChannelRPCPyPvt *>(pvoid);
    RPCClientPtr const & channelRPC = pvt->getChannelRPC();
    bool result = false;
    try {
        PyAllowThreads x;
        result = channelRPC->waitConnect(timeout);
    } catch (epics::pvAccess::RPCRequestException & e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    } catch (std::runtime_error & e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    }

    if(result) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    return NULL;
}

static PyObject * _request(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    PyObject *pargument = 0;
    int *lastRequest = 0;
    if(!PyArg_ParseTuple(args,"OOi:channelRPCPy",
        &pcapsule,
        &pargument,
        &lastRequest))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,pargument)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"channelRPCPyPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    ChannelRPCPyPvt *pvt = static_cast<ChannelRPCPyPvt *>(pvoid);
    RPCClientPtr const & channelRPC = pvt->getChannelRPC();
    pvoid = PyCapsule_GetPointer(pargument,"pvStructure");
    PVStructure::shared_pointer *pvStructure =
        static_cast<PVStructure::shared_pointer *>(pvoid);
    bool last = (lastRequest==0) ? false : true ;
    try {
        PyAllowThreads x;
        pvt->pvResponse = channelRPC->request(*pvStructure,last);
    } catch (epics::pvAccess::RPCRequestException & e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    } catch (std::runtime_error & e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    }

    if(pvt->pvResponse.get()==0) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    PyObject *pyObject = PyCapsule_New(&pvt->pvResponse,"pvStructure",0);
    return pyObject;
}

static PyObject * _issueRequest(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    PyObject *pargument = 0;
    int *lastRequest = 0;
    if(!PyArg_ParseTuple(args,"OOi:channelRPCPy",
        &pcapsule,
        &pargument,
        &lastRequest))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt,pargument)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"channelRPCPyPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    ChannelRPCPyPvt *pvt = static_cast<ChannelRPCPyPvt *>(pvoid);
    RPCClientPtr const & channelRPC = pvt->getChannelRPC();
    pvoid = PyCapsule_GetPointer(pargument,"pvStructure");
    PVStructure::shared_pointer *pvStructure =
        static_cast<PVStructure::shared_pointer *>(pvoid);
    bool last = (lastRequest==0) ? false : true ;
    try {
        PyAllowThreads x;
        channelRPC->issueRequest(*pvStructure,last);
    } catch (epics::pvAccess::RPCRequestException & e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    } catch (std::runtime_error & e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _waitResponse(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    double timeout = 1.0;
    if(!PyArg_ParseTuple(args,"Od:channelRPCPy",
        &pcapsule,
        &timeout))
    {
        PyErr_SetString(PyExc_SyntaxError,
           "Bad argument. Expected (pvt)");
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"channelRPCPyPvt");
    if(pvoid==0) {
        PyErr_SetString(PyExc_SyntaxError,
           "first arg must be return from _init");
        return NULL;
    }
    ChannelRPCPyPvt *pvt = static_cast<ChannelRPCPyPvt *>(pvoid);
    RPCClientPtr const & channelRPC = pvt->getChannelRPC();
    try {
        PyAllowThreads x;
        pvt->pvResponse = channelRPC->waitResponse(timeout);
    } catch (epics::pvAccess::RPCRequestException & e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    } catch (std::runtime_error & e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return NULL;
    }

    if(pvt->pvResponse.get()==0) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    PyObject *pyObject = PyCapsule_New(&pvt->pvResponse,"pvStructure",0);
    return pyObject;
}

static char _initDoc[] = "_init channelRPCPy.";
static char _destroyDoc[] = "_destroy channelRPCPy.";
static char _connectDoc[] = "_connect.";
static char _issueConnectDoc[] = "_issueConnect.";
static char _waitConnectDoc[] = "_waitConnect(timeout).";
static char _requestDoc[] = "_request.";
static char _issueRequestDoc[] = "_issueRequest.";
static char _waitResponseDoc[] = "_waitResponse.";

static PyMethodDef methods[] = {
    {"_init",_init,METH_VARARGS,_initDoc},
    {"_destroy",_destroy,METH_VARARGS,_destroyDoc},
    {"_connect",_connect,METH_VARARGS,_connectDoc},
    {"_issueConnect",_issueConnect,METH_VARARGS,_issueConnectDoc},
    {"_waitConnect",_waitConnect,METH_VARARGS,_waitConnectDoc},
    {"_request",_request,METH_VARARGS,_requestDoc},
    {"_issueRequest",_issueRequest,METH_VARARGS,_issueRequestDoc},
    {"_waitResponse",_waitResponse,METH_VARARGS,_waitResponseDoc},
    {NULL,NULL,0,NULL}
};

PyMODINIT_FUNC initchannelRPCPy(void)
{
    PyObject * m = Py_InitModule("channelRPCPy",methods);
    if(m==NULL) printf("initchannelRPCPy failed\n");
}

}}
