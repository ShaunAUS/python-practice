"""
test_board_api.py — Board API 통합 테스트
secretary의 BoardIntegrationTest.java + Controller 테스트 에 대응

Java 구조 대응표:
  @SpringBootTest + IntegrationTestSupport  →  client fixture (TestClient + 인메모리 SQLite)
  entityManager.flush/clear                 →  각 요청이 별도 HTTP round-trip → 세션 분리
  @Nested class CreateBoard                 →  class TestCreateBoard:
  @DisplayName("...")                       →  한글 docstring
  given/when/then 주석                      →  # given / # when / # then
  assertThat(response.body)                →  assert response.json()[...] == ...
  assertThat(status).isEqualTo(404)        →  assert response.status_code == 404
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

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
    make_board_request,
)


# ---------------------------------------------------------------------------
# TestCreateBoard — POST /api/boards
# ---------------------------------------------------------------------------

class TestCreateBoard:
    """게시글 생성 API 통합 테스트 — Java CreateBoard @Nested 에 대응."""

    def test_게시글_생성_200_응답_및_camelCase_JSON(self, client: TestClient) -> None:
        """POST /api/boards → 200 + camelCase 응답 필드(createdAt, updatedAt) 검증.

        chamchi 방식: 모든 응답 Response 엔벨로프 + 기본 200.
        """
        # given
        payload = make_board_request()

        # when
        response = client.post("/api/boards", json=payload)

        # then
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["title"] == DEFAULT_TITLE
        assert body["data"]["content"] == DEFAULT_CONTENT
        assert body["data"]["author"] == DEFAULT_AUTHOR
        assert "id" in body["data"]
        assert isinstance(body["data"]["id"], int)
        # camelCase 검증 — snake_case 키가 없어야 한다
        assert "createdAt" in body["data"]
        assert "updatedAt" in body["data"]
        assert "created_at" not in body["data"]
        assert "updated_at" not in body["data"]

    def test_생성된_게시글_id_는_양수(self, client: TestClient) -> None:
        """자동 증가 id가 1 이상의 정수로 반환된다."""
        # given
        payload = make_board_request()

        # when
        response = client.post("/api/boards", json=payload)

        # then
        assert response.status_code == 200
        assert response.json()["data"]["id"] >= 1


# ---------------------------------------------------------------------------
# TestGetBoards — GET /api/boards
# ---------------------------------------------------------------------------

class TestGetBoards:
    """게시글 목록 조회 API 통합 테스트 — Java GetBoards @Nested 에 대응."""

    def test_게시글_목록_조회(self, client: TestClient) -> None:
        """두 개 생성 후 GET → 목록에 두 개 포함 확인."""
        # given
        client.post("/api/boards", json=make_board_request())
        client.post(
            "/api/boards",
            json=make_board_request(title=SECOND_TITLE, content=SECOND_CONTENT, author=SECOND_AUTHOR),
        )

        # when
        response = client.get("/api/boards")

        # then
        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]) == 2

    def test_게시글_없으면_빈_목록_반환(self, client: TestClient) -> None:
        """게시글이 없을 때 빈 배열 반환."""
        # when
        response = client.get("/api/boards")

        # then
        assert response.status_code == 200
        body = response.json()
        assert body["data"] == []

    def test_목록_항목에_camelCase_필드_포함(self, client: TestClient) -> None:
        """목록 응답의 각 항목도 camelCase 키를 가진다."""
        # given
        client.post("/api/boards", json=make_board_request())

        # when
        response = client.get("/api/boards")

        # then
        assert response.status_code == 200
        body = response.json()
        item = body["data"][0]
        assert "createdAt" in item
        assert "updatedAt" in item


# ---------------------------------------------------------------------------
# TestGetBoardDetail — GET /api/boards/{id}
# ---------------------------------------------------------------------------

class TestGetBoardDetail:
    """게시글 상세 조회 API 통합 테스트 — Java GetBoardDetail @Nested 에 대응."""

    def test_정상_상세_조회(self, client: TestClient) -> None:
        """생성 후 상세 조회 → 동일 데이터 반환."""
        # given
        created = client.post("/api/boards", json=make_board_request()).json()
        board_id = created["data"]["id"]

        # when
        response = client.get(f"/api/boards/{board_id}")

        # then
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["id"] == board_id
        assert body["data"]["title"] == DEFAULT_TITLE
        assert body["data"]["content"] == DEFAULT_CONTENT
        assert body["data"]["author"] == DEFAULT_AUTHOR

    def test_존재하지_않는_id_조회_시_404(self, client: TestClient) -> None:
        """없는 id 조회 → 404 + 엔벨로프 에러 형식 검증."""
        # when
        response = client.get("/api/boards/999")

        # then
        assert response.status_code == 404
        body = response.json()
        assert body["success"] is False
        assert body["errorCode"] == "BOARD_NOT_FOUND"
        assert "게시글을 찾을 수 없습니다" in body["message"]
        assert "999" in body["message"]


# ---------------------------------------------------------------------------
# TestUpdateBoard — PUT /api/boards/{id}
# ---------------------------------------------------------------------------

class TestUpdateBoard:
    """게시글 수정 API 통합 테스트 — Java UpdateBoard @Nested 에 대응."""

    def test_정상_수정(self, client: TestClient) -> None:
        """생성 후 수정 → 변경된 필드 반환."""
        # given
        created = client.post("/api/boards", json=make_board_request()).json()
        board_id = created["data"]["id"]
        update_payload = make_board_request(
            title=UPDATE_TITLE, content=UPDATE_CONTENT, author=UPDATE_AUTHOR
        )

        # when
        response = client.put(f"/api/boards/{board_id}", json=update_payload)

        # then
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["id"] == board_id
        assert body["data"]["title"] == UPDATE_TITLE
        assert body["data"]["content"] == UPDATE_CONTENT
        assert body["data"]["author"] == UPDATE_AUTHOR

    def test_존재하지_않는_id_수정_시_404(self, client: TestClient) -> None:
        """없는 id 수정 → 404."""
        # given
        update_payload = make_board_request(title=UPDATE_TITLE, content=UPDATE_CONTENT, author=UPDATE_AUTHOR)

        # when
        response = client.put("/api/boards/999", json=update_payload)

        # then
        assert response.status_code == 404
        body = response.json()
        assert body["success"] is False
        assert body["errorCode"] == "BOARD_NOT_FOUND"
        assert "999" in body["message"]

    def test_수정_후_GET_으로_변경_확인(self, client: TestClient) -> None:
        """수정 후 GET으로 재조회 시 변경된 내용이 반영된다.

        Java: entityManager.flush/clear 후 재조회 패턴 에 대응.
        """
        # given
        board_id = client.post("/api/boards", json=make_board_request()).json()["data"]["id"]
        client.put(
            f"/api/boards/{board_id}",
            json=make_board_request(title=UPDATE_TITLE, content=UPDATE_CONTENT, author=UPDATE_AUTHOR),
        )

        # when
        response = client.get(f"/api/boards/{board_id}")

        # then
        assert response.status_code == 200
        assert response.json()["data"]["title"] == UPDATE_TITLE


# ---------------------------------------------------------------------------
# TestDeleteBoard — DELETE /api/boards/{id}
# ---------------------------------------------------------------------------

class TestDeleteBoard:
    """게시글 삭제 API 통합 테스트 — Java DeleteBoard @Nested 에 대응."""

    def test_정상_삭제_200_응답(self, client: TestClient) -> None:
        """생성 후 삭제 → 200 + 엔벨로프 응답."""
        # given
        board_id = client.post("/api/boards", json=make_board_request()).json()["data"]["id"]

        # when
        response = client.delete(f"/api/boards/{board_id}")

        # then
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True

    def test_삭제_후_조회_시_404(self, client: TestClient) -> None:
        """삭제 후 같은 id 조회 → 404.

        Java: boardRepository.findById(id).isEmpty() 검증 에 대응.
        """
        # given
        board_id = client.post("/api/boards", json=make_board_request()).json()["data"]["id"]
        client.delete(f"/api/boards/{board_id}")

        # when
        response = client.get(f"/api/boards/{board_id}")

        # then
        assert response.status_code == 404

    def test_존재하지_않는_id_삭제_시_404(self, client: TestClient) -> None:
        """없는 id 삭제 → 404."""
        # when
        response = client.delete("/api/boards/999")

        # then
        assert response.status_code == 404
        body = response.json()
        assert body["success"] is False
        assert body["errorCode"] == "BOARD_NOT_FOUND"
        assert "999" in body["message"]

    def test_삭제_후_목록에서_제거_확인(self, client: TestClient) -> None:
        """두 개 생성 후 하나 삭제 → 목록에 하나만 남는다."""
        # given
        id1 = client.post("/api/boards", json=make_board_request()).json()["data"]["id"]
        client.post(
            "/api/boards",
            json=make_board_request(title=SECOND_TITLE, content=SECOND_CONTENT, author=SECOND_AUTHOR),
        )

        # when
        client.delete(f"/api/boards/{id1}")
        response = client.get("/api/boards")

        # then
        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]) == 1
        assert body["data"][0]["title"] == SECOND_TITLE


# ---------------------------------------------------------------------------
# TestValidation — 400 Bad Request (검증 실패)
# ---------------------------------------------------------------------------

class TestValidation:
    """Pydantic 유효성 검사 실패 테스트.

    주의: Pydantic v2는 빈 문자열("")을 str로 허용.
    필수 필드 누락(title 키 자체가 없음) 시 400이 발생.
    Java: @Valid + MethodArgumentNotValidException 에 대응.
    """

    def test_title_누락_시_400(self, client: TestClient) -> None:
        """title 필드 없이 POST → 400 Bad Request."""
        # given
        payload = {"content": DEFAULT_CONTENT, "author": DEFAULT_AUTHOR}  # title 누락

        # when
        response = client.post("/api/boards", json=payload)

        # then
        assert response.status_code == 400
        body = response.json()
        assert body["success"] is False
        assert body["errorCode"] == "VALIDATION_ERROR"

    def test_content_누락_시_400(self, client: TestClient) -> None:
        """content 필드 없이 POST → 400."""
        # given
        payload = {"title": DEFAULT_TITLE, "author": DEFAULT_AUTHOR}

        # when
        response = client.post("/api/boards", json=payload)

        # then
        assert response.status_code == 400
        body = response.json()
        assert body["success"] is False
        assert body["errorCode"] == "VALIDATION_ERROR"

    def test_author_누락_시_400(self, client: TestClient) -> None:
        """author 필드 없이 POST → 400."""
        # given
        payload = {"title": DEFAULT_TITLE, "content": DEFAULT_CONTENT}

        # when
        response = client.post("/api/boards", json=payload)

        # then
        assert response.status_code == 400
        body = response.json()
        assert body["success"] is False
        assert body["errorCode"] == "VALIDATION_ERROR"

    def test_빈_요청_본문_400(self, client: TestClient) -> None:
        """빈 JSON {} 으로 POST → 400."""
        # when
        response = client.post("/api/boards", json={})

        # then
        assert response.status_code == 400
        body = response.json()
        assert body["success"] is False
        assert body["errorCode"] == "VALIDATION_ERROR"

    def test_빈_문자열_title_400(self, client: TestClient) -> None:
        """title 이 빈 문자열 "" 이면 400 — Java @NotBlank(min_length=1) 대응.

        H1 적용 전엔 bare str 라 ""가 통과해 Java 와 동작이 달랐음.
        """
        # when
        response = client.post("/api/boards", json=make_board_request(title=""))

        # then
        assert response.status_code == 400
        assert response.json()["errorCode"] == "VALIDATION_ERROR"

    def test_빈_문자열_content_400(self, client: TestClient) -> None:
        """content 가 빈 문자열이면 400."""
        # when
        response = client.post("/api/boards", json=make_board_request(content=""))

        # then
        assert response.status_code == 400
        assert response.json()["errorCode"] == "VALIDATION_ERROR"

    def test_빈_문자열_author_400(self, client: TestClient) -> None:
        """author 가 빈 문자열이면 400."""
        # when
        response = client.post("/api/boards", json=make_board_request(author=""))

        # then
        assert response.status_code == 400
        assert response.json()["errorCode"] == "VALIDATION_ERROR"
