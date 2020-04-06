APP := redisolar
PORT := 8001


ifeq (${IS_CI}, true)
	FLAGS := "--ci"
else
	FLAGS := ""
endif

.PHONY: mypy test all clean dev load frontend

env: env/bin/activate

env/bin/activate: requirements.txt
	test -d env || python3 -m venv env
	. env/bin/activate; pip install wheel; pip install -Ue .
	touch env/bin/activate

mypy: env
	. env/bin/activate; mypy --ignore-missing-imports redisolar

test: env
	. env/bin/activate; pytest $(FLAGS)

lint: env
	. env/bin/activate; pylint redisolar

all: env mypy lint test

clean:
	rm -rf env
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

dev: env
	. env/bin/activate; FLASK_ENV=development FLASK_APP=$(APP) FLASK_DEBUG=1 flask run --port=$(PORT)

frontend: env
	cd frontend; npm run build
	rm -rf redisolar/static
	cp -r frontend/dist/static redisolar/static
	cp frontend/dist/index.html redisolar/static/

load: env
	. env/bin/activate; load_redisolar
