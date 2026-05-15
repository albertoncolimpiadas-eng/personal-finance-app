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
- `GET /accounts/{account_id}`
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
