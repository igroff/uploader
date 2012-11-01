.PHONY: clean start test

pyenv:
	virtualenv -p python2.7 pyenv

dirs:
	mkdir -p var/logs

setup: dirs pyenv
	echo "setup"
	
start: setup
	echo "starting application"

test: setup
	echo "running tests"
	
	

clean:
	- @rm -rf pyenv
	- @rm -rf var


