from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.boards import router as board_router
from app.core.config import get_settings
from app.core.db import init_db
from app.core.handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    init_db()  # 앱 시작 시 테이블 생성
    yield


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
)

register_exception_handlers(app)
app.include_router(board_router)
