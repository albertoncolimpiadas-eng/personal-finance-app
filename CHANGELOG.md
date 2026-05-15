# Changelog

## 0.1.0 - 2026-05-15

Initial local-first personal finance application.

### Added

- Docker Compose setup for backend and frontend services.
- FastAPI backend with SQLModel and SQLite persistence.
- React + Vite + TypeScript frontend with dashboard, accounts, transactions, categories, budgets, and import pages.
- Account CRUD, calculated account balances, and account summaries.
- Category CRUD with default income and expense seed categories.
- Transaction CRUD with filtering and validation for income, expense, and transfer transactions.
- Monthly budgets with monthly spending summary.
- Dashboard monthly and yearly summaries.
- CSV transaction import preview and confirm endpoints.
- CSV transaction export endpoint and frontend download action.
- Local SQLite backup instructions.
- Backend pytest suite using temporary SQLite databases.

### Limitations

- Local-only, single-user app.
- No authentication, bank synchronization, cloud deployment, Kubernetes, PostgreSQL, or microservices.
- CSV import requires matching accounts and categories to exist before confirming import.
- CSV transfer import remains limited because transfer rows need a target account.
