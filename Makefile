.PHONY: clean start test debug setup

debug: setup
	@echo "starting in debug mode"
	@etc/debug-server

.pyenv:
	virtualenv -p python2.7 .pyenv
	source .pyenv/bin/activate && pip install -r frozen

var/logs: 
	mkdir -p var/logs

setup: var/logs .pyenv
	echo "setup"
	
start: setup 
	@echo "starting application"
	@etc/server start

test: setup
	source .pyenv/bin/activate && nosetests	

clean:
	- @rm -rf pyenv
	- @rm -rf var


