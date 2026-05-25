"""
conftest.py — pytest 공용 픽스처 & 팩토리
secretary 의 BoardTestFixture + IntegrationTestSupport + ControllerTestConfig 에 대응

Java 구조 대응표:
  BoardTestFixture.DEFAULT_*   →  이 파일의 DEFAULT_* 상수
  BoardTestFixture.createBoard()  →  make_board() 팩토리 함수
  IntegrationTestSupport (@SpringBootTest + @Transactional)  →  client fixture (get_db 오버라이드)
  entityManager.flush/clear  →  각 테스트마다 독립 engine (function scope)
"""
from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.domain.board import Base, Board
from app.main import app

# ---------------------------------------------------------------------------
# 픽스처 상수 — Java BoardTestFixture.DEFAULT_*/SECOND_* 에 대응
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
# 팩토리 함수 — Java BoardTestFixture.createBoard() / createBoardWithoutId() 에 대응
# ---------------------------------------------------------------------------

def make_board(
    *,
    title: str = DEFAULT_TITLE,
    content: str = DEFAULT_CONTENT,
    author: str = DEFAULT_AUTHOR,
) -> Board:
    """Board 엔티티 인스턴스 생성 (id 없음 — DB 저장 전 상태).

    단위 테스트에서는 Mock 반환값으로, 통합 테스트에서는 DB 저장 대상으로 사용.
    Java BoardTestFixture.createBoardWithoutId() 에 대응.
    """
    now = datetime.now(UTC)
    return Board(
        title=title,
        content=content,
        author=author,
        created_at=now,
        updated_at=now,
    )


def make_board_request(
    *,
    title: str = DEFAULT_TITLE,
    content: str = DEFAULT_CONTENT,
    author: str = DEFAULT_AUTHOR,
) -> dict[str, str]:
    """POST/PUT 요청 본문 dict 생성.

    통합 테스트에서 client.post(..., json=make_board_request()) 형태로 사용.
    """
    return {"title": title, "content": content, "author": author}


# ---------------------------------------------------------------------------
# pytest fixture — DB 엔진 & 세션 (function scope → 테스트마다 독립 DB)
# ---------------------------------------------------------------------------

@pytest.fixture()
def test_engine():
    """인메모리 SQLite 엔진 — Java @Transactional + entityManager.flush/clear 에 대응.

    StaticPool: 같은 프로세스 내 여러 연결이 하나의 인메모리 DB를 공유.
    function scope: 각 테스트마다 테이블을 새로 생성/삭제 → 완전한 격리.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db_session(test_engine) -> Generator[Session, None, None]:
    """SQLAlchemy 세션 픽스처 — 단위 테스트에서 직접 DB 접근 시 사용."""
    TestingSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# ---------------------------------------------------------------------------
# pytest fixture — FastAPI TestClient (get_db 의존성 오버라이드)
# ---------------------------------------------------------------------------

@pytest.fixture()
def client(test_engine) -> Generator[TestClient, None, None]:
    """FastAPI TestClient — Java @WebMvcTest MockMvc 또는 @SpringBootTest + TestRestTemplate 에 대응.

    get_db 의존성을 인메모리 SQLite 세션으로 오버라이드.
    TestClient를 컨텍스트 매니저로 사용하면 lifespan(startup)이 실행되지만,
    get_db가 이미 오버라이드되어 있으므로 실제 board.db는 건드리지 않음.
    """
    TestingSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    # context manager 사용 → lifespan startup/shutdown 실행
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
