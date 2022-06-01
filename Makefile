APP := redisolar
PORT := 8081
VALID_PYTHON_FOUND := $(shell command -v python3.8 2> /dev/null)
ifndef VALID_PYTHON_FOUND
    VALID_PYTHON_FOUND := $(shell command -v python3.9 2> /dev/null)
    PYTHON_COMMAND := "python3.9"
else
    PYTHON_COMMAND := "python3.8"
endif
ifndef VALID_PYTHON_FOUND
    VALID_PYTHON_FOUND := $(shell command -v python3.10 2> /dev/null)
    PYTHON_COMMAND := "python3.10"
endif
ifndef VALID_PYTHON_FOUND
    VALID_PYTHON_FOUND := $(shell command -v python3.11 2> /dev/null)
    PYTHON_COMMAND := "python3.11"
endif

ifndef VALID_PYTHON_FOUND
    $(error "Python 3.8-11 is not installed! See README.md")
endif

ifeq (${IS_CI}, true)
	FLAGS := "--ci"
else
	FLAGS := "-s"
endif

.PHONY: mypy test all clean dev load frontend timeseries-docker deps

all: env mypy lint test

env: env/bin/activate

env/bin/activate: requirements.txt
	test -d env || ${PYTHON_COMMAND} -m venv env
	. env/bin/activate; pip install --upgrade pip; pip install pip-tools wheel -e .; pip-sync requirements.txt requirements-dev.txt
	touch env/bin/activate

mypy: env
	. env/bin/activate; mypy --ignore-missing-imports redisolar

test: env
	. env/bin/activate; pytest $(FLAGS)

lint: env
	. env/bin/activate; pylint redisolar

clean:
	rm -rf env
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

dev: env
	. env/bin/activate; FLASK_ENV=development FLASK_APP=$(APP) FLASK_DEBUG=1 flask run --port=$(PORT) --host=0.0.0.0

requirements.txt: requirements.in
	pip-compile requirements.in > requirements.txt

requirements-dev.txt: requirements-dev.in
	pip-compile requirements-dev.in > requirements-dev.txt

deps: requirements-dev.txt requirements.txt

frontend: env
	cd frontend; npm run build
	rm -rf redisolar/static
	cp -r frontend/dist/static redisolar/static
	cp frontend/dist/index.html redisolar/static/

load: env
	. env/bin/activate; FLASK_APP=$(APP) flask load

timeseries-docker:
	docker run -p 6379:6379 -it -d --rm redislabs/redistimeseries

timeseries-podman:
	podman run -p 6379:6379 -it -d --rm redislabs/redistimeseries
