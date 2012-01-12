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

#include <pv/ezchannelRPC.h>
#include <stdexcept>

using namespace epics::pvData;

namespace epics { namespace pvAccess {

class ChannelRPCPyPvt {
public:
    ChannelRPCPyPvt(const char *channelName);
    ChannelRPCPyPvt(
        const char *channelName,
        PVStructure::shared_pointer pvRequest);
    ~ChannelRPCPyPvt();
    void destroy();
    EZChannelRPC::shared_pointer const & getChannelRPC(){
        return channelRPC;
    }
    PVStructure::shared_pointer pvResponse;
private:
    EZChannelRPC::shared_pointer channelRPC;
};

ChannelRPCPyPvt::ChannelRPCPyPvt(
    const char *channelName)
: channelRPC(new EZChannelRPC(channelName))
{
}

ChannelRPCPyPvt::ChannelRPCPyPvt(
    const char *channelName,
    PVStructure::shared_pointer pvRequest)
: channelRPC(new EZChannelRPC(channelName,pvRequest))
{
}

ChannelRPCPyPvt::~ChannelRPCPyPvt()
{
}

void ChannelRPCPyPvt::destroy()
{
//printf("ChannelRPCPyPvt::destroy\n");
   channelRPC->destroy();
   channelRPC.reset();
}

static PyObject * _init1(PyObject *willBeNull, PyObject *args)
{
    PyObject *self = 0;
    const char *serverName = 0;
    if(!PyArg_ParseTuple(args,"Os:channelRPCPy",
        &self,
        &serverName))
    {
        return NULL;
    }
    ChannelRPCPyPvt *pvt = new ChannelRPCPyPvt(serverName);
    PyObject *pyObject = PyCapsule_New(pvt,"channelRPCPyPvt",0);
    return pyObject;
}

static PyObject * _init2(PyObject *willBeNull, PyObject *args)
{
    PyObject *self = 0;
    const char *serverName = 0;
    const char *request = 0;
    if(!PyArg_ParseTuple(args,"Oss:channelRPCPy",
        &self,
        &serverName,
        &request))
    {
        return NULL;
    }
    CreateRequest::shared_pointer createRequest = getCreateRequest();
    PVStructure::shared_pointer pvRequest =
         createRequest->createRequest(request);

    ChannelRPCPyPvt *pvt = new ChannelRPCPyPvt(serverName,pvRequest);
    PyObject *pyObject = PyCapsule_New(pvt,"channelRPCPyPvt",0);
    return pyObject;
}

static PyObject * _destroy(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:channelRPCPy",
        &pcapsule))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"channelRPCPyPvt");
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
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"channelRPCPyPvt");
    ChannelRPCPyPvt *pvt = static_cast<ChannelRPCPyPvt *>(pvoid);
    EZChannelRPC::shared_pointer const & channelRPC = pvt->getChannelRPC();
    bool result = false;
    Py_BEGIN_ALLOW_THREADS
        result = channelRPC->connect(timeout);
    Py_END_ALLOW_THREADS
    if(result) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    return NULL;
}

static PyObject * _issueConnect(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:channelRPCPy",
        &pcapsule))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"channelRPCPyPvt");
    ChannelRPCPyPvt *pvt = static_cast<ChannelRPCPyPvt *>(pvoid);
    EZChannelRPC::shared_pointer const & channelRPC = pvt->getChannelRPC();
    Py_BEGIN_ALLOW_THREADS
        channelRPC->issueConnect();
    Py_END_ALLOW_THREADS
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
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"channelRPCPyPvt");
    ChannelRPCPyPvt *pvt = static_cast<ChannelRPCPyPvt *>(pvoid);
    EZChannelRPC::shared_pointer const & channelRPC = pvt->getChannelRPC();
    bool result = false;
    Py_BEGIN_ALLOW_THREADS
        result = channelRPC->waitConnect(timeout);
    Py_END_ALLOW_THREADS
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
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"channelRPCPyPvt");
    ChannelRPCPyPvt *pvt = static_cast<ChannelRPCPyPvt *>(pvoid);
    EZChannelRPC::shared_pointer const & channelRPC = pvt->getChannelRPC();
    pvoid = PyCapsule_GetPointer(pargument,"pvStructure");
    PVStructure::shared_pointer *pvStructure =
        static_cast<PVStructure::shared_pointer *>(pvoid);
    bool last = (lastRequest==0) ? false : true ;
    Py_BEGIN_ALLOW_THREADS
        pvt->pvResponse = channelRPC->request(*pvStructure,last);
    Py_END_ALLOW_THREADS
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
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"channelRPCPyPvt");
    ChannelRPCPyPvt *pvt = static_cast<ChannelRPCPyPvt *>(pvoid);
    EZChannelRPC::shared_pointer const & channelRPC = pvt->getChannelRPC();
    pvoid = PyCapsule_GetPointer(pargument,"pvStructure");
    PVStructure::shared_pointer *pvStructure =
        static_cast<PVStructure::shared_pointer *>(pvoid);
    bool last = (lastRequest==0) ? false : true ;
    Py_BEGIN_ALLOW_THREADS
        channelRPC->issueRequest(*pvStructure,last);
    Py_END_ALLOW_THREADS
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject * _waitRequest(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:channelRPCPy",
        &pcapsule))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"channelRPCPyPvt");
    ChannelRPCPyPvt *pvt = static_cast<ChannelRPCPyPvt *>(pvoid);
    EZChannelRPC::shared_pointer const & channelRPC = pvt->getChannelRPC();
    Py_BEGIN_ALLOW_THREADS
        pvt->pvResponse = channelRPC->waitRequest();
    Py_END_ALLOW_THREADS
    if(pvt->pvResponse.get()==0) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    PyObject *pyObject = PyCapsule_New(&pvt->pvResponse,"pvStructure",0);
    return pyObject;
}

static PyObject * _getMessage(PyObject *willBeNull, PyObject *args)
{
    PyObject *pcapsule = 0;
    if(!PyArg_ParseTuple(args,"O:channelRPCPy",
        &pcapsule))
    {
        return NULL;
    }
    void *pvoid = PyCapsule_GetPointer(pcapsule,"channelRPCPyPvt");
    ChannelRPCPyPvt *pvt = static_cast<ChannelRPCPyPvt *>(pvoid);
    EZChannelRPC::shared_pointer const & channelRPC = pvt->getChannelRPC();
    String message;
    Py_BEGIN_ALLOW_THREADS
        message = channelRPC->getMessage();
    Py_END_ALLOW_THREADS
    PyObject *pyObject = Py_BuildValue("s",message.c_str());
    return pyObject;
}

static char _init1Doc[] = "_init1 channelRPCPy.";
static char _init2Doc[] = "_init2 channelRPCPy.";
static char _destroyDoc[] = "_destroy channelRPCPy.";
static char _connectDoc[] = "_connect.";
static char _issueConnectDoc[] = "_issueConnect.";
static char _waitConnectDoc[] = "_waitConnect(timeout).";
static char _requestDoc[] = "_request.";
static char _issueRequestDoc[] = "_issueRequest.";
static char _waitRequestDoc[] = "_waitRequest.";
static char _getMessageDoc[] = "_getMessage.";

static PyMethodDef methods[] = {
    {"_init1",_init1,METH_VARARGS,_init1Doc},
    {"_init2",_init2,METH_VARARGS,_init2Doc},
    {"_destroy",_destroy,METH_VARARGS,_destroyDoc},
    {"_connect",_connect,METH_VARARGS,_connectDoc},
    {"_issueConnect",_issueConnect,METH_VARARGS,_issueConnectDoc},
    {"_waitConnect",_waitConnect,METH_VARARGS,_waitConnectDoc},
    {"_request",_request,METH_VARARGS,_requestDoc},
    {"_issueRequest",_issueRequest,METH_VARARGS,_issueRequestDoc},
    {"_waitRequest",_waitRequest,METH_VARARGS,_waitRequestDoc},
    {"_getMessage",_getMessage,METH_VARARGS,_getMessageDoc},
    {NULL,NULL,0,NULL}
};

PyMODINIT_FUNC initchannelRPCPy(void)
{
    PyObject * m = Py_InitModule("channelRPCPy",methods);
    if(m==NULL) printf("initchannelRPCPy failed\n");
}

}}
