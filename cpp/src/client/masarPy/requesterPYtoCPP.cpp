/* requesterPytoCpp.cpp */
/*
 *Copyright - See the COPYRIGHT that is included with this distribution.
 *EPICS pvServiceCPP is distributed subject to a Software License Agreement found
 *in file LICENSE that is included with this distribution.
 */
/* Author:  Marty Kraimer Date: 2011.07 */

#include "requesterPy.h"
#include <stdexcept>

namespace epics { namespace masar {

using namespace epics::pvData;

RequesterPy::RequesterPy(
    PyObject *requesterPy
)
: requesterPy(requesterPy)
{
//printf("RequesterPy::RequesterPy\n");
    Py_XINCREF(requesterPy);
    char *methodName = const_cast<char *>("getRequesterName");
    PyObject *namePy = PyObject_CallMethod(requesterPy,methodName,NULL);
    if(namePy==NULL) {
        throw std::invalid_argument("getRequesterName invalid");
    }
    char *name = PyString_AsString(namePy);
    requesterName = String(name);
    Py_DECREF(namePy);
}

RequesterPy::~RequesterPy()
{
//printf("RequesterPy::~RequesterPy\n");
    Py_XDECREF(requesterPy);
}

String RequesterPy::getRequesterName()
{
    return requesterName;
}

void RequesterPy::message(String message,MessageType messageType)
{
    static char *methodName = const_cast<char *>("message");
    static char * sh = const_cast<char *>("sh");
    char *mess= const_cast<char *>(message.c_str());
    PyGILState_STATE gstate = PyGILState_Ensure();
        PyObject * result =
            PyObject_CallMethod(requesterPy,methodName,sh,
                mess,(short)messageType);
        if(result==NULL) {
            throw std::invalid_argument("call Requester.message failed");
        }
        Py_XDECREF(result);
    PyGILState_Release(gstate);
}

void RequesterPy::monitorEvent()
{
    static char *methodName = const_cast<char *>("monitorEvent");
    PyGILState_STATE gstate = PyGILState_Ensure();
        PyObject * result =
            PyObject_CallMethod(requesterPy,methodName,NULL);
        if(result==NULL) {
            throw std::invalid_argument("call Requester.message failed");
        }
        Py_XDECREF(result);
    PyGILState_Release(gstate);
}

}}
