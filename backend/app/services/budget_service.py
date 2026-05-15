from datetime import date
from decimal import Decimal

from sqlmodel import Session

from app.models.budget import Budget
from app.models.category import Category, CategoryType
from app.models.transaction import TransactionType
from app.repositories import budget_repository, category_repository, transaction_repository
from app.schemas.budget_schema import (
    BudgetCategoryRead,
    BudgetCreate,
    BudgetMonthlySummary,
    BudgetUpdate,
)


class BudgetValidationError(ValueError):
    pass


def list_budgets(session: Session) -> list[Budget]:
    return budget_repository.list_budgets(session)


def get_budget(session: Session, budget_id: int) -> Budget | None:
    return budget_repository.get_budget(session, budget_id)


def create_budget(session: Session, budget_create: BudgetCreate) -> Budget:
    validate_budget(session, budget_create)
    return budget_repository.create_budget(session, budget_create)


def update_budget(session: Session, budget_id: int, budget_update: BudgetUpdate) -> Budget | None:
    budget = budget_repository.get_budget(session, budget_id)
    if budget is None:
        return None

    validate_budget(session, budget_update, current_budget_id=budget_id)
    return budget_repository.update_budget(session, budget, budget_update)


def delete_budget(session: Session, budget_id: int) -> bool:
    budget = budget_repository.get_budget(session, budget_id)
    if budget is None:
        return False

    budget_repository.delete_budget(session, budget)
    return True


def validate_budget(
    session: Session,
    budget_data: BudgetCreate | BudgetUpdate,
    current_budget_id: int | None = None,
) -> None:
    category = category_repository.get_category(session, budget_data.category_id)
    if category is None:
        raise BudgetValidationError("category_id does not reference an existing category")
    if category.type != CategoryType.EXPENSE:
        raise BudgetValidationError("budget category must be an expense category")

    existing = budget_repository.get_budget_by_category_month(
        session,
        budget_data.category_id,
        budget_data.year,
        budget_data.month,
    )
    if existing is not None and existing.id != current_budget_id:
        raise BudgetValidationError("budget already exists for this category/year/month")


def get_monthly_summary(session: Session, year: int, month: int) -> list[BudgetMonthlySummary]:
    validate_month(year, month)
    summaries: list[BudgetMonthlySummary] = []
    for budget in budget_repository.list_budgets_for_month(session, year, month):
        category = category_repository.get_category(session, budget.category_id)
        if category is None:
            continue

        spent_amount = get_expense_spent_for_category(session, budget.category_id, year, month)
        remaining_amount = budget.limit_amount - spent_amount
        percentage_used = (
            spent_amount / budget.limit_amount * Decimal("100")
            if budget.limit_amount > 0
            else Decimal("0")
        )
        summaries.append(
            BudgetMonthlySummary(
                category=to_budget_category_read(category),
                limit_amount=budget.limit_amount,
                spent_amount=spent_amount,
                remaining_amount=remaining_amount,
                percentage_used=percentage_used,
            )
        )

    return summaries


def get_expense_spent_for_category(
    session: Session,
    category_id: int,
    year: int,
    month: int,
) -> Decimal:
    start_date, end_date = month_range(year, month)
    transactions = transaction_repository.list_transactions(
        session=session,
        category_id=category_id,
        transaction_type=TransactionType.EXPENSE,
        date_from=start_date,
        date_to=end_date,
    )
    return sum((transaction.amount for transaction in transactions), Decimal("0"))


def to_budget_category_read(category: Category) -> BudgetCategoryRead:
    return BudgetCategoryRead(
        id=category.id,
        name=category.name,
        type=category.type,
        color=category.color,
    )


def validate_month(year: int, month: int) -> None:
    if year < 1900 or year > 2200:
        raise BudgetValidationError("year must be between 1900 and 2200")
    if month < 1 or month > 12:
        raise BudgetValidationError("month must be between 1 and 12")


def month_range(year: int, month: int) -> tuple[date, date]:
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year, 12, 31)
    else:
        end_date = date(year, month + 1, 1).replace(day=1) - date.resolution
    return start_date, end_date
