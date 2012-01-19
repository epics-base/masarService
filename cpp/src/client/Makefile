TOP = ../..
include $(TOP)/configure/CONFIG

USR_INCLUDES += -I${PYTHON_BASE}/include/${PYTHON}

CLIENT = $(TOP)/src/client/

#SRC_DIRS += $(CLIENT)/masarPy
#INC += masarPy.h  
#INC += requesterPy.h
#LIBSRCS += requesterPYtoCPP.cpp
#LIBSRCS += masarPy.cpp

#SRC_DIRS += $(CLIENT)/masarPVA
#INC += xxx.h
#LIBSRCS += masarPVA.cpp

SRC_DIRS += $(CLIENT)gatherV3ScalarData
INC += gatherV3ScalarData.h
LIBSRCS += gatherV3ScalarData.cpp

SRC_DIRS += $(CLIENT)ezchannelRPC
INC += ezchannelRPC.h
LIBSRCS += ezchannelRPC.cpp

LIBRARY = masarClient

masarClient_LIBS += pvAccess pvData Com
masarClient_LIBS += $(EPICS_BASE_HOST_LIBS)

include $(TOP)/configure/RULES

