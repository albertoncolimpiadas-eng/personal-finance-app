# Personal Finance App

Local-first personal finance web app for tracking accounts, categories, transactions, monthly budgets, dashboard summaries, CSV import/export, and local SQLite backups.

The app is intended to run on one local machine with Docker Compose. It does not use Docker Desktop, Kubernetes, cloud deployment, bank synchronization, multi-user authentication, PostgreSQL, or microservices.

## Stack

- Backend: Python, FastAPI, SQLModel, SQLite, pytest
- Frontend: React, Vite, TypeScript
- Runtime: Docker Engine inside Rocky Linux on WSL2
- Container entry point: Docker Compose plugin through `docker compose`
- Database file: `./data/finance.db`, mounted into the backend container as `/app/data/finance.db`

## Environment Assumptions

- Rocky Linux running on WSL2.
- Docker Engine is installed directly inside Rocky WSL.
- Docker Desktop is not required.
- Docker Compose is available as the Docker CLI plugin.
- Use Rocky/RHEL-compatible commands.
- Use `dnf`, not `apt`, when installing system packages.
- Use `docker compose`, not `docker-compose`.

Useful checks:

```bash
docker compose version
sudo systemctl status docker
```

## Project Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── routers/
│   │   ├── schemas/
│   │   └── services/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── data/
│   └── .gitkeep
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── types/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── styles.css
│   ├── Dockerfile
│   └── package.json
├── compose.yaml
├── CHANGELOG.md
└── README.md
```

## Setup

From the project root:

```bash
mkdir -p data
docker compose config
```

The first command keeps the local SQLite mount target available. The second command validates the Compose file.

## Run The App

Start both services:

```bash
docker compose up --build
```

Then open:

- Frontend: http://localhost:8080
- Backend health check: http://localhost:8000/health
- Backend API docs: http://localhost:8000/docs

Stop the app:

```bash
docker compose down
```

Start only the backend:

```bash
docker compose up --build backend
```

## Manual Smoke Test

1. Start the app with `docker compose up --build`.
2. Visit http://localhost:8080 and confirm the React app loads.
3. Confirm the header shows the backend as reachable.
4. Visit http://localhost:8000/health and confirm it returns:

```json
{"status":"ok","service":"personal-finance-backend"}
```

5. Visit http://localhost:8000/docs and confirm FastAPI documentation opens.
6. Confirm the local SQLite database exists at `./data/finance.db` after backend startup.

## Tests

Run backend tests with one command:

```bash
docker compose run --rm backend pytest
```

The pytest suite uses temporary SQLite databases and does not read from or write to the real local database at `./data/finance.db`.

Build the frontend:

```bash
docker compose run --rm frontend npm run build
```

## SQLite Persistence

The backend creates database tables on application startup with SQLModel.

The local `./data` folder is mounted into the backend container at `/app/data`, and the backend uses:

```text
sqlite:////app/data/finance.db
```

The generated SQLite database is intentionally ignored by git.

## Backup And Restore

All local application data is stored in:

```text
./data/finance.db
```

Back up the database by stopping the containers and copying that file:

```bash
docker compose down
cp ./data/finance.db ./data/finance.backup.db
```

Restore a backup by stopping the containers and replacing `./data/finance.db` with the backed-up database file.

## API Overview

All API endpoints are documented by FastAPI at http://localhost:8000/docs.

Accounts:

- `GET /accounts`
- `GET /accounts/summary`
- `GET /accounts/{account_id}`
- `GET /accounts/{account_id}/balance`
- `POST /accounts`
- `PUT /accounts/{account_id}`
- `DELETE /accounts/{account_id}`

Categories:

- `GET /categories`
- `GET /categories/{category_id}`
- `POST /categories`
- `PUT /categories/{category_id}`
- `DELETE /categories/{category_id}`

Transactions:

- `GET /transactions`
- `GET /transactions/{transaction_id}`
- `POST /transactions`
- `PUT /transactions/{transaction_id}`
- `DELETE /transactions/{transaction_id}`

`GET /transactions` supports `account_id`, `category_id`, `transaction_type`, `date_from`, `date_to`, and `text` filters.

Budgets:

- `GET /budgets`
- `GET /budgets/monthly-summary?year=YYYY&month=M`
- `GET /budgets/{budget_id}`
- `POST /budgets`
- `PUT /budgets/{budget_id}`
- `DELETE /budgets/{budget_id}`

Dashboard:

- `GET /dashboard/monthly-summary?year=YYYY&month=M`
- `GET /dashboard/yearly-summary?year=YYYY`

CSV import/export:

- `POST /imports/transactions-csv/preview`
- `POST /imports/transactions-csv/confirm`
- `GET /exports/transactions.csv`

Health:

- `GET /health`

## CSV Import Format

The basic CSV import format expects these columns:

```text
date,description,amount,account_name,category_name,transaction_type
```

The importer previews rows before saving them. It validates that referenced accounts and categories already exist, dates and amounts are valid, and transaction type is one of `income`, `expense`, or `transfer`. Income and expense rows require an existing category with the matching category type.

The frontend Import page also exposes a button to download all transactions as CSV.

## Known Limitations

- Version 0.1 is local-only and single-user.
- There is no authentication or authorization.
- There is no bank synchronization or automatic transaction matching.
- CSV import requires referenced accounts and categories to exist before confirming the import.
- CSV transfer import preview is intentionally limited because imported transfer rows need a target account.
- SQLite is the only supported database.
- There is no cloud deployment, Kubernetes setup, mobile app, OAuth, or payment integration.
