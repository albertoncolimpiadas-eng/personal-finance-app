# Project instructions for Codex

This repository contains a local-first personal finance web application.

## Environment

The project is developed inside Rocky Linux running on WSL2.

Important constraints:

- Do not assume Ubuntu.
- Use Rocky/RHEL-compatible commands.
- Use `dnf`, not `apt`.
- Do not assume Docker Desktop.
- Docker Engine runs directly inside Rocky WSL.
- Docker Compose is available through the Docker Compose plugin.
- Use `docker compose`, not `docker-compose`.

Project path:

~/projects/personal-finance-app

## Goal

Build a simple, maintainable and containerized personal finance app that runs locally on the user's computer using Docker Compose.

The application must be accessible from the browser.

## Tech stack

- Backend: Python, FastAPI, SQLModel, SQLite.
- Frontend: React, Vite, TypeScript.
- Database: SQLite stored in `/data/finance.db` inside the backend container.
- Local database path: `./data/finance.db`.
- Containerization: Docker Compose.
- Deployment target for now: local machine only.

## Functional scope for version 0.1

Implement:

- Accounts
- Categories
- Transactions
- Monthly budgets
- Dashboard summary
- CSV import
- CSV export
- Local backup instructions

Do not implement yet:

- Bank synchronization
- Cloud deployment
- Multi-user authentication
- Kubernetes
- Microservices
- Mobile app
- OAuth
- Payment integrations

## Architecture rules

Keep frontend and backend separated.

Backend must expose a REST API.

Backend must be organized by layers:

- routers
- services
- repositories
- models
- schemas
- database

Frontend must call the backend only through a dedicated API client module.

Do not mix business logic inside React components.

Do not put all backend code in `main.py`.

Do not over-engineer the project.

## Backend conventions

Use:

- FastAPI
- SQLModel
- SQLite
- Pydantic validation
- Type hints
- pytest for tests

Backend structure should be similar to:

backend/
└── app/
    ├── main.py
    ├── database.py
    ├── models/
    ├── schemas/
    ├── repositories/
    ├── services/
    └── routers/

## Frontend conventions

Use:

- React
- Vite
- TypeScript

Frontend structure should be similar to:

frontend/
└── src/
    ├── api/
    ├── components/
    ├── pages/
    ├── types/
    └── App.tsx

## Data model

Initial entities:

Account:
- id
- name
- type
- currency
- initial_balance
- created_at

Category:
- id
- name
- type
- color
- created_at

Transaction:
- id
- transaction_type
- amount
- date
- description
- account_id
- category_id
- target_account_id
- notes
- created_at

Budget:
- id
- category_id
- year
- month
- limit_amount
- created_at

## Business rules

Account types:

- cash
- current_account
- savings
- credit_card

Category types:

- income
- expense

Transaction types:

- income
- expense
- transfer

Income transaction:

- requires account_id
- requires category_id
- category must be income
- target_account_id must be empty

Expense transaction:

- requires account_id
- requires category_id
- category must be expense
- target_account_id must be empty

Transfer transaction:

- requires account_id as source account
- requires target_account_id as destination account
- source account and target account must be different
- category_id is optional

Balance calculation:

- Start from account.initial_balance.
- Add income transactions for the account.
- Subtract expense transactions for the account.
- Subtract transfers where the account is source.
- Add transfers where the account is target.

Do not store current balance as an editable field. Calculate it from transactions.

## Definition of done

A task is complete only when:

- The code runs locally.
- Docker Compose starts the app.
- Backend health endpoint works.
- Frontend loads in the browser.
- Existing tests pass.
- README is updated if setup or commands changed.
- No unnecessary features are added.
