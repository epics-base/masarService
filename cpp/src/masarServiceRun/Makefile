TOP = ../..
include $(TOP)/configure/CONFIG
USR_INCLUDES += -I${PYTHON_BASE}/include/${PYTHON}


PROD_HOST += masarServiceRun
masarServiceRun_SRCS += masarServiceRun.cpp
masarServiceRun_LIBS += masarServer gather nt pvIOC pvAccess pvData Com
masarServiceRun_LIBS += $(PYTHON)

# Needed on RHEL/CentOS
USR_SYS_LIBS += util

include $(TOP)/configure/RULES

