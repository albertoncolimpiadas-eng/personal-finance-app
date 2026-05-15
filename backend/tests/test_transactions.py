from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app import models  # noqa: F401
from app.database import get_session
from app.main import app


@pytest.fixture(name="client")
def client_fixture() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def get_test_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()


def create_account(client: TestClient, name: str) -> int:
    response = client.post(
        "/accounts",
        json={"name": name, "type": "current_account"},
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def create_category(client: TestClient, name: str, category_type: str) -> int:
    response = client.post(
        "/categories",
        json={"name": name, "type": category_type},
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def test_create_income_transaction(client: TestClient) -> None:
    account_id = create_account(client, "Checking")
    category_id = create_category(client, "Salary", "income")

    response = client.post(
        "/transactions",
        json={
            "transaction_type": "income",
            "amount": "2500.00",
            "date": "2026-05-15",
            "description": "May salary",
            "account_id": account_id,
            "category_id": category_id,
        },
    )

    assert response.status_code == 201
    transaction = response.json()
    assert transaction["transaction_type"] == "income"
    assert Decimal(transaction["amount"]) == Decimal("2500.00")
    assert transaction["description"] == "May salary"
    assert transaction["account_id"] == account_id
    assert transaction["category_id"] == category_id
    assert transaction["target_account_id"] is None


def test_create_expense_transaction(client: TestClient) -> None:
    account_id = create_account(client, "Checking")
    category_id = create_category(client, "Supermarket", "expense")

    response = client.post(
        "/transactions",
        json={
            "transaction_type": "expense",
            "amount": "42.95",
            "date": "2026-05-14",
            "description": "Grocery run",
            "account_id": account_id,
            "category_id": category_id,
            "notes": "Weekly shop",
        },
    )

    assert response.status_code == 201
    transaction = response.json()
    assert transaction["transaction_type"] == "expense"
    assert Decimal(transaction["amount"]) == Decimal("42.95")
    assert transaction["notes"] == "Weekly shop"


def test_create_transfer_transaction(client: TestClient) -> None:
    source_account_id = create_account(client, "Checking")
    target_account_id = create_account(client, "Savings")

    response = client.post(
        "/transactions",
        json={
            "transaction_type": "transfer",
            "amount": "300.00",
            "date": "2026-05-13",
            "description": "Move to savings",
            "account_id": source_account_id,
            "target_account_id": target_account_id,
        },
    )

    assert response.status_code == 201
    transaction = response.json()
    assert transaction["transaction_type"] == "transfer"
    assert transaction["account_id"] == source_account_id
    assert transaction["target_account_id"] == target_account_id
    assert transaction["category_id"] is None


def test_reject_invalid_transfer_same_source_and_target(client: TestClient) -> None:
    account_id = create_account(client, "Checking")

    response = client.post(
        "/transactions",
        json={
            "transaction_type": "transfer",
            "amount": "100.00",
            "date": "2026-05-12",
            "description": "Invalid transfer",
            "account_id": account_id,
            "target_account_id": account_id,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "transfer source and target accounts must be different"


def test_reject_expense_with_income_category(client: TestClient) -> None:
    account_id = create_account(client, "Checking")
    category_id = create_category(client, "Salary", "income")

    response = client.post(
        "/transactions",
        json={
            "transaction_type": "expense",
            "amount": "15.00",
            "date": "2026-05-11",
            "description": "Wrong category",
            "account_id": account_id,
            "category_id": category_id,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "expense transaction must use an expense category"


def test_filter_transactions(client: TestClient) -> None:
    checking_id = create_account(client, "Checking")
    savings_id = create_account(client, "Savings")
    income_category_id = create_category(client, "Freelance", "income")
    expense_category_id = create_category(client, "Restaurants", "expense")
    client.post(
        "/transactions",
        json={
            "transaction_type": "income",
            "amount": "120.00",
            "date": "2026-05-01",
            "description": "Invoice ABC",
            "account_id": checking_id,
            "category_id": income_category_id,
        },
    )
    client.post(
        "/transactions",
        json={
            "transaction_type": "expense",
            "amount": "20.00",
            "date": "2026-05-10",
            "description": "Dinner",
            "account_id": checking_id,
            "category_id": expense_category_id,
        },
    )
    client.post(
        "/transactions",
        json={
            "transaction_type": "transfer",
            "amount": "50.00",
            "date": "2026-05-15",
            "description": "Savings transfer",
            "account_id": checking_id,
            "target_account_id": savings_id,
        },
    )

    response = client.get(
        "/transactions",
        params={
            "account_id": checking_id,
            "transaction_type": "income",
            "date_from": "2026-05-01",
            "date_to": "2026-05-31",
            "text": "invoice",
        },
    )

    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 1
    assert transactions[0]["description"] == "Invoice ABC"
