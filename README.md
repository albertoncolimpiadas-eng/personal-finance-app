# Personal Finance App

Local-first personal finance web app scaffold.

## Stack

- Backend: Python, FastAPI, SQLModel, SQLite
- Frontend: React, Vite, TypeScript
- Runtime: Docker Compose with Docker Engine inside Rocky Linux on WSL2
- Database file: `./data/finance.db`, mounted in the backend container as `/app/data/finance.db`

This project does not use Docker Desktop, Kubernetes, cloud deployment, bank synchronization, multi-user authentication, PostgreSQL, or microservices.

## Project Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   └── finance.py
│   │   ├── repositories/
│   │   ├── routers/
│   │   │   └── health.py
│   │   ├── schemas/
│   │   └── services/
│   ├── tests/
│   │   ├── test_health.py
│   │   └── test_models.py
│   ├── Dockerfile
│   └── requirements.txt
├── data/
│   └── .gitkeep
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── components/
│   │   ├── pages/
│   │   │   └── HomePage.tsx
│   │   ├── types/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── styles.css
│   │   └── vite-env.d.ts
│   ├── Dockerfile
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts
├── compose.yaml
└── README.md
```

## Run The App

From the project root:

```bash
docker compose up --build
```

Then open:

- Frontend: http://localhost:8080
- Backend health check: http://localhost:8000/health
- Backend API docs: http://localhost:8000/docs

The frontend includes pages for Dashboard, Accounts, Transactions, Categories, Budgets, and Import. It checks `GET /health` and shows backend reachability in the header.

Stop the app with:

```bash
docker compose down
```

## Manual Test

1. Start the app with `docker compose up --build`.
2. Visit http://localhost:8080 and confirm the React app loads.
3. Visit http://localhost:8000/health and confirm it returns:

```json
{"status":"ok","service":"personal-finance-backend"}
```

4. Visit http://localhost:8000/docs and confirm the FastAPI documentation opens.
5. Confirm the local SQLite database exists at `./data/finance.db`.

## SQLite Persistence

The backend creates database tables on application startup with SQLModel.

The local `./data` folder is mounted into the backend container at `/app/data`, and the app uses:

```text
sqlite:////app/data/finance.db
```

The generated SQLite database is intentionally ignored by git.

## Accounts API

Accounts can be managed from the FastAPI docs at http://localhost:8000/docs.

Available endpoints:

- `GET /accounts`
- `GET /accounts/summary`
- `GET /accounts/{account_id}`
- `GET /accounts/{account_id}/balance`
- `POST /accounts`
- `PUT /accounts/{account_id}`
- `DELETE /accounts/{account_id}`

Example create request:

```json
{
  "name": "Main checking",
  "type": "current_account",
  "currency": "EUR",
  "initial_balance": "0"
}
```

Account balances are calculated from transactions at request time. The app does not store `current_balance` as an editable database field.

## Categories API

Categories can be managed from the FastAPI docs at http://localhost:8000/docs.

Available endpoints:

- `GET /categories`
- `GET /categories/{category_id}`
- `POST /categories`
- `PUT /categories/{category_id}`
- `DELETE /categories/{category_id}`

Example create request:

```json
{
  "name": "Groceries",
  "type": "expense",
  "color": "#0f766e"
}
```

When the category table is empty, the backend seeds these defaults on startup:

- Expense: Supermarket, Housing, Transport, Restaurants, Health, Leisure, Subscriptions
- Income: Salary, Freelance, Other income

## Transactions API

Transactions can be managed from the FastAPI docs at http://localhost:8000/docs.

Available endpoints:

- `GET /transactions`
- `GET /transactions/{transaction_id}`
- `POST /transactions`
- `PUT /transactions/{transaction_id}`
- `DELETE /transactions/{transaction_id}`

`GET /transactions` supports these optional filters:

- `account_id`
- `category_id`
- `transaction_type`
- `date_from`
- `date_to`
- `text`

Example income request:

```json
{
  "transaction_type": "income",
  "amount": "2500.00",
  "date": "2026-05-15",
  "description": "May salary",
  "account_id": 1,
  "category_id": 8
}
```

Example transfer request:

```json
{
  "transaction_type": "transfer",
  "amount": "300.00",
  "date": "2026-05-15",
  "description": "Move to savings",
  "account_id": 1,
  "target_account_id": 2
}
```

## Budgets API

Monthly budgets can be managed from the FastAPI docs at http://localhost:8000/docs.

Available endpoints:

- `GET /budgets`
- `GET /budgets/monthly-summary?year=YYYY&month=M`
- `GET /budgets/{budget_id}`
- `POST /budgets`
- `PUT /budgets/{budget_id}`
- `DELETE /budgets/{budget_id}`

Budgets are allowed only for expense categories, and only one budget can exist for each category/year/month.

Example create request:

```json
{
  "category_id": 1,
  "year": 2026,
  "month": 5,
  "limit_amount": "500.00"
}
```

## Dashboard API

Dashboard summaries are calculated from transactions and account balances.

Available endpoints:

- `GET /dashboard/monthly-summary?year=YYYY&month=M`
- `GET /dashboard/yearly-summary?year=YYYY`

Monthly summary returns total income, total expense, net savings, savings rate, category breakdowns, and account balances.

Yearly summary returns one aggregate row per month.

Backend tests can be run inside the backend container once dependencies are built:

```bash
docker compose run --rm backend pytest
```

To start only the backend service:

```bash
docker compose up --build backend
```

## Rocky Linux Notes

Use Rocky/RHEL-compatible commands. For package installation, use `dnf`, not `apt`.

Example Docker Engine status check:

```bash
sudo systemctl status docker
```

Use Compose through the Docker CLI:

```bash
docker compose version
```
