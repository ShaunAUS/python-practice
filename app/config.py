from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """앱 설정 — Java application.yml + @ConfigurationProperties 에 대응.

    우선순위(높→낮): 환경변수 > .env 파일 > 아래 기본값.
    Spring 의 profile/환경변수 override 와 동일한 동작.

    환경변수 접두사 APP_ 사용 → APP_DATABASE_URL, APP_SQL_ECHO ...
    (예: 운영에서 `export APP_DATABASE_URL=...` 로 .env 덮어쓰기)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        extra="ignore",  # 정의 안 된 환경변수 무시
    )

    # DB 연결 — Java spring.datasource.url 에 대응
    database_url: str = "sqlite:///./board.db"
    # SQL 로그 출력 — Java spring.jpa.show-sql 에 대응
    sql_echo: bool = False

    # 앱 메타 — Java spring.application.name / FastAPI() 인자에 대응
    app_name: str = "Board API"
    app_description: str = "게시판 CRUD API — Java Spring Boot BoardApplication 에 대응"
    app_version: str = "1.0.0"


# import 시 1회 생성되는 싱글톤 — Java 스프링 컨텍스트의 설정 빈에 대응
settings = Settings()
