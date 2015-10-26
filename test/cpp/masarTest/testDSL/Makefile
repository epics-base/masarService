TOP=../..

include $(TOP)/configure/CONFIG


PROD_HOST += testDSLGetLiveMachine
testDSLGetLiveMachine_SRCS += testDSLGetLiveMachine.cpp
testDSLGetLiveMachine_LIBS += gather nt pvAccess pvData Com
testDSLGetLiveMachine_LIBS += masarPy masarServer
testDSLGetLiveMachine_LIBS += $(PYTHON)

PROD_HOST += testDSLRetrieveSnapshot
testDSLRetrieveSnapshot_SRCS += testDSLRetrieveSnapshot.cpp
testDSLRetrieveSnapshot_LIBS += gather nt pvAccess pvData Com
testDSLRetrieveSnapshot_LIBS += masarPy masarServer
testDSLRetrieveSnapshot_LIBS += $(PYTHON)

PROD_HOST += testDSLRetrieveServiceConfigs
testDSLRetrieveServiceConfigs_SRCS += testDSLRetrieveServiceConfigs.cpp
testDSLRetrieveServiceConfigs_LIBS += gather nt pvAccess pvData Com
testDSLRetrieveServiceConfigs_LIBS += masarPy masarServer
testDSLRetrieveServiceConfigs_LIBS += $(PYTHON)

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

