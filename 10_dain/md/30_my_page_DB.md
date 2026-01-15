# 마이페이지 DB 연동 및 유저 액션 구현 기록 (my_page_DB.md)

## 1. 개요
*   **목표**: 
    1. 사용자의 정책 카드 스와이프(Like/Pass) 액션을 DB에 저장.
    2. 저장된 데이터를 기반으로 마이페이지에서 '찜한 정책' 목록을 표시.
    3. Like/Pass 데이터를 분석하여 마이페이지 내 '관심 키워드 트렌드(차트)' 실시간 반영.
*   **관련 파일**:
    *   `models.py`: DB 테이블 정의
    *   `routers/mypage.py`: 마이페이지 관련 API (액션 저장, 조회, 통계)
    *   `static/script.js`: 프론트엔드 액션 처리 및 API 호출
    *   `templates/mypage.html`: 마이페이지 UI

---

## 2. 작업 내역 및 계획

### Step 1: DB 테이블 정의 (`models.py`)
- [x] `UserAction` 테이블 추가 (완료)
    - 컬럼: `id`, `user_email`, `policy_id`, `type` (like/pass), `created_at`

### Step 2: API 엔드포인트 구현 (`routers/mypage.py`)
- [x] `POST /api/mypage/action`: 사용자 스와이프 액션(Like/Pass) 저장
- [x] `GET /api/mypage/likes`: 사용자가 Like한 정책 목록 조회 (Policy 테이블 조인)
- [x] `GET /api/mypage/stats`: 사용자 관심 카테고리 통계 데이터 반환 (차트용)

### Step 3: 라우터 등록 (`main.py`)
- [x] `main.py`에 `routers/mypage.py` 등록 (`app.include_router(...)`)

### Step 4: 프론트엔드 연동 (`script.js`)
- [x] `CardSwiper` 클래스 수정
    - 스와이프(`right`/`left`) 발생 시 `/api/mypage/action` API 호출
    - 로그인 상태 체크 후 DB 저장 로직 추가
- [x] 마이페이지 로드 로직 수정
    - `/api/mypage/likes` 호출하여 찜한 정책 실제 데이터 렌더링
    - `/api/mypage/stats` 호출하여 Chart.js 데이터 실시간 업데이트

---

## 3. 상세 구현 기록 (Timeline)

### [1] DB 테이블 정의 (`models.py`)
- **작업 내용**: 사용자 행동(좋아요/패스) 저장을 위한 `UserAction` 테이블 추가
- **코드**:
  ```python
  from datetime import datetime

  class UserAction(Base):
      __tablename__ = "users_action"

      id = Column(Integer, primary_key=True, autoincrement=True)
      user_email = Column(String, nullable=False, index=True) 
      policy_id = Column(Integer, nullable=False)
      type = Column(String, nullable=False) # 'like' or 'pass'
      created_at = Column(DateTime, default=datetime.now)
  ```

### [2] API 엔드포인트 구현 (`routers/mypage.py`)
- **작업 내용**: `mypage.py` 파일 생성 및 3가지 핵심 API 구현
    1. `POST /api/mypage/action`: 유저 액션 저장 (Like/Pass)
    2. `GET /api/mypage/likes`: 내가 Like한 정책 목록 조회 (Policy 테이블 조인)
    3. `GET /api/mypage/stats`: Like/Pass 데이터를 집계하여 차트용 통계 반환
- **특이사항**: 기존의 빈 파일(`routers/ mypage.py`) 이름 수정하여 사용함.

### [3] 라우터 등록 및 코드 정리 (`main.py` & `models.py`)
- **작업 내용**: 
    - `main.py`에 `routers/mypage.py` 등록 (`app.include_router(mypage.router)`)
    - 기존의 임시 마이페이지 핸들러 주석 처리 (**-> 이후 404 오류 원인이 되어 재복구함**)
    - `models.py`에서 중복 정의된 `provider` 컬럼 코드 정리

### [4] 프론트엔드 연동 (`script.js`)
- **작업 내용 1: 스와이프 저장 연동**
    - `CardSwiper` 클래스 내 `swipeCard` 메서드 수정.
    - 스와이프 완료(DOM 제거) 시점에 `/api/mypage/action` API 호출하여 DB에 저장.
    ```javascript
    // (script.js 수정 내역)
    fetch('/api/mypage/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_email: userEmail, policy_id: policyId, type: actionType })
    })
    ```
- **작업 내용 2: 마이페이지 렌더링**
    - 마이페이지 로드 시 더미 데이터 대신 서버 API 호출.
    - `/api/mypage/likes`: 찜한 정책 목록 표시.
    - `/api/mypage/stats`: 차트 데이터 업데이트.

---

## 4. 트러블 슈팅 (오류 수정 기록)

### [오류 1] 마이페이지 404 Not Found
- **현상**: `/mypage.html` 접속 시 404 에러 페이지가 뜸.
- **원인**: `main.py`에서 라우터를 통합하는 과정에서, HTML 페이지를 서빙하는 핸들러(`@app.get("/mypage.html")`)를 중복으로 오인하여 주석 처리해버림. `routers/mypage.py`는 API(`prefix="/api/mypage"`)만 담당하고 페이지 서빙 로직이 없었기 때문에 연결 고리가 끊어짐.
- **조치**: `main.py`의 주석 처리된 코드를 다시 활성화.
- **수정 코드 (`main.py`)**:
    ```python
    # [2] 마이 페이지 (복구: API 라우터와 별개로 HTML 페이지 서빙 필요)
    @app.get("/mypage.html")
    async def read_mypage(request: Request):
        return templates.TemplateResponse("mypage.html", {"request": request})
    ```
