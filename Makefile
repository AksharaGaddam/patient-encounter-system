# Makefile for common tasks (docker targets removed)
.PHONY: migrate test lint format check-coverage run seed

migrate:
	python -m scripts.run_migrations

run:
	uvicorn src.main:app --reload

test:
	pytest

lint:
	ruff check .

format:
	black .

check-coverage:
	pytest --maxfail=1 -q --cov=src --cov-fail-under=80

seed:
	python -m scripts.seed_data
