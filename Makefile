SHELL=/bin/bash

.PHONY: clean start test debug setup freeze docs show_config git_hooks crontab


SOURCE_ENV=pythonbrew venv use .pyenv
$(if $(shell which pythonbrew), $(info found me some brew), $(error OH SHIT, NO BREW))

debug: .pyenv
	@pyserver/bin/server debug

.pyenv:
	pythonbrew venv create --no-site-packages .pyenv
	${SOURCE_ENV} && pip install -r pyserver/etc/frozen
	-mkdir tmp
	${SOURCE_ENV} && cd tmp/ && curl -O http://public.intimidatingbits.com/birkenfeld-sphinx-contrib-f60d4a35adab.zip
	${SOURCE_ENV} && cd tmp/ && unzip birkenfeld-sphinx-contrib-f60d4a35adab.zip
	${SOURCE_ENV} && cd tmp/birkenfeld-sphinx-contrib-f60d4a35adab/httpdomain && python setup.py build
	${SOURCE_ENV} && cd tmp/birkenfeld-sphinx-contrib-f60d4a35adab/httpdomain && python setup.py install
	cd tmp/ && curl -O http://public.intimidatingbits.com/apsw-3.7.14.1-r1.zip
	cd tmp/ && unzip apsw-3.7.14.1-r1.zip
	${SOURCE_ENV} && cd tmp/apsw-3.7.14.1-r1 && python setup.py fetch --all --missing-checksum-ok build --enable-all-extensions install
	-rm -rf tmp/
	touch .pyenv

var/logs: 
	mkdir -p var/logs

.doc_build:
	mkdir -p .doc_build/text
	mkdir -p .doc_build/doctrees

setup: var/logs
	
start: setup 
	@exec pyserver/bin/server start

test: .pyenv
	@-rm -rf ./cache/
	@-find . -name '*.pyc' | xargs rm
ifdef TESTS
	@export ROOT_STORAGE_PATH=./output && nosetests -v -s --tests ${TESTS}
else
	@export ROOT_STORAGE_PATH=./output && nosetests -v -s
endif

show_config:
	@pyserver/bin/server config

freeze: .pyenv
	${SOURCE_ENV} && pip freeze

docs: .doc_build .pyenv
	rm -rf .doc_build/text/*
	rm -rf .doc_build/doctrees/*
	${SOURCE_ENV} && sphinx-build -n -b text -d .doc_build/doctrees documentation .doc_build/text
	cp .doc_build/text/index.txt README

clean: setup
	- @rm -rf var/
	- @rm -rf tmp/
	@rm .pyenv
	@ pythonbrew venv delete .pyenv

git_hooks:
	@cp pyserver/etc/git_hooks/* .git/hooks

crontab:
	@if [ -f ./crontab ]; then cat ./crontab | crontab; fi

# allows for projects using this framework to extend the Makefile
-include Makefile.child

