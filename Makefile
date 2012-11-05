.PHONY: clean start test debug setup freeze

debug: setup
	@pyserver/bin/server debug

.pyenv:
	virtualenv -p python2.7 .pyenv
	source .pyenv/bin/activate && pip install -r pyserver/etc/frozen

var/logs: 
	mkdir -p var/logs

setup: var/logs .pyenv
	echo "setup"
	
start: setup 
	@pyserver/bin/server start

test: setup
	@pyserver/bin/server test

freeze: setup
	source .pyenv/bin/activate && pip freeze

clean:
	- @rm -rf .pyenv
	- @rm -rf var


