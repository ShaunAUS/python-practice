"""
test_service.py — BoardService 단위 테스트 (실제 인메모리 세션 사용).

crud.py 를 repository + service 로 분리하면서 테스트 대상도 service 계층으로 변경.
service 가 repository 를 호출하므로 DB 동작까지 한 번에 커버.
not-found → BoardNotFoundError 발생도 단위 테스트로 커버(예외 검증).
"""
from __future__ import annotations

import pytest
from sqlmodel import Session

from app.core.exceptions import BoardNotFoundError
from app.repository import BoardRepository
from app.schemas import BoardCreate
from app.service import BoardService
from tests.conftest import (
    DEFAULT_AUTHOR,
    DEFAULT_CONTENT,
    DEFAULT_TITLE,
    SECOND_AUTHOR,
    SECOND_CONTENT,
    SECOND_TITLE,
    UPDATE_AUTHOR,
    UPDATE_CONTENT,
    UPDATE_TITLE,
)


def _service(session: Session) -> BoardService:
    return BoardService(BoardRepository(session))


def _create(session: Session, **kw):
    data = BoardCreate(
        title=kw.get("title", DEFAULT_TITLE),
        content=kw.get("content", DEFAULT_CONTENT),
        author=kw.get("author", DEFAULT_AUTHOR),
    )
    return _service(session).create(data)


class TestCreate:
    def test_생성_시_id_발급_및_필드_저장(self, db_session: Session) -> None:
        board = _create(db_session)
        assert board.id is not None
        assert board.id >= 1
        assert board.title == DEFAULT_TITLE
        assert board.content == DEFAULT_CONTENT
        assert board.author == DEFAULT_AUTHOR

    def test_생성_시_타임스탬프_자동_설정(self, db_session: Session) -> None:
        board = _create(db_session)
        assert board.created_at is not None
        assert board.updated_at is not None


class TestGetAll:
    def test_전체_목록_반환(self, db_session: Session) -> None:
        _create(db_session)
        _create(db_session, title=SECOND_TITLE, content=SECOND_CONTENT, author=SECOND_AUTHOR)
        assert len(_service(db_session).find_all()) == 2

    def test_게시글_없으면_빈_리스트(self, db_session: Session) -> None:
        assert _service(db_session).find_all() == []


class TestGet:
    def test_정상_조회(self, db_session: Session) -> None:
        created = _create(db_session)
        found = _service(db_session).find_by_id(created.id)
        assert found.id == created.id

    def test_없는_id_는_예외(self, db_session: Session) -> None:
        with pytest.raises(BoardNotFoundError):
            _service(db_session).find_by_id(999)


class TestUpdate:
    def test_필드_업데이트(self, db_session: Session) -> None:
        board = _create(db_session)
        updated = _service(db_session).update(
            board.id,
            BoardCreate(title=UPDATE_TITLE, content=UPDATE_CONTENT, author=UPDATE_AUTHOR),
        )
        assert updated.title == UPDATE_TITLE
        assert updated.content == UPDATE_CONTENT
        assert updated.author == UPDATE_AUTHOR

    def test_없는_id_수정_시_예외(self, db_session: Session) -> None:
        with pytest.raises(BoardNotFoundError):
            _service(db_session).update(
                999,
                BoardCreate(title=UPDATE_TITLE, content=UPDATE_CONTENT, author=UPDATE_AUTHOR),
            )


class TestDelete:
    def test_삭제_후_조회_불가(self, db_session: Session) -> None:
        board = _create(db_session)
        board_id = board.id
        _service(db_session).delete(board_id)
        with pytest.raises(BoardNotFoundError):
            _service(db_session).find_by_id(board_id)

    def test_없는_id_삭제_시_예외(self, db_session: Session) -> None:
        with pytest.raises(BoardNotFoundError):
            _service(db_session).delete(999)

    def test_soft_delete_행은_DB에_남고_deleted_True(self, db_session: Session) -> None:
        from app.models import Board

        created = _create(db_session)
        board_id = created.id
        _service(db_session).delete(board_id)
        # PK 직접 조회(필터 우회) → 행은 남아있고 deleted=True 여야 함
        raw = db_session.get(Board, board_id)
        assert raw is not None
        assert raw.deleted is True
