# Board API — Python FastAPI (Java Spring Boot 대응 비교용)

## 실행법

```bash
# venv 활성화 후 실행
source .venv/bin/activate
uvicorn app.main:app --reload

# 또는 venv 직접 지정
.venv/bin/uvicorn app.main:app --reload
```

서버 기동 후 → http://localhost:8000/docs (Swagger UI 자동 제공)

---

## 레이어 구조 — Java 대응표

| 파일 | Java 대응 | 역할 |
|---|---|---|
| `app/main.py` | `BoardApplication.java` | FastAPI 앱 생성, 라우터·핸들러 등록, startup 이벤트 |
| `app/database.py` | `application.yml` + JPA 설정 | DB 연결, 세션 팩토리, `get_db()` 의존성 |
| `app/domain/board.py` | `Board.java` (`@Entity`) | SQLAlchemy ORM 모델, 테이블 정의 |
| `app/dto/board_schema.py` | `BoardRequest.java`, `BoardResponse.java` (record) | Pydantic 요청/응답 스키마, camelCase 변환 |
| `app/repository/board_repository.py` | `BoardRepository.java` (`JpaRepository`) | DB CRUD 쿼리 |
| `app/service/board_service.py` | `BoardService.java` (`@Service`) | 비즈니스 로직, 예외 처리 |
| `app/controller/board_controller.py` | `BoardController.java` (`@RestController`) | HTTP 라우팅, 상태코드, 의존성 주입 |
| `app/exception/handlers.py` | `GlobalExceptionHandler.java` (`@RestControllerAdvice`) | 커스텀 예외 → JSON 응답 매핑 |
| `app/dto/response_schema.py` | `Response.java` (`Response<T>`) | API 공통 응답 엔벨로프 (`ok()`/`fail()`) |
| `app/enums/error_code.py` | `ErrorCode.java` | 에러 코드 정의 (`.name`/`.message`) |

---

## API 엔드포인트

### POST /api/boards — 게시글 생성 (200)

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

```bash
curl -s http://localhost:8000/api/boards/1 | jq
```

### PUT /api/boards/{id} — 수정 (200 / 404)

```bash
curl -s -X PUT http://localhost:8000/api/boards/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "수정된 글", "content": "내용 변경", "author": "민재"}' | jq
```

### DELETE /api/boards/{id} — 삭제 (200 / 404)

```bash
curl -s -X DELETE http://localhost:8000/api/boards/1 | jq
```

---

## 공통 응답 형식

모든 응답은 `Response[T]` 엔벨로프(Java `Response<T>` 대응)로 감싸진다.

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

목록 조회는 `data`가 배열, 삭제는 `data`가 `null` + `message`가 `"삭제되었습니다"`.

## 에러 응답

404 (게시글 없음):
```json
{ "success": false, "data": null, "message": "게시글을 찾을 수 없습니다. id=1", "errorCode": "BOARD_NOT_FOUND" }
```

400 (검증 실패 — 필수 필드 누락):
```json
{ "success": false, "data": null, "message": "입력값 검증에 실패했습니다.", "errorCode": "VALIDATION_ERROR" }
```
# python-practice
