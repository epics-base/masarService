#Makefile at top of application tree
TOP = .
include $(TOP)/configure/CONFIG

DIRS += configure

DIRS += cpp
cpp_DEPEND_DIRS = configure
DIRS += python
python_DEPEND_DIRS = configure
DIRS += test/cpp
test/cpp_DEPEND_DIRS = configure cpp

include $(TOP)/configure/RULES_TOP

UNINSTALL_DIRS += $(INSTALL_LOCATION)/python$(PY_VER)
