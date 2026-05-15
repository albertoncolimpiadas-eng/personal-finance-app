from sqlmodel import SQLModel

from app import models  # noqa: F401


def test_finance_tables_are_registered() -> None:
    assert {"accounts", "categories", "transactions", "budgets"}.issubset(
        SQLModel.metadata.tables.keys()
    )
