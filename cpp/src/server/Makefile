TOP = ../..
include $(TOP)/configure/CONFIG

USR_INCLUDES += -I${PYTHON_BASE}/include/${PYTHON}

INC += dsl.h

LIBRARY = masarService

SERVER = $(TOP)/src/server/

SRC_DIRS += $(SERVER)/service
INC += masarService.h
LIBSRCS += masarService.cpp
LIBSRCS += masarServiceMain.cpp

SRC_DIRS += $(SERVER)/dslPYIRMIS
INC += dslPYIRMIS.h
LIBSRCS += dslPYIRMIS.cpp

maserService_LIBS += Com pvData pvAccess pvIOC nt
maserService_LIBS += $(PYTHON)

PROD_HOST += masarServiceRun
masarServiceRun_OBJS += masarServiceMain
masarServiceRun_LIBS += nt pvIOC pvAccess pvData Com masarService
masarServiceRun_LIBS += $(PYTHON)

$(PYTHON)_DIR = $(PYTHON_BASE)/lib/$(PYTHON)/config

include $(TOP)/configure/RULES

