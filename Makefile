.PHONY: up down migrate seed ingest chat test fmt logs

up:
	docker compose up -d
	@echo "Postgres : localhost:5432 — Mock API : http://localhost:8001/docs"

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	uv run alembic upgrade head

ingest: (à faire avant de lancer seed)
	uv run python -m collect.sessions
	uv run python -m collect.feedbacks

seed:
	uv run python seed.py



chat:
	uv run python scripts/chat.py

test:
	uv run pytest -v

fmt:
	uv run ruff format . || true
