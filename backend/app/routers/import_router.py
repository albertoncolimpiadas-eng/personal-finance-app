from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlmodel import Session

from app.database import get_session
from app.schemas.import_schema import TransactionCsvImportResult, TransactionCsvPreview
from app.services import import_service

router = APIRouter(prefix="/imports", tags=["imports"])

SessionDependency = Annotated[Session, Depends(get_session)]


@router.post("/transactions-csv/preview", response_model=TransactionCsvPreview)
async def preview_transactions_csv(
    session: SessionDependency,
    file: UploadFile = File(...),
) -> TransactionCsvPreview:
    return import_service.preview_transactions_csv(session, await file.read())


@router.post("/transactions-csv/confirm", response_model=TransactionCsvImportResult)
async def confirm_transactions_csv(
    session: SessionDependency,
    file: UploadFile = File(...),
) -> TransactionCsvImportResult:
    return import_service.confirm_transactions_csv(session, await file.read())
