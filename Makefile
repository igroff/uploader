SHELL=/usr/bin/env bash
.PHONY: start stop deploy clean test

virtual_env:
	@virtualenv --no-site-packages --python=python2.7 virtual_env
	@source virtual_env/bin/activate && pip install -r freezer.pip

start: virtual_env
	@supervisord --configuration supervisord.conf

debug: virtual_env
	@source virtual_env/bin/activate && gunicorn --access-logfile log/access.log -w 1 -b 127.0.0.1:5000 server:app

stop:
	@for pid in `ps -ef | grep '$(CURDIR)/server.py' | grep -v grep | awk '{ print($$2) }'`; do kill $$pid; done

deploy:
	fab deploy:name=uploader --host ${HOST}

deploy_vagrant:
	fab vagrant_deploy:name=uploader

test: virtual_env
	source virtual_env/bin/activate && ./server.py test

clean:
	@rm -rf virtual_env
