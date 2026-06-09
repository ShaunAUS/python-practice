# Board API — Python FastAPI (공식 권장 구조)

게시판 CRUD REST API. FastAPI 공식 권장 방식 + 최신 스택(SQLModel, pydantic-settings)으로 작성.
구조는 tiangolo `full-stack-fastapi-template` 을 따름.

## 실행법

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

서버 기동 후 → http://localhost:8000/api/boards

> Swagger UI(`/docs`)·OpenAPI(`/openapi.json`)는 비활성화됨 (`main.py` `openapi_url=None`).

설정은 `.env`(또는 환경변수 `APP_*`)로 주입 — `app/core/config.py` 참고.

---

## 구조 (FastAPI 공식)

| 파일 | 역할 |
|---|---|
| `app/main.py` | FastAPI 앱 생성, lifespan(테이블 생성), 라우터·예외 핸들러 등록 |
| `app/models.py` | SQLModel — `BoardBase` / `Board`(table) / `BoardCreate` / `BoardPublic` (ORM+스키마 통합) |
| `app/crud.py` | DB CRUD 함수 (create/get/get_boards/update/delete) |
| `app/api/deps.py` | `SessionDep` — 세션 의존성 별칭 |
| `app/api/routes/boards.py` | `APIRouter` 엔드포인트 |
| `app/core/config.py` | `pydantic-settings` 설정 |
| `app/core/db.py` | engine, `get_session`, `init_db` |
| `app/core/response.py` | `Response[T]` 공통 응답 엔벨로프 |
| `app/core/errors.py` | `ErrorCode` enum, `BoardNotFoundError` |
| `app/core/handlers.py` | 예외 → 엔벨로프 JSON 매핑 |

레이어드(controller/service/repository) 대신 공식 방식: **route → crud**. 비즈니스 규칙(not-found→404)은 route 에서 처리.

---

## API 엔드포인트

### POST /api/boards — 생성 (200)
```bash
curl -s -X POST http://localhost:8000/api/boards \
  -H "Content-Type: application/json" \
  -d '{"title": "첫 글", "content": "안녕하세요", "author": "민재"}' | jq
```

### GET /api/boards — 전체 목록 (200)
```bash
curl -s http://localhost:8000/api/boards | jq
```

### GET /api/boards/{id} — 단건 조회 (200 / 404)
### PUT /api/boards/{id} — 수정 (200 / 404)
### DELETE /api/boards/{id} — 삭제 (200 / 404)

---

## 공통 응답 형식

모든 응답은 `Response[T]` 엔벨로프로 감싸진다.

성공:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "첫 글",
    "content": "안녕하세요",
    "author": "민재",
    "createdAt": "2026-05-25T17:00:00",
    "updatedAt": "2026-05-25T17:00:00"
  },
  "message": "성공",
  "errorCode": null
}
```

목록 조회는 `data` 가 배열, 삭제는 `data` 가 `null` + `message` 가 `"삭제되었습니다"`.

## 에러 응답

404 (게시글 없음):
```json
{ "success": false, "data": null, "message": "게시글을 찾을 수 없습니다. id=1", "errorCode": "BOARD_NOT_FOUND" }
```

400 (검증 실패 — 빈 문자열/필수 필드 누락):
```json
{ "success": false, "data": null, "message": "입력값 검증에 실패했습니다.", "errorCode": "VALIDATION_ERROR" }
```

---

## 테스트

```bash
pytest -q
```

- `tests/unit/test_crud.py` — crud 함수 (실제 인메모리 SQLite 세션)
- `tests/integration/test_board_api.py` — API 계약 (TestClient + `dependency_overrides`)
