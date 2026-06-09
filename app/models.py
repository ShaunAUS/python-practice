from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class BoardBase(SQLModel):
    """공유 필드 — Field(min_length=1) 로 빈 문자열 검증(요청 시 400)."""
    # model_validate 여기서 제약조건들 검사
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    author: str = Field(min_length=1)


class Board(BoardBase, table=True):
    """게시글 테이블 — SQLModel(ORM + 스키마 통합)."""

    __tablename__ = "boards"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=_utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": _utcnow},  # UPDATE 시 자동 갱신
    )
    deleted: bool = Field(default=False, nullable=False)  # soft delete 플래그

    def update(self, title: str, content: str, author: str) -> None:
        """필드 일괄 변경 — Java Board.update() 대응."""
        self.title = title
        self.content = content
        self.author = author
