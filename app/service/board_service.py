from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.board import Board
from app.dto.board_schema import BoardRequest
from app.exception.handlers import BoardNotFoundError
from app.repository.board_repository import BoardRepository


class BoardService:
    """게시글 비즈니스 로직 — Java @Service BoardService 에 대응"""

    def __init__(self, db: Session) -> None:
        self._repo = BoardRepository(db)

    def create(self, req: BoardRequest) -> Board:
        board = Board(
            title=req.title,
            content=req.content,
            author=req.author,
        )
        return self._repo.save(board)

    def find_all(self) -> list[Board]:
        return self._repo.find_all()

    def find_by_id(self, board_id: int) -> Board:
        board = self._repo.find_by_id(board_id)
        if board is None:
            raise BoardNotFoundError(board_id)
        return board

    def update(self, board_id: int, req: BoardRequest) -> Board:
        board = self.find_by_id(board_id)
        board.title = req.title
        board.content = req.content
        board.author = req.author
        return self._repo.save(board)

    def delete(self, board_id: int) -> None:
        board = self.find_by_id(board_id)
        self._repo.delete(board)
