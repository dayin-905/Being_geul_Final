# [Task] 관리자 페이지 고도화 체크리스트

## 1. 보안 및 초기 설정 (Priority: High)
- [x] **초기 관리자 계정 생성기** (`create_admin.py`) 
    - [x] `email`, `password`, `name` 입력을 받아 DB에 User 생성 (또는 업데이트).
    - [x] `subscription_level`을 'admin'으로 설정.
- [x] **로그인 페이지(`login.html`) 개선**
    - [x] Form Input: `username` -> `email`로 변경.
    - [x] UI: 에러 메시지 표시 영역 디자인 개선.
- [x] **관리자 로그인 로직(`routers/admin.py`) 교체**
    - [x] 기존 하드코딩(`ADMIN_CREDENTIALS`) 제거.
    - [x] `db.query(User).filter(email=...)` 로직 적용.
    - [x] 비밀번호 해싱 검증 (auth.py의 `verify_password` 활용).
    - [x] 세션/쿠키에 암호화된 토큰(또는 안전한 식별자) 저장.
    - [x] **권한 체크 함수(`get_current_admin`)** 구현 및 라우터 의존성(`Depends`) 적용.


## 2. 유저 관리 강화
- [x] **유저 수정 모달(`users.html`)**
    - [x] 'Subscription Level' 드롭다운에 `admin` 옵션 추가.
- [x] **유저 검색/필터링**
    - [x] 이름/이메일 검색 기능 추가.
    - [x] 'Admin' 등급 유저만 모아보기 필터.

## 3. 정책 데이터 관리 (CRUD)
- [x] **정책 수정 페이지 (`policies_edit.html`)**
    - [x] 제목, 내용, 기간, URL, 지역, 장르 수정 Form.
- [x] **정책 삭제 기능**
    - [x] 삭제 버튼 클릭 시 `Delete` API 호출 (실제 삭제 or `is_active=False` 처리).

