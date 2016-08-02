TOP = ../..
include $(TOP)/configure/CONFIG
include $(TOP)/configure/CONFIG_PY

LOADABLE_LIBRARY += alarmPy
alarmPy_SRCS += alarmPy.cpp

LOADABLE_LIBRARY += timeStampPy
timeStampPy_SRCS += timeStampPy.cpp

LOADABLE_LIBRARY += controlPy
controlPy_SRCS += controlPy.cpp

LOADABLE_LIBRARY += displayPy
displayPy_SRCS += displayPy.cpp

LOADABLE_LIBRARY += channelRPCPy
channelRPCPy_SRCS += channelRPCPy.cpp

LOADABLE_LIBRARY += ntnameValuePy
ntnameValuePy_SRCS += ntnameValuePy.cpp

LOADABLE_LIBRARY += nttablePy
nttablePy_SRCS += nttablePy.cpp

LOADABLE_LIBRARY += ntmultiChannelPy
ntmultiChannelPy_SRCS += ntmultiChannelPy.cpp

LOADABLE_LIBRARY += gatherV3DataPy
gatherV3DataPy_SRCS += gatherV3DataPy.cpp

LOADABLE_LIBRARY += ntscalarPy
ntscalarPy_SRCS += ntscalarPy.cpp

LIB_LIBS += gather nt pvAccess pvData Com

include $(TOP)/configure/RULES
include $(TOP)/configure/RULES_PY

