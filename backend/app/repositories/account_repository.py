from sqlmodel import Session, select

from app.models.account import Account
from app.schemas.account_schema import AccountCreate, AccountUpdate


def list_accounts(session: Session) -> list[Account]:
    return list(session.exec(select(Account).order_by(Account.id)).all())


def get_account(session: Session, account_id: int) -> Account | None:
    return session.get(Account, account_id)


def get_account_by_name(session: Session, name: str) -> Account | None:
    statement = select(Account).where(Account.name == name)
    return session.exec(statement).first()


def create_account(session: Session, account_create: AccountCreate) -> Account:
    account = Account.model_validate(account_create)
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def update_account(
    session: Session,
    account: Account,
    account_update: AccountUpdate,
) -> Account:
    account_data = account_update.model_dump()
    for field, value in account_data.items():
        setattr(account, field, value)

    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def delete_account(session: Session, account: Account) -> None:
    session.delete(account)
    session.commit()
