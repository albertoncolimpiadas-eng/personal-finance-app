from decimal import Decimal

from sqlmodel import Session

from app.models.account import Account
from app.models.transaction import TransactionType
from app.repositories import account_repository, transaction_repository
from app.schemas.account_schema import (
    AccountBalance,
    AccountCreate,
    AccountSummary,
    AccountUpdate,
)


def list_accounts(session: Session) -> list[Account]:
    return account_repository.list_accounts(session)


def get_account(session: Session, account_id: int) -> Account | None:
    return account_repository.get_account(session, account_id)


def get_account_balance(session: Session, account_id: int) -> AccountBalance | None:
    account = account_repository.get_account(session, account_id)
    if account is None:
        return None

    return AccountBalance(
        account_id=account.id,
        current_balance=calculate_account_balance(session, account),
    )


def list_account_summaries(session: Session) -> list[AccountSummary]:
    return [
        AccountSummary(
            id=account.id,
            name=account.name,
            type=account.type,
            currency=account.currency,
            initial_balance=account.initial_balance,
            current_balance=calculate_account_balance(session, account),
        )
        for account in account_repository.list_accounts(session)
    ]


def create_account(session: Session, account_create: AccountCreate) -> Account:
    return account_repository.create_account(session, account_create)


def update_account(
    session: Session,
    account_id: int,
    account_update: AccountUpdate,
) -> Account | None:
    account = account_repository.get_account(session, account_id)
    if account is None:
        return None

    return account_repository.update_account(session, account, account_update)


def delete_account(session: Session, account_id: int) -> bool:
    account = account_repository.get_account(session, account_id)
    if account is None:
        return False

    account_repository.delete_account(session, account)
    return True


def calculate_account_balance(session: Session, account: Account) -> Decimal:
    balance = account.initial_balance
    transactions = transaction_repository.list_transactions_for_account_balance(
        session,
        account.id,
    )

    for transaction in transactions:
        if transaction.transaction_type == TransactionType.INCOME:
            balance += transaction.amount
        elif transaction.transaction_type == TransactionType.EXPENSE:
            balance -= transaction.amount
        elif transaction.account_id == account.id:
            balance -= transaction.amount
        elif transaction.target_account_id == account.id:
            balance += transaction.amount

    return balance
