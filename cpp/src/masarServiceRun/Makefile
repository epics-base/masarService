TOP = ../../..
include $(TOP)/configure/CONFIG
include $(TOP)/configure/CONFIG_PY
USR_INCLUDES += -I${PYTHON_BASE}/include/${PYTHON}


PROD_HOST += masarServiceRun
masarServiceRun_SRCS += masarServiceRun.cpp
masarServiceRun_LIBS += masarServer gather nt pvAccess pvData Com
masarServiceRun_SYS_LIBS += python$(PY_LD_VER)

# Needed on RHEL/CentOS
USR_SYS_LIBS += util

include $(TOP)/configure/RULES

