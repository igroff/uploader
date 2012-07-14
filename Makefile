.PHONY: start stop

start:
	@./server.py start > server.log 2>&1 &

stop:
	@ps -f | grep './server.py' | grep -v grep | awk '{ print($$2) }' | xargs kill
