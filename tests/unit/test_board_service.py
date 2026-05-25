"""
test_board_service.py — BoardService 단위 테스트
secretary의 BoardServiceUnitTest.java 에 대응

Java 구조 대응표:
  @ExtendWith(MockitoExtension)  →  unittest.mock.patch + Mock(spec=...)
  @Mock BoardRepository          →  patch("app.service.board_service.BoardRepository")
  @InjectMocks BoardService      →  BoardService(db=MagicMock()) 후 _repo 교체
  @Nested class CreateBoard      →  class TestCreateBoard:
  @DisplayName("...")            →  한글 docstring
  given/when/then 주석           →  # given / # when / # then
  assertThat(x).isEqualTo(y)    →  assert x == y
  assertThatThrownBy(...)        →  pytest.raises(BoardNotFoundError)
"""
from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from app.dto.board_schema import BoardRequest
from app.exception.handlers import BoardNotFoundError
from app.service.board_service import BoardService
from tests.conftest import (
    DEFAULT_AUTHOR,
    DEFAULT_CONTENT,
    DEFAULT_TITLE,
    SECOND_AUTHOR,
    SECOND_CONTENT,
    SECOND_TITLE,
    UPDATE_AUTHOR,
    UPDATE_CONTENT,
    UPDATE_TITLE,
    make_board,
)


# ---------------------------------------------------------------------------
# 헬퍼: Mock repository가 주입된 BoardService 생성
# ---------------------------------------------------------------------------

def _make_service_with_mock_repo() -> tuple[BoardService, Mock]:
    """BoardService 인스턴스와 그 내부 _repo Mock 반환.

    BoardService.__init__가 BoardRepository를 내부에서 생성하므로,
    patch로 BoardRepository 클래스를 가로채고 반환된 인스턴스를 Mock으로 대체.
    Java @Mock BoardRepository + @InjectMocks BoardService 에 대응.
    """
    with patch("app.service.board_service.BoardRepository") as MockRepo:
        mock_repo = MockRepo.return_value  # 생성자가 반환할 mock 인스턴스
        service = BoardService(db=MagicMock())
        # patch 블록 밖에서도 사용할 수 있도록 _repo를 직접 세팅
        service._repo = mock_repo
        return service, mock_repo


# ---------------------------------------------------------------------------
# TestCreateBoard — 게시글 생성
# ---------------------------------------------------------------------------

class TestCreateBoard:
    """createBoard 메서드 단위 테스트 — Java CreateBoard @Nested 에 대응."""

    def test_게시글_생성_후_저장된_엔티티_반환(self) -> None:
        """repository.save가 호출되고 반환된 Board를 그대로 반환한다."""
        # given
        service, mock_repo = _make_service_with_mock_repo()
        saved_board = make_board()
        mock_repo.save.return_value = saved_board
        req = BoardRequest(title=DEFAULT_TITLE, content=DEFAULT_CONTENT, author=DEFAULT_AUTHOR)

        # when
        result = service.create(req)

        # then
        assert result is saved_board
        mock_repo.save.assert_called_once()

    def test_생성_시_repository_save_에_Board_인스턴스_전달(self) -> None:
        """create()가 올바른 필드로 Board 객체를 만들어 save에 전달한다."""
        # given
        service, mock_repo = _make_service_with_mock_repo()
        mock_repo.save.side_effect = lambda b: b  # 전달받은 Board를 그대로 반환
        req = BoardRequest(title=DEFAULT_TITLE, content=DEFAULT_CONTENT, author=DEFAULT_AUTHOR)

        # when
        result = service.create(req)

        # then
        assert result.title == DEFAULT_TITLE
        assert result.content == DEFAULT_CONTENT
        assert result.author == DEFAULT_AUTHOR

    def test_repository_save_정확히_1회_호출(self) -> None:
        """create() 호출당 save가 정확히 한 번 호출된다."""
        # given
        service, mock_repo = _make_service_with_mock_repo()
        mock_repo.save.return_value = make_board()
        req = BoardRequest(title=DEFAULT_TITLE, content=DEFAULT_CONTENT, author=DEFAULT_AUTHOR)

        # when
        service.create(req)

        # then
        assert mock_repo.save.call_count == 1


# ---------------------------------------------------------------------------
# TestGetBoards — 게시글 목록 조회
# ---------------------------------------------------------------------------

class TestGetBoards:
    """find_all 메서드 단위 테스트 — Java GetBoards @Nested 에 대응."""

    def test_전체_목록_반환(self) -> None:
        """repository.find_all 결과를 그대로 반환한다."""
        # given
        service, mock_repo = _make_service_with_mock_repo()
        boards = [make_board(), make_board(title=SECOND_TITLE, content=SECOND_CONTENT, author=SECOND_AUTHOR)]
        mock_repo.find_all.return_value = boards

        # when
        result = service.find_all()

        # then
        assert result == boards
        mock_repo.find_all.assert_called_once()

    def test_게시글_없으면_빈_리스트_반환(self) -> None:
        """게시글이 없을 때 빈 리스트를 반환한다."""
        # given
        service, mock_repo = _make_service_with_mock_repo()
        mock_repo.find_all.return_value = []

        # when
        result = service.find_all()

        # then
        assert result == []


# ---------------------------------------------------------------------------
# TestGetBoardDetail — 게시글 상세 조회
# ---------------------------------------------------------------------------

class TestGetBoardDetail:
    """find_by_id 메서드 단위 테스트 — Java GetBoardDetail @Nested 에 대응."""

    def test_정상_조회_시_Board_반환(self) -> None:
        """repository가 Board를 반환하면 서비스도 동일 Board를 반환한다."""
        # given
        service, mock_repo = _make_service_with_mock_repo()
        board = make_board()
        mock_repo.find_by_id.return_value = board

        # when
        result = service.find_by_id(1)

        # then
        assert result is board
        mock_repo.find_by_id.assert_called_once_with(1)

    def test_존재하지_않는_id_조회_시_BoardNotFoundError_발생(self) -> None:
        """repository가 None을 반환하면 BoardNotFoundError가 발생한다.

        Java: assertThatThrownBy(...).isInstanceOf(BusinessException.class) 에 대응.
        """
        # given
        service, mock_repo = _make_service_with_mock_repo()
        mock_repo.find_by_id.return_value = None

        # when & then
        with pytest.raises(BoardNotFoundError) as exc_info:
            service.find_by_id(999)

        assert exc_info.value.board_id == 999


# ---------------------------------------------------------------------------
# TestUpdateBoard — 게시글 수정
# ---------------------------------------------------------------------------

class TestUpdateBoard:
    """update 메서드 단위 테스트 — Java UpdateBoard @Nested 에 대응."""

    def test_정상_수정_시_필드가_업데이트된다(self) -> None:
        """update()가 Board 필드를 변경하고 save를 호출한다."""
        # given
        service, mock_repo = _make_service_with_mock_repo()
        original = make_board()
        mock_repo.find_by_id.return_value = original
        mock_repo.save.side_effect = lambda b: b
        req = BoardRequest(title=UPDATE_TITLE, content=UPDATE_CONTENT, author=UPDATE_AUTHOR)

        # when
        result = service.update(1, req)

        # then
        assert result.title == UPDATE_TITLE
        assert result.content == UPDATE_CONTENT
        assert result.author == UPDATE_AUTHOR
        mock_repo.save.assert_called_once()

    def test_존재하지_않는_id_수정_시_BoardNotFoundError_발생(self) -> None:
        """find_by_id가 None이면 update()는 BoardNotFoundError를 발생시킨다.

        Java: assertThatThrownBy(...).isInstanceOf(BusinessException.class) 에 대응.
        """
        # given
        service, mock_repo = _make_service_with_mock_repo()
        mock_repo.find_by_id.return_value = None
        req = BoardRequest(title=UPDATE_TITLE, content=UPDATE_CONTENT, author=UPDATE_AUTHOR)

        # when & then
        with pytest.raises(BoardNotFoundError) as exc_info:
            service.update(999, req)

        assert exc_info.value.board_id == 999

    def test_수정_시_repository_save_정확히_1회_호출(self) -> None:
        """update() 호출 시 save가 정확히 한 번 호출된다."""
        # given
        service, mock_repo = _make_service_with_mock_repo()
        mock_repo.find_by_id.return_value = make_board()
        mock_repo.save.side_effect = lambda b: b
        req = BoardRequest(title=UPDATE_TITLE, content=UPDATE_CONTENT, author=UPDATE_AUTHOR)

        # when
        service.update(1, req)

        # then
        assert mock_repo.save.call_count == 1


# ---------------------------------------------------------------------------
# TestDeleteBoard — 게시글 삭제
# ---------------------------------------------------------------------------

class TestDeleteBoard:
    """delete 메서드 단위 테스트 — Java DeleteBoard @Nested 에 대응."""

    def test_정상_삭제_시_repository_delete_호출(self) -> None:
        """delete()는 Board를 조회한 뒤 repository.delete를 호출한다."""
        # given
        service, mock_repo = _make_service_with_mock_repo()
        board = make_board()
        mock_repo.find_by_id.return_value = board

        # when
        service.delete(1)

        # then
        mock_repo.delete.assert_called_once_with(board)

    def test_존재하지_않는_id_삭제_시_BoardNotFoundError_발생(self) -> None:
        """find_by_id가 None이면 delete()는 BoardNotFoundError를 발생시킨다.

        Java: assertThatThrownBy(...).isInstanceOf(BusinessException.class) 에 대응.
        """
        # given
        service, mock_repo = _make_service_with_mock_repo()
        mock_repo.find_by_id.return_value = None

        # when & then
        with pytest.raises(BoardNotFoundError) as exc_info:
            service.delete(999)

        assert exc_info.value.board_id == 999

    def test_삭제_성공_시_repository_delete_정확히_1회_호출(self) -> None:
        """delete() 호출당 repository.delete가 정확히 한 번 호출된다."""
        # given
        service, mock_repo = _make_service_with_mock_repo()
        mock_repo.find_by_id.return_value = make_board()

        # when
        service.delete(1)

        # then
        assert mock_repo.delete.call_count == 1
