SHELL=/usr/bin/env bash
.PHONY: start stop deploy clean test

virtual_env:
	virtualenv --no-site-packages --python=python2.7 virtual_env
	source virtual_env/bin/activate && pip install -r freezer.pip

start: virtual_env
	source virtual_env/bin/activate && $(CURDIR)/server.py start > server.log 2>&1 &

debug: virtual_env
	source virtual_env/bin/activate && $(CURDIR)/server.py start 

stop:
	@for pid in `ps -ef | grep '$(CURDIR)/server.py' | grep -v grep | awk '{ print($$2) }'`; do kill $$pid; done

deploy:
	fab deploy:name=uploader --host ${HOST}

deploy_test:
	fab deploy:name=uploader --host 127.0.0.1 --user vagrant --keyfile 

test: virtual_env
	source virtual_env/bin/activate && ./server.py test

clean:
	@rm -rf virtual_env
