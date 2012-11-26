SHELL=/bin/bash
.PHONY: clean start test debug setup freeze docs show_config git_hooks crontab


debug: setup
	@pyserver/bin/server debug

.pyenv:
	virtualenv -p python2.7 .pyenv
	source .pyenv/bin/activate && pip install -r pyserver/etc/frozen
	-mkdir tmp
	source .pyenv/bin/activate && cd tmp/ && curl -O http://public.intimidatingbits.com/birkenfeld-sphinx-contrib-f60d4a35adab.zip
	source .pyenv/bin/activate && cd tmp/ && unzip birkenfeld-sphinx-contrib-f60d4a35adab.zip
	source .pyenv/bin/activate && cd tmp/birkenfeld-sphinx-contrib-f60d4a35adab/httpdomain && python setup.py build
	source .pyenv/bin/activate && cd tmp/birkenfeld-sphinx-contrib-f60d4a35adab/httpdomain && python setup.py install
	cd tmp/ && curl -O http://public.intimidatingbits.com/apsw-3.7.14.1-r1.zip
	cd tmp/ && unzip apsw-3.7.14.1-r1.zip
	source .pyenv/bin/activate && cd tmp/apsw-3.7.14.1-r1 && python setup.py build --enable-all-extensions install
	-rm -rf tmp/

var/logs: 
	mkdir -p var/logs

.doc_build:
	mkdir -p .doc_build/text
	mkdir -p .doc_build/doctrees

setup: var/logs .pyenv
	@echo "setup"
	
start: setup 
	@exec pyserver/bin/server start

test: setup
	@find . -name '*.pyc' | xargs rm
	@pyserver/bin/server test

show_config:
	@pyserver/bin/server config

freeze: setup
	source .pyenv/bin/activate && pip freeze

docs: .doc_build .pyenv
	rm -rf .doc_build/text/*
	rm -rf .doc_build/doctrees/*
	source .pyenv/bin/activate && sphinx-build -n -b text -d .doc_build/doctrees documentation .doc_build/text
	cp .doc_build/text/index.txt README

clean:
	- @rm -rf .pyenv
	- @rm -rf var

git_hooks:
	@cp pyserver/etc/git_hooks/* .git/hooks

crontab:
	@if [ -f ./crontab ]; then cat ./crontab | crontab; fi

# allows for projects using this framework to extend the Makefile
-include Makefile.child

