TOP = ../..
include $(TOP)/configure/CONFIG

USR_INCLUDES += -I${PYTHON_BASE}/include/${PYTHON}

LIBSRCS += alarmPy.cpp
LIBSRCS += timeStampPy.cpp
LIBSRCS += channelRPCPy.cpp
LIBSRCS += ntnameValuePy.cpp
LIBSRCS += nttablePy.cpp
LIBSRCS += gatherV3DataPy.cpp

LIBRARY = masarPy

masarPy_LIBS += gather nt pvIOC pvAccess pvData Com

include $(TOP)/configure/RULES

