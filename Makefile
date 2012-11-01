.PHONY: clean start test

debug: setup
	echo "starting in debug mode"
	etc/debug-server

pyenv:
	virtualenv -p python2.7 pyenv
	source pyenv/bin/activate && pip install -r frozen

dirs:
	mkdir -p var/logs

setup: dirs pyenv
	echo "setup"
	
start: setup
	echo "starting application"
	etc/server

test: setup
	source pyenv/bin/activate && nosetests	
	

clean:
	- @rm -rf pyenv
	- @rm -rf var


