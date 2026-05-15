from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session

from app.database import create_db_and_tables, engine
from app.routers.account_router import router as account_router
from app.routers.category_router import router as category_router
from app.routers.health import router as health_router
from app.routers.transaction_router import router as transaction_router
from app.services.category_service import seed_default_categories


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    create_db_and_tables()
    with Session(engine) as session:
        seed_default_categories(session)
    yield


app = FastAPI(title="Personal Finance API", lifespan=lifespan)

app.include_router(account_router)
app.include_router(category_router)
app.include_router(transaction_router)
app.include_router(health_router)
