.PHONY: help setup install test run db-up db-down migrate migration

help:
	@echo "make setup          Create the virtual environment and install dependencies"
	@echo "make install        Install development dependencies"
	@echo "make test           Run the complete test suite"
	@echo "make run            Start the FastAPI development server"
	@echo "make db-up          Start PostgreSQL"
	@echo "make db-down        Stop PostgreSQL"
	@echo "make migrate        Apply all database migrations"
	@echo "make migration MSG= Create a new Alembic migration"

setup:
	python3 -m venv backend/.venv
	$(MAKE) install

install:
	cd backend && .venv/bin/pip install -r requirements-dev.txt

test:
	cd backend && .venv/bin/pytest -q

run:
	cd backend && .venv/bin/uvicorn src.main:app --reload

db-up:
	docker compose up -d postgres

db-down:
	docker compose down

migrate:
	cd backend && .venv/bin/alembic upgrade head

migration:
	@test -n "$(MSG)" || (echo "Usage: make migration MSG='describe the change'" && exit 1)
	cd backend && .venv/bin/alembic revision --autogenerate -m "$(MSG)"
