TOP=../../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE

#=============================
# Build the IOC support library


exampleSupport_LIBS += $(EPICS_BASE_IOC_LIBS)

#=============================
# Build the IOC application

PROD_IOC = example
# example.dbd will be created and installed
DBD += example.dbd

# example.dbd will be made up from these files:
example_DBD += base.dbd
example_DBD += exampleInclude.dbd


# example_registerRecordDeviceDriver.cpp derives from example.dbd
example_SRCS += example_registerRecordDeviceDriver.cpp

# Build the main IOC entry point on workstation OSs.
example_SRCS_DEFAULT += exampleMain.cpp
example_SRCS_vxWorks += -nil-

# Add support from base/src/vxWorks if needed
#example_OBJS_vxWorks += $(EPICS_BASE_BIN)/vxComLibrary

# Link in the code from the support library

# NOTE: To build SNL programs, SNCSEQ must be defined
# in the <top>/configure/RELEASE file


# Finally link to the EPICS Base libraries
example_LIBS += $(EPICS_BASE_IOC_LIBS)

#=============================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

