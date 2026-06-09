from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from sqlmodel import Field, SQLModel

from app.models import BoardBase


class BoardCreate(BoardBase):
    """POST/PUT 요청 본문."""


class BoardUpdate(SQLModel):
    """PATCH 부분수정 본문 — 전부 Optional, 보낸 필드만 갱신. 값 보내면 빈 문자열은 거부."""

    title: str | None = Field(default=None, min_length=1)
    content: str | None = Field(default=None, min_length=1)
    author: str | None = Field(default=None, min_length=1)


class BoardPublic(BoardBase):
    """응답 본문 — snake_case → camelCase (createdAt/updatedAt)."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: int
    created_at: datetime
    updated_at: datetime


class Page[T](BaseModel):
    """페이지네이션 응답 — items + 페이지 메타 (snake_case → camelCase: totalPages)."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    items: list[T]
    page: int
    size: int
    total: int
    total_pages: int
