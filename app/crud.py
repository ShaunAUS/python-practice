from __future__ import annotations

from sqlmodel import Session, select

from app.models import Board, BoardCreate


def create_board(session: Session, data: BoardCreate) -> Board:
    board = Board.model_validate(data)
    session.add(board)
    session.commit()
    session.refresh(board)
    return board


def get_boards(session: Session) -> list[Board]:
    return list(session.exec(select(Board)).all())


def get_board(session: Session, board_id: int) -> Board | None:
    return session.get(Board, board_id)


def update_board(session: Session, board: Board, data: BoardCreate) -> Board:
    board.title = data.title
    board.content = data.content
    board.author = data.author
    session.add(board)
    session.commit()
    session.refresh(board)
    return board


def delete_board(session: Session, board: Board) -> None:
    session.delete(board)
    session.commit()
