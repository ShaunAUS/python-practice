from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class _CamelModel(BaseModel):
    """camelCase JSON 응답을 위한 공통 베이스 — Java DTO record 에 대응"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class BoardRequest(_CamelModel):
    """POST/PUT 요청 본문 — Java BoardRequest record 에 대응"""

    title: str
    content: str
    author: str


class BoardResponse(_CamelModel):
    """응답 본문 — Java BoardResponse record 에 대응

    DB 컬럼(snake_case) → JSON(camelCase) 자동 변환:
      created_at → createdAt, updated_at → updatedAt
    """

    id: int
    title: str
    content: str
    author: str
    created_at: datetime
    updated_at: datetime
