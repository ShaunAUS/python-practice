from __future__ import annotations

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.core.errors import ErrorCode

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    """API 공통 응답 엔벨로프 — 기존 기능 유지(success/data/message/errorCode)."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    success: bool
    data: Optional[T] = None
    message: str = "성공"
    error_code: Optional[str] = None  # JSON: errorCode

    @classmethod
    def ok(cls, data: Optional[T] = None, message: str = "성공") -> "Response[T]":
        return cls(success=True, data=data, message=message, error_code=None)

    @classmethod
    def fail(cls, error_code: ErrorCode, message: Optional[str] = None) -> "Response[T]":
        return cls(
            success=False,
            data=None,
            message=message or error_code.message,
            error_code=error_code.name,
        )
