TOP = ../..
include $(TOP)/configure/CONFIG
USR_INCLUDES += -I${PYTHON_BASE}/include/${PYTHON}


PROD_HOST += masarServiceRun
masarServiceRun_SRCS += masarServiceRun.cpp
masarServiceRun_LIBS += nt pvIOC pvAccess pvData Com masarServer masarClient
masarServiceRun_LIBS += $(PYTHON)

include $(TOP)/configure/RULES

