from __future__ import annotations


class BoardNotFoundError(Exception):
    """게시글을 찾을 수 없을 때 발생 — Java exception/BoardNotFoundException 대응."""

    def __init__(self, board_id: int) -> None:
        self.board_id = board_id
        super().__init__(f"게시글을 찾을 수 없습니다. id={board_id}")
