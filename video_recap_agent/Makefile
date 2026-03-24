.PHONY: up down dev restart logs migrate migration test test-cov shell

# --- Docker ---
up:
	docker compose up -d

down:
	docker compose down

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

restart:
	docker compose restart

logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-worker:
	docker compose logs -f worker

# --- Database ---
migrate:
	docker compose exec backend alembic upgrade head

migration:
	docker compose exec backend alembic revision --autogenerate -m "$(msg)"

# --- Testing ---
test:
	docker compose exec backend pytest tests/ -v

test-cov:
	docker compose exec backend pytest tests/ -v --cov=app --cov-report=term-missing

# --- Shell ---
shell:
	docker compose exec backend bash

shell-db:
	docker compose exec postgres psql -U postgres video_recap

# --- Utilities ---
build:
	docker compose build

clean:
	docker compose down -v --remove-orphans
