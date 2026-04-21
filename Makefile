.PHONY: install test lint format clean run

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

lint:
	ruff check .

format:
	black .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf data/

run:
	python -m workflows.main

dev:
	python -m workflows.main --debug
