from sqlmodel import Session

from app.models.category import Category, CategoryType
from app.repositories import category_repository
from app.schemas.category_schema import CategoryCreate, CategoryUpdate

DEFAULT_CATEGORIES: tuple[CategoryCreate, ...] = (
    CategoryCreate(name="Supermarket", type=CategoryType.EXPENSE),
    CategoryCreate(name="Housing", type=CategoryType.EXPENSE),
    CategoryCreate(name="Transport", type=CategoryType.EXPENSE),
    CategoryCreate(name="Restaurants", type=CategoryType.EXPENSE),
    CategoryCreate(name="Health", type=CategoryType.EXPENSE),
    CategoryCreate(name="Leisure", type=CategoryType.EXPENSE),
    CategoryCreate(name="Subscriptions", type=CategoryType.EXPENSE),
    CategoryCreate(name="Salary", type=CategoryType.INCOME),
    CategoryCreate(name="Freelance", type=CategoryType.INCOME),
    CategoryCreate(name="Other income", type=CategoryType.INCOME),
)


def list_categories(session: Session) -> list[Category]:
    return category_repository.list_categories(session)


def get_category(session: Session, category_id: int) -> Category | None:
    return category_repository.get_category(session, category_id)


def create_category(session: Session, category_create: CategoryCreate) -> Category:
    return category_repository.create_category(session, category_create)


def update_category(
    session: Session,
    category_id: int,
    category_update: CategoryUpdate,
) -> Category | None:
    category = category_repository.get_category(session, category_id)
    if category is None:
        return None

    return category_repository.update_category(session, category, category_update)


def delete_category(session: Session, category_id: int) -> bool:
    category = category_repository.get_category(session, category_id)
    if category is None:
        return False

    category_repository.delete_category(session, category)
    return True


def seed_default_categories(session: Session) -> None:
    if category_repository.count_categories(session) > 0:
        return

    for category_create in DEFAULT_CATEGORIES:
        category_repository.create_category(session, category_create)
