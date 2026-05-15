from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, Session, create_engine

from app import models  # noqa: F401
from app.database import get_session
from app.main import app


@pytest.fixture(name="test_engine")
def test_engine_fixture(tmp_path) -> Generator[Engine, None, None]:
    database_path = tmp_path / "finance-test.db"
    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)

    yield engine

    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(name="session")
def session_fixture(test_engine: Engine) -> Generator[Session, None, None]:
    with Session(test_engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(test_engine: Engine) -> Generator[TestClient, None, None]:
    def get_test_session() -> Generator[Session, None, None]:
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session

    yield TestClient(app)

    app.dependency_overrides.clear()
