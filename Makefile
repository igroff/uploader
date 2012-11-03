.PHONY: clean start test debug setup

debug: setup
	@echo "starting in debug mode"
	@pyserver/bin/debug-server

.pyenv:
	virtualenv -p python2.7 .pyenv
	source .pyenv/bin/activate && pip install -r pyserver/etc/frozen

var/logs: 
	mkdir -p var/logs

setup: var/logs .pyenv
	echo "setup"
	
start: setup 
	@echo "starting application"
	@pyserver/bin/server start

test: setup
	source .pyenv/bin/activate && nosetests	

clean:
	- @rm -rf .pyenv
	- @rm -rf var


