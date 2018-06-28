SHELL := /bin/bash

venv: requirements.txt
	python3 -m venv venv; \
    ./venv/bin/pip install --timeout 60 -r requirements.txt; \

install: venv
	source venv/bin/activate; \
	pip install --upgrade --force-reinstall .

test:
	PYTHONPATH=.:./deperson/ ./venv/bin/pytest tests/*.py

test/coverage:
	source venv/bin/activate; \
	PYTHONPATH=.:./deperson/ ./venv/bin/pytest --cov=deperson tests/*.py
