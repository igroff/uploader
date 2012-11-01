.PHONY: clean start test

pyenv:
	virtualenv -p python2.7 pyenv
	source pyenv/bin/activate && pip install -r frozen

dirs:
	mkdir -p var/logs

setup: dirs pyenv
	echo "setup"
	
start: setup
	echo "starting application"

test: setup
	source pyenv/bin/activate && nosetests	
	

clean:
	- @rm -rf pyenv
	- @rm -rf var


