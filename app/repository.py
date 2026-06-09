from __future__ import annotations

from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Board


class BoardRepository:
    """DB 접근 계층 — Java BoardRepository(JpaRepository) 대응."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, board: Board) -> Board:
        self.session.add(board)  # 트랜잭션 자동 시작 (첫 SQL 시점)
        self.session.commit()  # 여기서 커밋 + 트랜잭션 끝
        self.session.refresh(board)  # 새 트랜잭션에서 다시 조회해서 기존board 객체에 넣어준다
        return board

    def find_all(self) -> list[Board]:
        return list(
            self.session.exec(
                select(Board)
                .where(Board.deleted == False)
            ).all()
        )

    def count(self) -> int:
        return self.session.exec(
            select(func.count())
            .select_from(Board)
            .where(Board.deleted == False)
        ).one()

    def find_page(self, offset: int, limit: int) -> list[Board]:
        return list(
            self.session.exec(
                select(Board)
                .where(Board.deleted == False)
                .order_by(Board.id)
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def find_by_id(self, board_id: int) -> Board | None:
        return self.session.exec(
            select(Board)
            .where(Board.id == board_id, Board.deleted == False)
        ).first()

    def save(self, board: Board) -> Board:
        self.session.add(board)
        self.session.commit()
        self.session.refresh(board)
        return board

    def delete(self, board: Board) -> None:
        board.deleted = True  # 물리 삭제 대신 플래그만 변경 (soft delete)
        self.session.add(board) # 파이썬도 더티체킹 가능, 그래서 이건 제거가능
        self.session.commit() # 이건제거 x , 파이썬 더티체킹은 상태추적만해줌, 반영 x
