# [jisang_auth_modal.md] 회원가입 및 로그인 로직 개선

## 2. [auth_modal.html] 회원가입 및 로그인 로직 개선 (Original Goal)
- [x] **이메일 형식 강제 (Validation)**:
    - [x] 아이디 입력 칸에 `type="email"` 적용
    - [x] 정규표현식을 사용하여 이메일 형식이 아닐 경우 가입 차단 안내
- [x] **엔터키(Enter) 로그인**: 이메일/비밀번호 입력 후 엔터 키 입력 시 '로그인' 버튼 클릭 이벤트 트리거 (script.js `AuthController.init`에 구현됨)
- [x] **지역(Region) 데이터 저장 오류 수정**: 회원가입 시 선택한 지역 정보가 DB에 누락되는 원인 디버깅 및 수정 (Backend Social Login 수정 완료)

## 상세 작업 이력 (Work Log)

### [2026-01-05] 검증 스크립트(`debug_signup.py`) 테스트 결과
- 별도 스크립트로 회원가입 로직 실행 시 **성공**.
- 즉, 코드는 정상이나 **서버 프로세스가 패키지 설치 내역을 반영하지 못함** (재시작 필요).

### [2026-01-05] (신규) 소셜 로그인(OAuth) 문제 해결 완료
- **결과**: Google 및 Naver 로그인 정상 작동 확인 (사용자 검증 완료).
- **해결책**:
    1. `.env` 파일 내 Redirect URI 설정 변수명 및 경로 수정.
    2. `auth.py`에서 환경변수 로드 시 `.strip()` 처리로 공백 제거.
    3. 개발자 콘솔 Client ID 재확인 및 적용.
    4. **Backend**: OAuth 리다이렉트 경로를 `nav.html`이 없는 `/`에서 `/main.html`로 변경하고, 한글 이름 깨짐 방지를 위해 `urllib.parse.quote` 적용.
    5. **Frontend**: `nav.html` 스크립트에서 URL 파라미터(`social_login=success`)를 파싱하여 `localStorage`에 저장하는 로직 복구.
