TOP = ../..
include $(TOP)/configure/CONFIG

USR_INCLUDES += -I${PYTHON_BASE}/include/${PYTHON}

INC += dsl.h

LIBRARY = masarServer

SERVER = $(TOP)/src/server/

SRC_DIRS += $(SERVER)/service
INC += masarService.h
LIBSRCS += masarService.cpp

SRC_DIRS += $(SERVER)/dslPY
INC += dslPY.h
LIBSRCS += dslPY.cpp

masarService_LIBS += gather nt pvIOC pvAccess pvData Com
masarService_LIBS += $(PYTHON)


$(PYTHON)_DIR = $(PYTHON_BASE)/lib/$(PYTHON)/config

include $(TOP)/configure/RULES

