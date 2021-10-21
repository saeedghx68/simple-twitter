REQ_FILE=requirements.txt

freeze_requirements:
	pip freeze > $(REQ_FILE) 

install_requirements:
	pip install -r $(REQ_FILE)

run:
	python -m sanic server.app --host=$(host) --port=$(port) --workers=$(workers)

test:
	ENVIRONMENT=test pytest unittesting/

all:
	cp .env.tpl .env
	mkdir -p logs
	touch -f logs/error.log
	touch -f logs/access.log
	sudo apt install python3.10 python3.10-dev python3.10-venv
	python3.10 -m venv venv
	./venv/bin/pip install -r $(REQ_FILE)
	./venv/bin/python -m sanic server.app --host=$(host) --port=$(port) --workers=$(workers)
