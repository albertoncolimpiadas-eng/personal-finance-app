from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AccountType(str, Enum):
    CASH = "cash"
    CURRENT_ACCOUNT = "current_account"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"


class Account(SQLModel, table=True):
    __tablename__ = "accounts"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    type: AccountType
    currency: str = Field(default="EUR", max_length=3)
    initial_balance: Decimal = Field(
        default=Decimal("0.00"),
        max_digits=14,
        decimal_places=2,
    )
    created_at: datetime = Field(default_factory=utc_now)
