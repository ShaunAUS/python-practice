from __future__ import annotations

from app.core.exceptions import BoardNotFoundError
from app.models import Board
from app.repository import BoardRepository
from app.schemas import BoardCreate, BoardPublic, BoardUpdate, Page


class BoardService:
    """비즈니스 로직 계층 — Java BoardService 대응. 응답 DTO(BoardPublic) 변환까지 담당."""

    def __init__(self, repository: BoardRepository) -> None:
        self.repository = repository

    def create(self, data: BoardCreate) -> BoardPublic:
        board = self.repository.create(Board.model_validate(data))
        return BoardPublic.model_validate(board)

    def find_all(self) -> list[BoardPublic]:
        return [BoardPublic.model_validate(b) for b in self.repository.find_all()]

    def get_page(self, page: int, size: int) -> Page[BoardPublic]:
        offset = (page - 1) * size
        rows = self.repository.find_page(offset, size)
        total = self.repository.count()
        total_pages = (total + size - 1) // size if size else 0
        return Page(
            items=[BoardPublic.model_validate(b) for b in rows],
            page=page,
            size=size,
            total=total,
            total_pages=total_pages,
        )

    def find_by_id(self, board_id: int) -> BoardPublic:
        board = self.repository.find_by_id(board_id)
        if board is None:
            raise BoardNotFoundError(board_id)
        return BoardPublic.model_validate(board)

    def update(self, board_id: int, data: BoardCreate) -> BoardPublic:
        board = self.repository.find_by_id(board_id)
        if board is None:
            raise BoardNotFoundError(board_id)
        board.update(data.title, data.content, data.author)
        return BoardPublic.model_validate(self.repository.save(board))

    def patch(self, board_id: int, data: BoardUpdate) -> BoardPublic:
        board = self.repository.find_by_id(board_id)
        if board is None:
            raise BoardNotFoundError(board_id)

        # DTO에서 실제로 들어온 필드만 골라 갱신 (exclude_unset → PATCH 부분수정)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(board, key, value)
        return BoardPublic.model_validate(self.repository.save(board)) # 파이썬은 @Transactional이 없어서  self.session.commit()로 명시적으로 커밋해야함

    def delete(self, board_id: int) -> None:
        board = self.repository.find_by_id(board_id)
        if board is None:
            raise BoardNotFoundError(board_id)
        self.repository.delete(board)
