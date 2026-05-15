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


def test_create_account(client: TestClient) -> None:
    response = client.post(
        "/accounts",
        json={
            "name": "Main checking",
            "type": "current_account",
            "initial_balance": "150.25",
        },
    )

    assert response.status_code == 201
    account = response.json()
    assert account["id"] == 1
    assert account["name"] == "Main checking"
    assert account["type"] == "current_account"
    assert account["currency"] == "EUR"
    assert Decimal(account["initial_balance"]) == Decimal("150.25")
    assert "created_at" in account


def test_list_accounts(client: TestClient) -> None:
    client.post(
        "/accounts",
        json={"name": "Cash wallet", "type": "cash"},
    )
    client.post(
        "/accounts",
        json={
            "name": "Savings",
            "type": "savings",
            "currency": "usd",
            "initial_balance": "-25.00",
        },
    )

    response = client.get("/accounts")

    assert response.status_code == 200
    accounts = response.json()
    assert [account["name"] for account in accounts] == ["Cash wallet", "Savings"]
    assert accounts[0]["currency"] == "EUR"
    assert accounts[1]["currency"] == "USD"
    assert Decimal(accounts[1]["initial_balance"]) == Decimal("-25.00")
