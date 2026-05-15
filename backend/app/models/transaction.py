from datetime import date as date_type
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"

    id: int | None = Field(default=None, primary_key=True)
    transaction_type: TransactionType
    amount: Decimal = Field(max_digits=14, decimal_places=2)
    date: date_type = Field(index=True)
    description: str = Field(index=True)
    account_id: int = Field(foreign_key="accounts.id", index=True)
    category_id: int | None = Field(default=None, foreign_key="categories.id", index=True)
    target_account_id: int | None = Field(default=None, foreign_key="accounts.id", index=True)
    notes: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
