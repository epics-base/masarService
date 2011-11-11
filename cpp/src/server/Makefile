TOP = ../..
include $(TOP)/configure/CONFIG

USR_INCLUDES += -I${PYTHON_BASE}/include/${PYTHON}

INC += dsl.h

SERVER = $(TOP)/src/server/

SRC_DIRS += $(SERVER)/scc
#INC += xxx.h
#LIBSRCS += xxx.cpp

SRC_DIRS += $(SERVER)/service
#INC += xxx.h
#LIBSRCS +=  xxx.cpp


LIBRARY = maserServiceServer

maserPython_LIBS += pvAccess pvData Com

include $(TOP)/configure/RULES

