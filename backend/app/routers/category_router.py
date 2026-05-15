from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from app.database import get_session
from app.schemas.category_schema import CategoryCreate, CategoryRead, CategoryUpdate
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])

SessionDependency = Annotated[Session, Depends(get_session)]


@router.get("", response_model=list[CategoryRead])
def list_categories(session: SessionDependency) -> list[CategoryRead]:
    return category_service.list_categories(session)


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, session: SessionDependency) -> CategoryRead:
    category = category_service.get_category(session, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    return category


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    category_create: CategoryCreate,
    session: SessionDependency,
) -> CategoryRead:
    return category_service.create_category(session, category_create)


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    session: SessionDependency,
) -> CategoryRead:
    category = category_service.update_category(session, category_id, category_update)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, session: SessionDependency) -> Response:
    deleted = category_service.delete_category(session, category_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
