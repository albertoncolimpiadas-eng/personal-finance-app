from datetime import date
from decimal import Decimal

from sqlmodel import Session

from app.models.category import Category
from app.models.transaction import Transaction, TransactionType
from app.repositories import category_repository, transaction_repository
from app.schemas.budget_schema import BudgetCategoryRead
from app.schemas.dashboard_schema import (
    CategoryAggregate,
    DashboardMonthlySummary,
    DashboardYearlyMonthSummary,
)
from app.services import account_service
from app.services.budget_service import month_range, validate_month


def get_monthly_summary(session: Session, year: int, month: int) -> DashboardMonthlySummary:
    validate_month(year, month)
    start_date, end_date = month_range(year, month)
    transactions = transaction_repository.list_transactions(
        session=session,
        date_from=start_date,
        date_to=end_date,
    )
    income_transactions = [
        transaction
        for transaction in transactions
        if transaction.transaction_type == TransactionType.INCOME
    ]
    expense_transactions = [
        transaction
        for transaction in transactions
        if transaction.transaction_type == TransactionType.EXPENSE
    ]

    total_income = sum_amounts(income_transactions)
    total_expense = sum_amounts(expense_transactions)
    net_savings = total_income - total_expense
    savings_rate = (
        net_savings / total_income * Decimal("100")
        if total_income > 0
        else Decimal("0")
    )

    return DashboardMonthlySummary(
        total_income=total_income,
        total_expense=total_expense,
        net_savings=net_savings,
        savings_rate=savings_rate,
        expenses_by_category=aggregate_by_category(session, expense_transactions),
        income_by_category=aggregate_by_category(session, income_transactions),
        account_balances=account_service.list_account_summaries(session),
    )


def get_yearly_summary(session: Session, year: int) -> list[DashboardYearlyMonthSummary]:
    if year < 1900 or year > 2200:
        raise ValueError("year must be between 1900 and 2200")

    summaries: list[DashboardYearlyMonthSummary] = []
    for month in range(1, 13):
        start_date, end_date = month_range(year, month)
        transactions = transaction_repository.list_transactions(
            session=session,
            date_from=start_date,
            date_to=end_date,
        )
        total_income = sum_amounts(
            transaction
            for transaction in transactions
            if transaction.transaction_type == TransactionType.INCOME
        )
        total_expense = sum_amounts(
            transaction
            for transaction in transactions
            if transaction.transaction_type == TransactionType.EXPENSE
        )
        summaries.append(
            DashboardYearlyMonthSummary(
                month=month,
                total_income=total_income,
                total_expense=total_expense,
                net_savings=total_income - total_expense,
            )
        )

    return summaries


def aggregate_by_category(
    session: Session,
    transactions: list[Transaction],
) -> list[CategoryAggregate]:
    totals: dict[int, Decimal] = {}
    for transaction in transactions:
        if transaction.category_id is None:
            continue
        totals[transaction.category_id] = totals.get(transaction.category_id, Decimal("0")) + transaction.amount

    aggregates: list[CategoryAggregate] = []
    for category_id, amount in sorted(totals.items()):
        category = category_repository.get_category(session, category_id)
        if category is None:
            continue
        aggregates.append(
            CategoryAggregate(
                category=to_category_read(category),
                amount=amount,
            )
        )

    return aggregates


def to_category_read(category: Category) -> BudgetCategoryRead:
    return BudgetCategoryRead(
        id=category.id,
        name=category.name,
        type=category.type,
        color=category.color,
    )


def sum_amounts(transactions) -> Decimal:
    return sum((transaction.amount for transaction in transactions), Decimal("0"))
