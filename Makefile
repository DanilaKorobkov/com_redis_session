PROJECT := com_redis_session
VERSION := $(shell git describe --tags `git rev-list --tags --max-count=1`)

VENV := .venv

REPORTS := .reports
COVERAGE := $(REPORTS)/coverage

SOURCES := $(PROJECT)
TESTS := tests

PY_FILES := $(shell find $(SOURCES) $(TESTS) -name "*.py")

SSH_KEY_PATH := $(HOME)/.ssh/id_rsa

clean:
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf $(REPORTS)
	rm -rf $(VENV)

$(VENV):
	poetry install --no-root

$(REPORTS):
	mkdir $(REPORTS)

setup: $(VENV) $(REPORTS)

flake8: setup
	poetry run flake8 $(SOURCES) $(TESTS)

mypy: setup
	poetry run mypy $(SOURCES) $(TESTS)

bandit: setup
	poetry run bandit -qr $(SOURCES) $(TESTS) -c .bandit.yml -o $(REPORTS)/bandit.json

pylint: setup
	poetry run pylint $(SOURCES) $(TESTS) > $(REPORTS)/pylint.txt

isort: setup
	poetry run isort $(SOURCES) $(TESTS)

isort-lint: setup
	poetry run isort -c $(SOURCES) $(TESTS)

trailing-comma: setup
	poetry run add-trailing-comma $(PY_FILES) --py36-plus --exit-zero-even-if-changed

trailing-comma-lint: setup
	poetry run add-trailing-comma $(PY_FILES) --py36-plus

auto-pep: setup
	poetry run autopep8 -air $(SOURCES) $(TESTS)

test: setup
	poetry run pytest --cov=$(PROJECT)

format: isort trailing-comma auto-pep

lint: flake8 mypy bandit pylint isort-lint trailing-comma-lint

all: format lint test

.DEFAULT_GOAL := all
