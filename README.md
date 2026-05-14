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
│   │   ├── repositories/
│   │   ├── routers/
│   │   │   └── health.py
│   │   ├── schemas/
│   │   └── services/
│   ├── Dockerfile
│   └── requirements.txt
├── data/
│   └── .gitkeep
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── styles.css
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

- Frontend: http://localhost:5173
- Backend health check: http://localhost:8000/health

Stop the app with:

```bash
docker compose down
```

## Manual Test

1. Start the app with `docker compose up --build`.
2. Visit http://localhost:5173 and confirm the React app loads.
3. Visit http://localhost:8000/health and confirm it returns:

```json
{"status":"ok"}
```

4. Confirm the local SQLite persistence folder exists at `./data`.

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
