from sqlmodel import Session, select

from app.models.category import Category
from app.schemas.category_schema import CategoryCreate, CategoryUpdate


def list_categories(session: Session) -> list[Category]:
    return list(session.exec(select(Category).order_by(Category.type, Category.name)).all())


def get_category(session: Session, category_id: int) -> Category | None:
    return session.get(Category, category_id)


def get_category_by_name(session: Session, name: str) -> Category | None:
    statement = select(Category).where(Category.name == name)
    return session.exec(statement).first()


def create_category(session: Session, category_create: CategoryCreate) -> Category:
    category = Category.model_validate(category_create)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def update_category(
    session: Session,
    category: Category,
    category_update: CategoryUpdate,
) -> Category:
    category_data = category_update.model_dump()
    for field, value in category_data.items():
        setattr(category, field, value)

    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def delete_category(session: Session, category: Category) -> None:
    session.delete(category)
    session.commit()


def count_categories(session: Session) -> int:
    categories = session.exec(select(Category.id)).all()
    return len(categories)
