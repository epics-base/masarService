TOP = ../..
include $(TOP)/configure/CONFIG

USR_INCLUDES += -I${PYTHON_BASE}/include/${PYTHON}

CLIENT = $(TOP)/src/client/

SRC_DIRS += $(CLIENT)/masarPy
INC += masarPy.h  
INC += requesterPy.h
#LIBSRCS += requesterPYtoCPP.cpp
#LIBSRCS += masarPy.cpp

#SRC_DIRS += $(CLIENT)/masarPVA
#INC += xxx.h
#LIBSRCS += masarPVA.cpp

SRC_DIRS += $(CLIENT)gatherV3Double
INC += gatherV3Double.h
LIBSRCS += gatherV3Double.cpp


LIBRARY = masarClient

masarServiceClient_LIBS += pvAccess pvData Com

include $(TOP)/configure/RULES

