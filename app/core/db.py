from __future__ import annotations

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app import models  # noqa: F401 — SQLModel.metadata 에 테이블 등록
from app.core.config import get_settings

settings = get_settings()  # import 시점 1회(engine 생성에 필요) — lru_cache 로 캐시됨

# SQLite 전용 옵션은 sqlite URL 일 때만 — 다른 DB 로 바꿔도 안 깨짐
_connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    echo=settings.sql_echo,
)


def init_db() -> None:
    """앱 시작 시 테이블 생성 (FastAPI 공식 SQL 튜토리얼 방식)."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """요청 스코프 세션 의존성 (FastAPI 공식 yield 패턴)."""
    with Session(engine) as session:
        yield session
