from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.domain.board import Base

# SQLite 전용 옵션(check_same_thread)은 sqlite URL 일 때만 적용 — 다른 DB 로 바꿔도 안 깨짐
_connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

engine = create_engine(
    settings.database_url,  # Java spring.datasource.url 에 대응 (config.Settings 에서 주입)
    connect_args=_connect_args,
    echo=settings.sql_echo,  # Java spring.jpa.show-sql 에 대응
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db() -> None:
    """앱 시작 시 테이블 생성 — Java @Entity + ddl-auto=create 에 대응"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI Depends 용 세션 제너레이터 — Java @Autowired / 의존성 주입에 대응"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
