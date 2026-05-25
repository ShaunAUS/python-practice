from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from app.config import settings
from app.controller.board_controller import router as board_router
from app.database import init_db
from app.exception.handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """앱 시작/종료 이벤트 — Java @PostConstruct / CommandLineRunner 에 대응

    TestClient 를 컨텍스트 매니저로 사용하면 startup 이 정상 실행됩니다.
    """
    init_db()  # 앱 시작 시 테이블 생성
    yield
    # 앱 종료 시 정리 로직 (필요 시 추가)


app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
)

# 예외 핸들러 등록 — Java @RestControllerAdvice GlobalExceptionHandler 에 대응
register_exception_handlers(app)

# 라우터 등록 — Java @RestController 빈 등록에 대응
app.include_router(board_router)
