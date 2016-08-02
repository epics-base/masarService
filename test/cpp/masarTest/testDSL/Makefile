TOP=../..

include $(TOP)/configure/CONFIG
include $(MASAR)/configure/CONFIG_PY


PROD_HOST += testDSLGetLiveMachine
testDSLGetLiveMachine_SRCS += testDSLGetLiveMachine.cpp
testDSLGetLiveMachine_LIBS += gather nt pvAccess pvData Com
testDSLGetLiveMachine_LIBS += masarServer
testDSLGetLiveMachine_SYS_LIBS += python$(PY_LD_VER)

PROD_HOST += testDSLRetrieveSnapshot
testDSLRetrieveSnapshot_SRCS += testDSLRetrieveSnapshot.cpp
testDSLRetrieveSnapshot_LIBS += gather nt pvAccess pvData Com
testDSLRetrieveSnapshot_LIBS += masarServer
testDSLRetrieveSnapshot_SYS_LIBS += python$(PY_LD_VER)

PROD_HOST += testDSLRetrieveServiceConfigs
testDSLRetrieveServiceConfigs_SRCS += testDSLRetrieveServiceConfigs.cpp
testDSLRetrieveServiceConfigs_LIBS += gather nt pvAccess pvData Com
testDSLRetrieveServiceConfigs_LIBS += masarServer
testDSLRetrieveServiceConfigs_SYS_LIBS += python$(PY_LD_VER)

# Needed on RHEL/CentOS
USR_SYS_LIBS += util

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

