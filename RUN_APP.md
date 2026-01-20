# Running the APP

## Prerequisites (Criteria for Installation)

Before running this project, ensure you have the following installed on your machine.

### 1. Docker Desktop

- **Mac/Linux:** [Download here](https://www.docker.com/products/docker-desktop/).
- **Windows:** [Download here](https://www.docker.com/products/docker-desktop/).

### 2. Make (Optional but Recommended)

We use a `Makefile` to simplify complex Docker commands.

- **Mac/Linux:** Usually pre-installed. If not: `sudo apt install make`.
- **Windows:**
  - Install via Chocolatey: `choco install make`.

## Quick Start

**Start the Server**

```bash
make run
```

**Stop the Server**

```bash
make down
```

_This will build the Docker images and start the containers_

---

## Database Management

The database runs in a separate Docker container. You do not need PostgreSQL installed locally.

### Initialize & Seed Data

When you run `make run`, data will automatically be added.

*Check out populate_db.py*

### Viewing Data

To enter the database CLI directly:

```bash
make view-data
```

## Command Reference

| Action | Make Command | Raw Docker Command |
| :--- | :--- | :--- |
| **Start Server** | `make run` | `docker compose --env-file .env.dev up --build` |
| **Stop Server** | `make down` | `docker compose --env-file .env.dev down` |
| **Clean Reset** | `make clear` | `docker compose --env-file .env.dev down -v --rmi all --remove-orphans` |
| **View Data** | `make view-data` | `docker compose --env-file .env.dev exec db psql -U postgres -d digital_finance_db` |