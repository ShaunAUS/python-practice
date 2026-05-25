from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """앱 설정 — pydantic-settings (FastAPI 공식 권장).

    우선순위(높→낮): 명시 인자 > 환경변수 > .env > 기본값.
    환경변수 접두사 APP_ : APP_DATABASE_URL, APP_SQL_ECHO ...
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        extra="ignore",
    )

    database_url: str = "sqlite:///./board.db"
    sql_echo: bool = False

    app_name: str = "Board API"
    app_description: str = "게시판 CRUD API — FastAPI 공식 구조"
    app_version: str = "1.0.0"


@lru_cache
def get_settings() -> Settings:
    """설정 의존성 (FastAPI 공식 권장) — lru_cache 로 1회만 생성.

    전역 싱글톤 대신 의존성으로 제공 → 테스트에서 dependency_overrides 로 교체 가능.
    """
    return Settings()
