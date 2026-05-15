from sqlmodel import Session, select

from app.models.budget import Budget
from app.schemas.budget_schema import BudgetCreate, BudgetUpdate


def list_budgets(session: Session) -> list[Budget]:
    statement = select(Budget).order_by(Budget.year.desc(), Budget.month.desc(), Budget.category_id)
    return list(session.exec(statement).all())


def list_budgets_for_month(session: Session, year: int, month: int) -> list[Budget]:
    statement = (
        select(Budget)
        .where(Budget.year == year)
        .where(Budget.month == month)
        .order_by(Budget.category_id)
    )
    return list(session.exec(statement).all())


def get_budget(session: Session, budget_id: int) -> Budget | None:
    return session.get(Budget, budget_id)


def get_budget_by_category_month(
    session: Session,
    category_id: int,
    year: int,
    month: int,
) -> Budget | None:
    statement = (
        select(Budget)
        .where(Budget.category_id == category_id)
        .where(Budget.year == year)
        .where(Budget.month == month)
    )
    return session.exec(statement).first()


def create_budget(session: Session, budget_create: BudgetCreate) -> Budget:
    budget = Budget.model_validate(budget_create)
    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget


def update_budget(session: Session, budget: Budget, budget_update: BudgetUpdate) -> Budget:
    for field, value in budget_update.model_dump().items():
        setattr(budget, field, value)

    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget


def delete_budget(session: Session, budget: Budget) -> None:
    session.delete(budget)
    session.commit()
