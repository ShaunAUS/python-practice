from __future__ import annotations

from enum import Enum


class ErrorCode(Enum):
    """에러 코드 정의 — Java enums/ErrorCode 대응."""

    BOARD_NOT_FOUND = "게시글을 찾을 수 없습니다."
    VALIDATION_ERROR = "입력값 검증에 실패했습니다."
    INTERNAL_SERVER_ERROR = "서버 내부 오류가 발생했습니다."

    @property
    def message(self) -> str:
        return self.value
