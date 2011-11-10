TOP = ../..
include $(TOP)/configure/CONFIG

USR_INCLUDES += -I${PYTHON_BASE}/include/${PYTHON}

INC += dsl.h

CLIENT = $(TOP)/src/serverCPP/

SRC_DIRS += $(CLIENT)/scc
#INC += xxx.h
#LIBSRCS += maserPy.cpp

SRC_DIRS += $(CLIENT)/service
#INC += xxx.h
#LIBSRCS += maserPy.cpp


LIBRARY = maserServiceServer

maserPython_LIBS += pvAccess pvData Com

include $(TOP)/configure/RULES

