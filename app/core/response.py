from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.core.error_code import ErrorCode


class Response[T](BaseModel):
    """API 공통 응답 엔벨로프 — 기존 기능 유지(success/data/message/errorCode)."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    success: bool
    data: T | None = None
    message: str = "성공"
    error_code: str | None = None  # JSON: errorCode

    @classmethod
    def ok(cls, data: T | None = None, message: str = "성공") -> Self:
        return cls(success=True, data=data, message=message, error_code=None)

    @classmethod
    def fail(cls, error_code: ErrorCode, message: str | None = None) -> Self:
        return cls(
            success=False,
            data=None,
            message=message or error_code.message,
            error_code=error_code.name,
        )
