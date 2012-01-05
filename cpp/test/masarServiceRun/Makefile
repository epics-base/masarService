TOP = ../..
include $(TOP)/configure/CONFIG
USR_INCLUDES += -I${PYTHON_BASE}/include/${PYTHON}


PROD_HOST += masarServiceRun
masarServiceRun_SRCS += masarServiceRun.cpp
masarServiceRun_LIBS += nt pvIOC pvAccess pvData Com masarServer
masarServiceRun_LIBS += $(PYTHON)

$(PYTHON)_DIR = $(PYTHON_BASE)/lib/$(PYTHON)/config

include $(TOP)/configure/RULES

