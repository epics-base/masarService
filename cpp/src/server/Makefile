TOP = ../..
include $(TOP)/configure/CONFIG

USR_INCLUDES += -I${PYTHON_BASE}/include/${PYTHON}

INC += dsl.h

LIBRARY = masarServer

SERVER = $(TOP)/src/server/

SRC_DIRS += $(SERVER)/service
INC += masarService.h
LIBSRCS += masarService.cpp
LIBSRCS += masarServiceMain.cpp

SRC_DIRS += $(SERVER)/dslPY
INC += dslPY.h
LIBSRCS += dslPY.cpp

masarService_LIBS += Com pvData pvAccess pvIOC nt
masarService_LIBS += $(PYTHON)

PROD_HOST += masarServiceRun
masarServiceRun_OBJS += masarServiceMain
masarServiceRun_LIBS += nt pvIOC pvAccess pvData Com masarServer
masarServiceRun_LIBS += $(PYTHON)

$(PYTHON)_DIR = $(PYTHON_BASE)/lib/$(PYTHON)/config

include $(TOP)/configure/RULES

