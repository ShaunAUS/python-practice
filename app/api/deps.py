from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.core.config import Settings, get_settings
from app.core.db import get_session
from app.repository import BoardRepository
from app.service import BoardService

# 세션 의존성 별칭 (FastAPI 공식 / tiangolo 템플릿 SessionDep 패턴)
SessionDep = Annotated[Session, Depends(get_session)]

# 설정 의존성 별칭 (FastAPI 공식 settings 패턴)
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_board_repository(session: SessionDep) -> BoardRepository:
    return BoardRepository(session)


RepositoryDep = Annotated[BoardRepository, Depends(get_board_repository)]


def get_board_service(repository: RepositoryDep) -> BoardService:
    return BoardService(repository)


# 자바의 @Service 처럼 자동 주입 안됨, 그래서 Depends로 "이 함수로 만들어라" 를 명시해야함
# 자바의 메서드 추출과 다른점은  FastAPI가 자동으로 호출해서 결과를 주입
# 파이썬은 Jwt 도 이방식으로 구현
ServiceDep = Annotated[BoardService, Depends(get_board_service)]