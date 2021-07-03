#Makefile at top of application tree
TOP = .
include $(TOP)/configure/CONFIG

DIRS += configure

DIRS += python
python_DEPEND_DIRS = configure

include $(TOP)/configure/RULES_TOP

UNINSTALL_DIRS += $(wildcard $(INSTALL_LOCATION)/python*.*)

nose.%: all
	$(MAKE) -C python/O.$(EPICS_HOST_ARCH) $@ PYTHON=$(PYTHON)
nose.%: all
	$(MAKE) -C python/O.$(EPICS_HOST_ARCH) $@ PYTHON=$(PYTHON)

nose: nose.minimasar

.PHONY: nose
