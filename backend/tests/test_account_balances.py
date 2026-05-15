from datetime import date
from decimal import Decimal

from sqlmodel import Session

from app.models.account import AccountType
from app.models.category import CategoryType
from app.models.transaction import TransactionType
from app.repositories import account_repository, category_repository
from app.schemas.account_schema import AccountCreate
from app.schemas.category_schema import CategoryCreate
from app.schemas.transaction_schema import TransactionCreate
from app.services import account_service, transaction_service


def create_account(
    session: Session,
    name: str,
    initial_balance: Decimal = Decimal("0.00"),
) -> int:
    account = account_repository.create_account(
        session,
        AccountCreate(
            name=name,
            type=AccountType.CURRENT_ACCOUNT,
            initial_balance=initial_balance,
        ),
    )
    assert account.id is not None
    return account.id


def create_category(session: Session, name: str, category_type: CategoryType) -> int:
    category = category_repository.create_category(
        session,
        CategoryCreate(name=name, type=category_type),
    )
    assert category.id is not None
    return category.id


def test_balance_calculation_includes_income_expense_and_transfers(
    session: Session,
) -> None:
    checking_id = create_account(session, "Checking", Decimal("100.00"))
    savings_id = create_account(session, "Savings", Decimal("10.00"))
    income_category_id = create_category(session, "Salary", CategoryType.INCOME)
    expense_category_id = create_category(session, "Groceries", CategoryType.EXPENSE)

    transaction_service.create_transaction(
        session,
        TransactionCreate(
            transaction_type=TransactionType.INCOME,
            amount=Decimal("250.00"),
            date=date(2026, 5, 15),
            description="Income",
            account_id=checking_id,
            category_id=income_category_id,
        ),
    )
    transaction_service.create_transaction(
        session,
        TransactionCreate(
            transaction_type=TransactionType.EXPENSE,
            amount=Decimal("40.00"),
            date=date(2026, 5, 15),
            description="Expense",
            account_id=checking_id,
            category_id=expense_category_id,
        ),
    )
    transaction_service.create_transaction(
        session,
        TransactionCreate(
            transaction_type=TransactionType.TRANSFER,
            amount=Decimal("70.00"),
            date=date(2026, 5, 15),
            description="Move to savings",
            account_id=checking_id,
            target_account_id=savings_id,
        ),
    )

    checking_balance = account_service.get_account_balance(session, checking_id)
    savings_balance = account_service.get_account_balance(session, savings_id)

    assert checking_balance is not None
    assert savings_balance is not None
    assert checking_balance.current_balance == Decimal("240.00")
    assert savings_balance.current_balance == Decimal("80.00")


def test_account_summary_returns_calculated_balances(session: Session) -> None:
    checking_id = create_account(session, "Checking", Decimal("25.00"))
    savings_id = create_account(session, "Savings", Decimal("5.00"))
    income_category_id = create_category(session, "Salary", CategoryType.INCOME)

    transaction_service.create_transaction(
        session,
        TransactionCreate(
            transaction_type=TransactionType.INCOME,
            amount=Decimal("100.00"),
            date=date(2026, 5, 15),
            description="Income",
            account_id=checking_id,
            category_id=income_category_id,
        ),
    )
    transaction_service.create_transaction(
        session,
        TransactionCreate(
            transaction_type=TransactionType.TRANSFER,
            amount=Decimal("20.00"),
            date=date(2026, 5, 15),
            description="Move to savings",
            account_id=checking_id,
            target_account_id=savings_id,
        ),
    )

    summaries = account_service.list_account_summaries(session)

    assert [(summary.name, summary.current_balance) for summary in summaries] == [
        ("Checking", Decimal("105.00")),
        ("Savings", Decimal("25.00")),
    ]
