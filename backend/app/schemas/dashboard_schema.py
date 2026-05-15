from decimal import Decimal

from sqlmodel import SQLModel

from app.schemas.account_schema import AccountSummary
from app.schemas.budget_schema import BudgetCategoryRead


class CategoryAggregate(SQLModel):
    category: BudgetCategoryRead
    amount: Decimal


class DashboardMonthlySummary(SQLModel):
    total_income: Decimal
    total_expense: Decimal
    net_savings: Decimal
    savings_rate: Decimal
    expenses_by_category: list[CategoryAggregate]
    income_by_category: list[CategoryAggregate]
    account_balances: list[AccountSummary]


class DashboardYearlyMonthSummary(SQLModel):
    month: int
    total_income: Decimal
    total_expense: Decimal
    net_savings: Decimal
