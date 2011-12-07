TOP = ../..
include $(TOP)/configure/CONFIG

USR_INCLUDES += -I${PYTHON_BASE}/include/${PYTHON}

DSLPY = $(TOP)/src/dslPY

SRC_DIRS += $(DSLPY)/dsl
LIBSRCS += dsl.cpp

LIBRARY = dslPY

dslPY_LIBS += pvData Com

dslPY_LIBS += $(PYTHON)
# Location of the python libraries
$(PYTHON)_DIR = $(PYTHON_BASE)/lib/$(PYTHON)/config

include $(TOP)/configure/RULES

