POROTO_ROOT?=.
ROCCC_ROOT?=/opt/roccc-0.7.6-distribution

TARGET?=ghdl
PARAMS?=
HEADER?=
PROJECT?=project
TEST?=test_vectors.py
WITH_UNISIM?=1

include $(POROTO_ROOT)/platforms/$(TARGET)/$(TARGET).mk

SDK?=''
PLATFORM_VENDOR?=''
PLATFORM?=''
PLATFORM_TARGET?=''
DEVICE_VENDOR?=''
DEVICE?=''
DESIGNER?=''
DESIGNER_VERSION?=''

ifeq ($(WITH_UNISIM),1)
PARAMS+= --unisim
endif

CONFIG+=--sdk $(SDK) --platform-vendor $(PLATFORM_VENDOR) --platform $(PLATFORM) --target $(PLATFORM_TARGET) --device-vendor $(DEVICE_VENDOR) --device $(DEVICE) --design-tool $(DESIGNER) --design-version $(DESIGNER_VERSION)

ifneq ($(DEVICE_FAMILY),)
	PARAMS+=--device-family $(DEVICE_FAMILY)
endif

ifneq ($(PACKAGE),)
	PARAMS+=--package $(PACKAGE)
endif

ifneq ($(SPEEDGRADE),)
	PARAMS+=--speed-grade $(SPEEDGRADE)
endif

ifneq ($(TEST),)
	PARAMS+=--tb $(TEST)
endif

export ROCCC_ROOT
export POROTO_ROOT:=$(shell cd $(POROTO_ROOT) && pwd)

export VHDL_FILES
export TIMEOUT

gen:
	if [ ! -e $(PROJECT) ]; then $(POROTO_ROOT)/mkproject.py $(CONFIG) $(PROJECT); fi
	$(POROTO_ROOT)/poroto.py $(PARAMS) --header "$(HEADER)" --keep-temp --debug $(CONFIG) --project $(PROJECT) $(FILES)

reset:
	$(POROTO_ROOT)/scripts/reset_roccc.sh

clean:
	rm -rf gen/
	if [ -e $(PROJECT) ]; then rm -rf $(PROJECT); fi
	
ifneq ($(PROJECT),)
compile:
	$(MAKE) -C $(PROJECT) compile

run:
	$(MAKE) -C $(PROJECT) run

view:
	$(MAKE) -C $(PROJECT) view

else
compile run view:
$(error Project not defined)
endif

.PHONY: gen reset compile run view