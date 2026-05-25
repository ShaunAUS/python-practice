from __future__ import annotations

from fastapi import APIRouter

from app import crud
from app.api.deps import SessionDep
from app.core.errors import BoardNotFoundError
from app.core.response import Response
from app.models import BoardCreate, BoardPublic

router = APIRouter(prefix="/api/boards", tags=["boards"])


@router.post("", response_model=Response[BoardPublic])
def create_board(body: BoardCreate, session: SessionDep) -> Response[BoardPublic]:
    board = crud.create_board(session, body)
    return Response.ok(BoardPublic.model_validate(board))


@router.get("", response_model=Response[list[BoardPublic]])
def list_boards(session: SessionDep) -> Response[list[BoardPublic]]:
    boards = crud.get_boards(session)
    return Response.ok([BoardPublic.model_validate(b) for b in boards])


@router.get("/{board_id}", response_model=Response[BoardPublic])
def get_board(board_id: int, session: SessionDep) -> Response[BoardPublic]:
    board = crud.get_board(session, board_id)
    if board is None:
        raise BoardNotFoundError(board_id)
    return Response.ok(BoardPublic.model_validate(board))


@router.put("/{board_id}", response_model=Response[BoardPublic])
def update_board(
    board_id: int, body: BoardCreate, session: SessionDep
) -> Response[BoardPublic]:
    board = crud.get_board(session, board_id)
    if board is None:
        raise BoardNotFoundError(board_id)
    board = crud.update_board(session, board, body)
    return Response.ok(BoardPublic.model_validate(board))


@router.delete("/{board_id}", status_code=200)
def delete_board(board_id: int, session: SessionDep) -> Response:
    board = crud.get_board(session, board_id)
    if board is None:
        raise BoardNotFoundError(board_id)
    crud.delete_board(session, board)
    return Response.ok(None, "삭제되었습니다")
