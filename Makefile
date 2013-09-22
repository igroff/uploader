SHELL=/bin/bash
FROZEN_HASH=$(shell openssl md5 pyserver/etc/frozen | sed -e 's[MD5(pyserver/etc/frozen)= [[g')
FROZEN_HASH_FILE=.frozen-hash-${FROZEN_HASH}
PYENV=.${FROZEN_HASH}
PYENV_DIR=~/.pythonbrew/venvs/Python-2.7.2/${PYENV}
with_brew=bash -i -c 'source ~/.pythonbrew/etc/bashrc && $(1)'
with_venv=bash -i -c 'source ~/.pythonbrew/etc/bashrc && pythonbrew venv use $(PYENV) && $(1)'

.PHONY: clean start test debug setup freeze docs show_config git_hooks crontab build

$(if $(shell test -f ~/.pythonbrew/etc/bashrc && echo pants;  ), $(info # found me some brew), $(error # OH SHIT, NO BREW))
debug: ${PYENV_DIR}
	@exec $(call with_venv, exec pyserver/bin/server debug)

${FROZEN_HASH_FILE}:
	$(MAKE) clean
	-@rm .frozen-hash*
	echo "environment was built for this version of the frozen file" > ${FROZEN_HASH_FILE}

${PYENV_DIR}:
	$(call with_brew, pythonbrew venv create ${PYENV})
	$(call with_venv, pip install --no-index --find-links=file://`pwd`/pyserver/packages/ -r pyserver/etc/frozen)
	-mkdir tmp
	$(call with_venv, cp `pwd`/pyserver/packages/birkenfeld-sphinx-contrib-f60d4a35adab.tar.gz ./tmp/)
	$(call with_venv, cd tmp/ && tar zxf birkenfeld-sphinx-contrib-f60d4a35adab.tar.gz)
	$(call with_venv, cd tmp/birkenfeld-sphinx-contrib-f60d4a35adab/httpdomain && python setup.py build)
	$(call with_venv, cd tmp/birkenfeld-sphinx-contrib-f60d4a35adab/httpdomain && python setup.py install)
	cp `pwd`/pyserver/packages/apsw-3.7.14.1-r1.zip tmp/
	cd tmp/ && unzip apsw-3.7.14.1-r1.zip
	cp `pwd`/pyserver/packages/sqlite-autoconf-3071600.tar.gz tmp/
	cd tmp/ && tar xf sqlite-autoconf-3071600.tar.gz && mv sqlite-autoconf-3071600/ apsw-3.7.14.1-r1/sqlite3
	$(call with_venv, cd tmp/apsw-3.7.14.1-r1 && python setup.py build --enable-all-extensions install)
	-rm -rf tmp/
	touch ${PYENV_DIR}

var/logs: 
	mkdir -p var/logs

var/run:
	mkdir -p var/run

.doc_build:
	mkdir -p .doc_build/text
	mkdir -p .doc_build/doctrees

setup: var/logs var/run

build: var/logs ${PYENV_DIR}
	
start: setup ${PYENV_DIR}
	@exec $(call with_venv, exec pyserver/bin/server start)

background: setup ${PYENV_DIR}
	@exec $(call with_venv, exec pyserver/bin/server background)

test: ${PYENV_DIR}
	@-rm -rf ./output
	@-find . -name '*.pyc' | xargs rm
ifdef TESTS
	@$(call with_venv, export ROOT_STORAGE_PATH=./output && nosetests -v -s --tests ${TESTS})
else
	@$(call with_venv, export ROOT_STORAGE_PATH=./output && nosetests -v -s)
endif

show_config:
	@pyserver/bin/server config

freeze: ${PYENV_DIR}
	$(call with_venv, pip freeze)

docs: .doc_build ${PYENV_DIR}
	rm -rf .doc_build/text/*
	rm -rf .doc_build/doctrees/*
	$(call with_venv, sphinx-build -n -b text -d .doc_build/doctrees documentation .doc_build/text)
	cp .doc_build/text/index.txt README

clean: setup
	- @rm -rf tmp/
	- @rm -rf .frozen-hash*
	@ $(call with_brew, pythonbrew venv delete ${PYENV})

git_hooks:
	@cp pyserver/etc/git_hooks/* .git/hooks

crontab:
	@if [ -f ./crontab ]; then cat ./crontab | crontab; fi

# allows for projects using this framework to extend the Makefile
-include Makefile.child

