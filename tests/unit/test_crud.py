"""
test_crud.py — crud 함수 단위 테스트 (실제 인메모리 세션 사용).

FastAPI 공식 방식: crud 는 실제 세션으로 테스트(얇은 DB 코드라 mock 이득 적음).
not-found → 404 동작은 통합 테스트(test_board_api)가 커버.
"""
from __future__ import annotations

from sqlmodel import Session

from app import crud
from app.models import BoardCreate
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


def _create(session: Session, **kw) -> "crud.Board":
    data = BoardCreate(
        title=kw.get("title", DEFAULT_TITLE),
        content=kw.get("content", DEFAULT_CONTENT),
        author=kw.get("author", DEFAULT_AUTHOR),
    )
    return crud.create_board(session, data)


class TestCreateBoard:
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


class TestGetBoards:
    def test_전체_목록_반환(self, db_session: Session) -> None:
        _create(db_session)
        _create(db_session, title=SECOND_TITLE, content=SECOND_CONTENT, author=SECOND_AUTHOR)
        boards = crud.get_boards(db_session)
        assert len(boards) == 2

    def test_게시글_없으면_빈_리스트(self, db_session: Session) -> None:
        assert crud.get_boards(db_session) == []


class TestGetBoard:
    def test_정상_조회(self, db_session: Session) -> None:
        created = _create(db_session)
        found = crud.get_board(db_session, created.id)
        assert found is not None
        assert found.id == created.id

    def test_없는_id_는_None(self, db_session: Session) -> None:
        assert crud.get_board(db_session, 999) is None


class TestUpdateBoard:
    def test_필드_업데이트(self, db_session: Session) -> None:
        board = _create(db_session)
        updated = crud.update_board(
            db_session,
            board,
            BoardCreate(title=UPDATE_TITLE, content=UPDATE_CONTENT, author=UPDATE_AUTHOR),
        )
        assert updated.title == UPDATE_TITLE
        assert updated.content == UPDATE_CONTENT
        assert updated.author == UPDATE_AUTHOR


class TestDeleteBoard:
    def test_삭제_후_조회_불가(self, db_session: Session) -> None:
        board = _create(db_session)
        board_id = board.id
        crud.delete_board(db_session, board)
        assert crud.get_board(db_session, board_id) is None
