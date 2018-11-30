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
	mkdir logs
	touch logs/error.log
	touch logs/access.log
	sudo apt install python3-pip virtualenv
	virtualenv -p python3.7 .env
	source .env/bin/activate
	pip install -r $(REQ_FILE)
	python -m sanic server.app --host=$(host) --port=$(port) --workers=$(workers)
