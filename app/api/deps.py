from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.core.config import Settings, get_settings
from app.core.db import get_session

# 세션 의존성 별칭 (FastAPI 공식 / tiangolo 템플릿 SessionDep 패턴)
SessionDep = Annotated[Session, Depends(get_session)]

# 설정 의존성 별칭 (FastAPI 공식 settings 패턴) — route 에서 settings 주입 시 사용
SettingsDep = Annotated[Settings, Depends(get_settings)]
