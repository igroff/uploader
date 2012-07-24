.PHONY: start stop deploy
start:
	@$(CURDIR)/server.py start > server.log 2>&1 &
stop:
	@for pid in `ps -ef | grep '$(CURDIR)/server.py' | grep -v grep | awk '{ print($$2) }'`; do kill $$pid; done
deploy:
	fab deploy:name=uploader --host ${HOST}
