APP_SERVICE = backend
MIGRATE_CMD = flask db upgrade
SEED_CMD = python3 tools/seed_db.py --file fixtures/seed_users.json --commit

# default command if not specified
all: run

run:
	@echo "Starting development environment..."
	docker compose --env-file .env.dev up --build

down:
	@echo "Stopping development environment..."
	docker compose --env-file .env.dev down

clear:
	@echo "Clearing all containers and volumes..."
	docker compose --env-file .env.dev down -v --rmi all --remove-orphans

view-data:
	@echo "Viewing data in the database..."
	docker compose --env-file .env.dev exec db psql -U postgres -d digital_finance_db

