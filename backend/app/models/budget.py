from datetime import datetime, timezone
from decimal import Decimal

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Budget(SQLModel, table=True):
    __tablename__ = "budgets"

    id: int | None = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="categories.id", index=True)
    year: int = Field(index=True)
    month: int = Field(index=True, ge=1, le=12)
    limit_amount: Decimal = Field(max_digits=14, decimal_places=2)
    created_at: datetime = Field(default_factory=utc_now)
