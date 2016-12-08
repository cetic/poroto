# vhdl files
FILES = $(VHDL_FILES) src/ROCCChelper.vhdl %%%GEN_FILES%%%
PACKAGES?=
WITH_UNISIM?=%%%UNISIM%%%

ifeq ($(WITH_UNISIM),1)
UNISIMS?=$(POROTO_ROOT)/vhdl/unisims
UNISIM=$(UNISIMS)/unisim_VCOMP.vhd $(UNISIMS)/unisim_VPKG.vhd $(UNISIMS)/primitive/FIFO18E1.vhd
PACKAGES+= -Punisim
endif

# testbench
SIMTOP = poroto_tb
SIMFILES =
# Simu break condition
GHDL_SIM_OPT    = --assert-level=error
TIMEOUT?=500ns
ifneq ($(TIMEOUT),)
GHDL_SIM_OPT+=--stop-time=$(TIMEOUT)
endif

SIMDIR = simu

GHDL_CMD        = ghdl
GHDL_FLAGS      = --ieee=synopsys --warn-no-vital-generic -fexplicit --std=93c

VIEW_CMD        = gtkwave

compile:
	mkdir -p simu
	$(GHDL_CMD) -i $(GHDL_FLAGS) --workdir=simu --work=work $(SIMFILES) $(FILES)
ifeq ($(WITH_UNISIM),1)
	mkdir -p unisim
	$(GHDL_CMD) -i $(GHDL_FLAGS) --workdir=unisim --work=unisim $(UNISIM)
endif
	$(GHDL_CMD) -m $(PACKAGES) $(GHDL_FLAGS) --workdir=simu $(SIMTOP)
	@mv $(SIMTOP) simu/$(SIMTOP)

run:
	$(SIMDIR)/$(SIMTOP) $(GHDL_SIM_OPT) --vcdgz=$(SIMDIR)/$(SIMTOP).vcdgz --wave=$(SIMDIR)/$(SIMTOP).ghw

view:
	$(VIEW_CMD) $(SIMDIR)/$(SIMTOP).ghw

view-vcd:
	gunzip --stdout $(SIMDIR)/$(SIMTOP).vcdgz | $(VIEW_CMD) --vcd

clean:
	$(GHDL_CMD) --clean --workdir=simu
	$(GHDL_CMD) --clean --workdir=unisim
	