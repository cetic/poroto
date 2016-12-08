GIT_VERSION:=$(shell git describe)
DIST=dist-$(GIT_VERSION)

DEMOS=vector_add vector_add_func vector_add_ip vector_add_reduce vector_avg vector_matrix buffer_sliding const_array brom_array loop_unroll
all:

dist-clean:
	@find . -name '*.pyc' -exec rm -f {} \;
	@for demo in $$(ls demo); do $(MAKE) -C demo/$$demo clean; done

dist:
	@echo "Creating archive for $(GIT_VERSION)..."
	-rm -rf $(DIST)
	-r -f $(GIT_VERSION).zip
	mkdir -p $(DIST)
	cp *.py LICENSE *.sh $(DIST)/
	mkdir -p $(DIST)/pycparser
	cp pycparser/*.py $(DIST)/pycparser
	cp pycparser/*.cfg $(DIST)/pycparser
	cp -r demo $(DIST)/
	cd $(DIST) && zip -r ../$(GIT_VERSION).zip .
	rm -rf $(DIST)

test:
	set -e; for demo in $(DEMOS); do $(MAKE) -C demo/$$demo TARGET=ghdl reset clean gen compile run; done
	@echo All tests successful

release:
	git clean -f
	git pull --squash -Xtheirs ../polca-toolchain
	git reset
	rm -rf vhdl/alphadata/ poroto/alphadata/ c/alphadata/
	git add .
