#Makefile at top of application tree
TOP = ./cpp
include $(TOP)/configure/CONFIG

DIRS += cpp
DIRS += test/cpp

include $(TOP)/configure/RULES_TOP
