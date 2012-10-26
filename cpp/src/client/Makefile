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

SRC_DIRS += $(CLIENT)/gatherV3Data
INC += gatherV3Data.h
LIBSRCS += gatherV3Data.cpp

#SRC_DIRS += $(CLIENT)ezchannelRPC
#INC += ezchannelRPC.h
#LIBSRCS += ezchannelRPC.cpp

LIBRARY = gather

gather_LIBS += pvAccess pvData ca Com
#masar_LIBS += $(EPICS_BASE_HOST_LIBS)

include $(TOP)/configure/RULES

