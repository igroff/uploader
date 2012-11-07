.PHONY: clean start test debug setup freeze docs

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
	-rm -rf tmp/

var/logs: 
	mkdir -p var/logs

.doc_build:
	mkdir -p .doc_build/text
	mkdir -p .doc_build/doctrees

setup: var/logs .pyenv
	echo "setup"
	
start: setup 
	@pyserver/bin/server start

test: setup
	@pyserver/bin/server test

freeze: setup
	source .pyenv/bin/activate && pip freeze

docs: .doc_build
	rm -rf .doc_build/text/*
	rm -rf .doc_build/doctrees/*
	source .pyenv/bin/activate && sphinx-build -n -b text -d .doc_build/doctrees documentation .doc_build/text

clean:
	- @rm -rf .pyenv
	- @rm -rf var


