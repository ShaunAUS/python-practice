from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.board import Board


class BoardRepository:
    """게시글 저장소 — Java JpaRepository<Board, Long> 에 대응

    SQLAlchemy 2.0 스타일 세션을 직접 사용.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def find_all(self) -> list[Board]:
        """전체 조회 — Java findAll() 에 대응"""
        return list(self._db.scalars(select(Board)).all())

    def find_by_id(self, board_id: int) -> Board | None:
        """단건 조회 — Java findById() 에 대응"""
        return self._db.get(Board, board_id)

    def save(self, board: Board) -> Board:
        """저장/수정 — Java save() 에 대응"""
        self._db.add(board)
        self._db.commit()
        self._db.refresh(board)
        return board

    def delete(self, board: Board) -> None:
        """삭제 — Java deleteById() 에 대응"""
        self._db.delete(board)
        self._db.commit()
