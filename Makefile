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

migrate:
	@echo "Running Database Migrations..."
	docker compose --env-file .env.dev exec $(APP_SERVICE) $(MIGRATE_CMD)

seed:
	@echo "Seeding Mock Data..."
	docker compose --env-file .env.dev exec $(APP_SERVICE) $(SEED_CMD)


reset:
	@echo "Resetting development environment..."
	docker compose --env-file .env.dev down -v
	docker compose --env-file .env.dev up --build -d
	@echo "Waiting 5 seconds for Database to accept connections..."
	@sleep 5
	@$(MAKE) migrate
	@$(MAKE) seed
	@echo "Reset complete! Fresh data ready."


