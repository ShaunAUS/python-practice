from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dto.board_schema import BoardRequest, BoardResponse
from app.dto.response_schema import Response
from app.service.board_service import BoardService

router = APIRouter(prefix="/api/boards", tags=["boards"])


def _get_service(db: Session = Depends(get_db)) -> BoardService:
    """BoardService 의존성 — Java @Autowired / 생성자 주입에 대응"""
    return BoardService(db)


@router.post("", response_model=Response[BoardResponse])
def create_board(
    req: BoardRequest,
    service: BoardService = Depends(_get_service),
) -> Response[BoardResponse]:
    board = service.create(req)
    return Response.ok(BoardResponse.model_validate(board))


@router.get("", response_model=Response[list[BoardResponse]])
def list_boards(
    service: BoardService = Depends(_get_service),
) -> Response[list[BoardResponse]]:
    boards = service.find_all()
    return Response.ok([BoardResponse.model_validate(b) for b in boards])


@router.get("/{board_id}", response_model=Response[BoardResponse])
def get_board(
    board_id: int,
    service: BoardService = Depends(_get_service),
) -> Response[BoardResponse]:
    board = service.find_by_id(board_id)
    return Response.ok(BoardResponse.model_validate(board))


@router.put("/{board_id}", response_model=Response[BoardResponse])
def update_board(
    board_id: int,
    req: BoardRequest,
    service: BoardService = Depends(_get_service),
) -> Response[BoardResponse]:
    board = service.update(board_id, req)
    return Response.ok(BoardResponse.model_validate(board))


@router.delete("/{board_id}", status_code=200)
def delete_board(
    board_id: int,
    service: BoardService = Depends(_get_service),
) -> Response:
    service.delete(board_id)
    return Response.ok(None, "삭제되었습니다")
