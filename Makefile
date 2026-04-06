.PHONY: help init test lint format typecheck clean build ci-lint

init:
	pip install -e ".[dev]"

test:
	pytest tests/

lint:
	flake8 src/ tests/

format:
	black src/ tests/
	isort src/ tests/

typecheck:
	mypy src/

build:
	python -m build

ci-lint: format lint typecheck build
	twine check dist/*

clean:
	rm -rf src/whenever_django.egg-info/ build/ dist/ .pytest_cache/ .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
