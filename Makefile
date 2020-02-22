# Initial prepares

LINT_TARGETS := $(shell find . -name '*.py')
LINT_ARGS := $(shell echo -r)
CMD_PREFIX := docker exec -it web

# Portainer

portainer:
	docker run --rm -d -p 9000:9000 -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer

# Shell & Debug commands

sh:
	@$(CMD_PREFIX) sh

shell:
	@$(CMD_PREFIX) python manage.py shell_plus

shell_sql:
	@$(CMD_PREFIX) python manage.py shell_plus --print-sql

runserver:
	@$(CMD_PREFIX) python manage.py runserver 0.0.0.0:8000

runserver_plus:
	@$(CMD_PREFIX) python manage.py runserver_plus 0.0.0.0:8000 --print-sql

up:
	docker-compose stop
	docker-compose up -d

start stopstart: %start : %
	@docker-compose up -d

stop:
	docker-compose stop

build:
	docker-compose stop
	docker-compose down
	docker-compose build --force-rm --no-cache --pull

top:
	docker-compose top

# Celery commands

worker_high_queue:
	docker exec -d celery_worker_CNN sh -c "celery worker -A cnn -c 4 -l info -E -n worker.high -Q high"
worker_low_queue:
	docker exec -d celery_worker_CNN sh -c "celery worker -A cnn -c 4 -l info -E -n worker.low -Q low"

beat:
	docker-compose exec web celery beat -A cnn -l info

flower:
	docker-compose exec -it web flower -A cnn --port=5555

# Project initialization

migrate:
	@$(CMD_PREFIX) python manage.py migrate

init-admin:
	@$(CMD_PREFIX) python manage.py shell -c "from django.contrib.auth import get_user_model; USER = get_user_model(); USER.objects.filter(username='admin').exists() or USER.objects.create_superuser(username='admin', password='admin')"

init:
	@$(MAKE) start
	@sleep 120
	@$(MAKE) migrate
	@$(MAKE) init-admin
	@$(MAKE) stopstart

# Requirements and dependencies management

update-requirements:
	@$(CMD_PREFIX) pipenv lock --clear
	@$(CMD_PREFIX) pipenv install -d --system
	@docker exec -i celery_worker_CNN pipenv install -d --system
	@docker exec -i celery_beat_CNN pipenv install -d --system

# Linters & Tests

lint_pylint:
	@echo '[PYLINT]'
	pylint --rcfile=.pylintrc *.py / /cnn /web/

lint_pycodestyle:
	@echo '[PYCODESTYLE]'
	pycodestyle $(LINT_TARGETS) --config=.pycodestyle

lint_safety:
	safety check -r Pipfile

lint_mypy:
	mypy $(LINT_TARGETS)

inspect:
	@echo '[BANDIT]'
	@$(CMD_PREFIX) bandit $(LINT_ARGS) $(LINT_TARGETS)

pytest:
	pytest

check: lint_pycodestyle inspect lint_pylint lint_safety lint_mypy
