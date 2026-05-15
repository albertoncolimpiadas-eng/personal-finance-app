from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app import models  # noqa: F401
from app.database import get_session
from app.main import app
from app.services.category_service import seed_default_categories


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


def test_seed_default_categories_when_empty(client: TestClient) -> None:
    session_generator = app.dependency_overrides[get_session]()
    session = next(session_generator)
    try:
        seed_default_categories(session)
    finally:
        session_generator.close()

    response = client.get("/categories")

    assert response.status_code == 200
    categories = response.json()
    category_names = {category["name"] for category in categories}
    assert category_names == {
        "Supermarket",
        "Housing",
        "Transport",
        "Restaurants",
        "Health",
        "Leisure",
        "Subscriptions",
        "Salary",
        "Freelance",
        "Other income",
    }
    assert len(categories) == 10


def test_create_and_list_categories(client: TestClient) -> None:
    create_response = client.post(
        "/categories",
        json={
            "name": "Dividends",
            "type": "income",
            "color": "#22c55e",
        },
    )

    assert create_response.status_code == 201
    created_category = create_response.json()
    assert created_category["name"] == "Dividends"
    assert created_category["type"] == "income"
    assert created_category["color"] == "#22c55e"

    list_response = client.get("/categories")

    assert list_response.status_code == 200
    categories = list_response.json()
    assert len(categories) == 1
    assert categories[0]["name"] == "Dividends"


def test_update_category(client: TestClient) -> None:
    create_response = client.post(
        "/categories",
        json={"name": "Groceries", "type": "expense"},
    )
    category_id = create_response.json()["id"]

    update_response = client.put(
        f"/categories/{category_id}",
        json={
            "name": "Food",
            "type": "expense",
            "color": "#f97316",
        },
    )

    assert update_response.status_code == 200
    updated_category = update_response.json()
    assert updated_category["id"] == category_id
    assert updated_category["name"] == "Food"
    assert updated_category["color"] == "#f97316"


def test_delete_category(client: TestClient) -> None:
    create_response = client.post(
        "/categories",
        json={"name": "One off", "type": "expense"},
    )
    category_id = create_response.json()["id"]

    delete_response = client.delete(f"/categories/{category_id}")
    get_response = client.get(f"/categories/{category_id}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
