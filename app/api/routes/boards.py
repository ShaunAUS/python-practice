from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import ServiceDep
from app.core.response import Response
from app.schemas import BoardCreate, BoardPublic, BoardUpdate, Page

router = APIRouter(prefix="/api/boards", tags=["boards"])


@router.post("", response_model=Response[BoardPublic])
def create_board(body: BoardCreate, service: ServiceDep) -> Response[BoardPublic]:
    return Response.ok(service.create(body))


@router.get("", response_model=Response[list[BoardPublic]])
def list_boards(service: ServiceDep) -> Response[list[BoardPublic]]:
    return Response.ok(service.find_all())


@router.get("/page", response_model=Response[Page[BoardPublic]])
def list_boards_paged(
    service: ServiceDep,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 10,
) -> Response[Page[BoardPublic]]:
    return Response.ok(service.get_page(page, size))


@router.get("/{board_id}", response_model=Response[BoardPublic])
def get_board(board_id: int, service: ServiceDep) -> Response[BoardPublic]:
    return Response.ok(service.find_by_id(board_id))


@router.put("/{board_id}", response_model=Response[BoardPublic])
def update_board(
    board_id: int, body: BoardCreate, service: ServiceDep
) -> Response[BoardPublic]:
    return Response.ok(service.update(board_id, body))


@router.patch("/{board_id}", response_model=Response[BoardPublic])
def patch_board(
    board_id: int, body: BoardUpdate, service: ServiceDep
) -> Response[BoardPublic]:
    return Response.ok(service.patch(board_id, body))


@router.delete("/{board_id}", status_code=200)
def delete_board(board_id: int, service: ServiceDep) -> Response:
    service.delete(board_id)
    return Response.ok(None, "삭제되었습니다")
