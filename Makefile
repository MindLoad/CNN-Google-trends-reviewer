# Initial prepares

LINT_TARGETS := $(shell find . -name '*.py')
LINT_ARGS := $(shell echo -r)

# Bash commands

up:
	docker-compose stop
	docker-compose up

sh:
	docker-compose exec web sh

shell:
	docker-compose exec web python3 manage.py shell_plus

worker:
	docker-compose exec web celery -A cnn worker -l info

beat:
	docker-compose exec web celery -A cnn beat -l info

flower:
	docker-compose exec -it web flower -A cnn --port=5555

lint_pylint:
	@echo '[PYLINT]'
	pylint --rcfile=.pylintrc *.py cnn/ cnn/cnn cnn/web/

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
