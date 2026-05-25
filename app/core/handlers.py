from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.errors import BoardNotFoundError, ErrorCode
from app.core.response import Response


def _envelope(error_code: ErrorCode, message: str | None = None) -> dict:
    """에러 응답을 공통 Response.fail() 엔벨로프(camelCase)로 직렬화."""
    return Response.fail(error_code, message).model_dump(by_alias=True)


def register_exception_handlers(app: FastAPI) -> None:
    """예외 → 엔벨로프 JSON 매핑 등록."""

    @app.exception_handler(BoardNotFoundError)
    async def board_not_found_handler(
        request: Request, exc: BoardNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content=_envelope(ErrorCode.BOARD_NOT_FOUND, str(exc)),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content=_envelope(ErrorCode.VALIDATION_ERROR),
        )

    @app.exception_handler(Exception)
    async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=_envelope(ErrorCode.INTERNAL_SERVER_ERROR),
        )
