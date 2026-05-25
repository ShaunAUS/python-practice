from __future__ import annotations

from enum import Enum


class ErrorCode(Enum):
    """에러 코드 정의."""

    BOARD_NOT_FOUND = "게시글을 찾을 수 없습니다."
    VALIDATION_ERROR = "입력값 검증에 실패했습니다."
    INTERNAL_SERVER_ERROR = "서버 내부 오류가 발생했습니다."

    @property
    def message(self) -> str:
        return self.value


class BoardNotFoundError(Exception):
    """게시글을 찾을 수 없을 때 발생."""

    def __init__(self, board_id: int) -> None:
        self.board_id = board_id
        super().__init__(f"게시글을 찾을 수 없습니다. id={board_id}")
