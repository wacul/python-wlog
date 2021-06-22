lint:
	flake8 wlog --ignore E501,W503

run-example:
	poetry install
	poetry run python _examples/00*.py
	AIA_LOG_LEVEL=debug AIA_LOG_FORMAT=text poetry run python _examples/00*.py
.PHONY: run-example
