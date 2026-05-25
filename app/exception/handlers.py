from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class BoardNotFoundError(Exception):
    """게시글을 찾을 수 없을 때 발생 — Java BoardNotFoundException 에 대응"""

    def __init__(self, board_id: int) -> None:
        self.board_id = board_id
        super().__init__(f"게시글을 찾을 수 없습니다. id={board_id}")


def register_exception_handlers(app: FastAPI) -> None:
    """예외 핸들러 등록 — Java GlobalExceptionHandler @RestControllerAdvice 에 대응"""

    @app.exception_handler(BoardNotFoundError)
    async def board_not_found_handler(
        request: Request, exc: BoardNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "data": None,
                "message": str(exc),
                "errorCode": "BOARD_NOT_FOUND",
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "data": None,
                "message": "입력값 검증에 실패했습니다.",
                "errorCode": "VALIDATION_ERROR",
            },
        )
