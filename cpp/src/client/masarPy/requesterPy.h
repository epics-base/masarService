/* requesterPy.h */
/*
 * Copyright - See the COPYRIGHT that is included with this distribution.
 * EPICS pvServiceCPP is distributed subject to a Software License Agreement found
 * in file LICENSE that is included with this distribution.
 */
/* Author:  Marty Kraimer Date: 2011.07 */
#ifndef REQUESTERPY_H
#define REQUESTERPY_H

#undef _POSIX_C_SOURCE
#undef _XOPEN_SOURCE
#include <Python.h>
#include <numpy/arrayobject.h>

#include <cstddef>
#include <cstdlib>
#include <cstddef>
#include <string>
#include <cstdio>

namespace epics { namespace masar {

class RequesterPy :
    public epics::pvService::GatherMonitorRequester,
    public std::tr1::enable_shared_from_this<RequesterPy>
{
public:
    POINTER_DEFINITIONS(RequesterPy);
    RequesterPy(
        PyObject *requesterPy);
    virtual ~RequesterPy();
    virtual epics::pvData::String getRequesterName();
    virtual void message(
        epics::pvData::String message,
        epics::pvData::MessageType messageType);
    virtual void monitorEvent();
private:
    RequesterPy::shared_pointer getPtrSelf()
    {
        return shared_from_this();
    }
    PyObject *requesterPy;
    epics::pvData::String requesterName;
};

}}

#endif  /* REQUESTERPY_H */
