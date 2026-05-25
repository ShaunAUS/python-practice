"""
conftest.py — pytest 공용 픽스처 & 팩토리 (FastAPI 공식 테스트 방식).

  - 인메모리 SQLite(StaticPool) + function scope → 테스트마다 독립 DB
  - get_session 의존성 오버라이드 (FastAPI 공식 dependency_overrides 패턴)
"""
from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.db import get_session
from app.main import app
from app.models import Board

# ---------------------------------------------------------------------------
# 픽스처 상수
# ---------------------------------------------------------------------------

DEFAULT_TITLE = "첫 번째 공지사항"
DEFAULT_CONTENT = "첫 번째 공지사항 내용입니다. 모든 회원분들께 안내드립니다."
DEFAULT_AUTHOR = "관리자"

SECOND_TITLE = "두 번째 공지사항"
SECOND_CONTENT = "두 번째 공지사항 내용입니다."
SECOND_AUTHOR = "운영자"

UPDATE_TITLE = "수정된 제목"
UPDATE_CONTENT = "수정된 내용입니다."
UPDATE_AUTHOR = "수정자"


# ---------------------------------------------------------------------------
# 팩토리
# ---------------------------------------------------------------------------

def make_board(
    *,
    title: str = DEFAULT_TITLE,
    content: str = DEFAULT_CONTENT,
    author: str = DEFAULT_AUTHOR,
) -> Board:
    """Board 엔티티 인스턴스 (id 없음 — DB 저장 전)."""
    return Board(title=title, content=content, author=author)


def make_board_request(
    *,
    title: str = DEFAULT_TITLE,
    content: str = DEFAULT_CONTENT,
    author: str = DEFAULT_AUTHOR,
) -> dict[str, str]:
    """POST/PUT 요청 본문 dict."""
    return {"title": title, "content": content, "author": author}


# ---------------------------------------------------------------------------
# 픽스처 — 엔진 / 세션 / 클라이언트
# ---------------------------------------------------------------------------

@pytest.fixture()
def test_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db_session(test_engine) -> Generator[Session, None, None]:
    """crud 단위 테스트용 실제 인메모리 세션."""
    with Session(test_engine) as session:
        yield session


@pytest.fixture()
def client(test_engine) -> Generator[TestClient, None, None]:
    """FastAPI TestClient — get_session 을 인메모리 세션으로 오버라이드."""

    def override_get_session() -> Generator[Session, None, None]:
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
