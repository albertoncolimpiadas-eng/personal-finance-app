from sqlmodel import Session

from app.models.account import Account
from app.repositories import account_repository
from app.schemas.account_schema import AccountCreate, AccountUpdate


def list_accounts(session: Session) -> list[Account]:
    return account_repository.list_accounts(session)


def get_account(session: Session, account_id: int) -> Account | None:
    return account_repository.get_account(session, account_id)


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
