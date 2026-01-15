# [Merge Request] 지상(Jisang) 작업 내역 요약

## 1. 개요
초기 목표였던 **3대 핵심 기능(Landing, Auth, Nav)** 개발 및 개선을 완료했습니다.
아래 파일들의 변경 사항을 확인 후 병합(Merge) 부탁드립니다.

## 2. 주요 변경 파일 (File Changes)

### 🟢 Backend (서버 로직)
*   **`main.py`**:
    *   신규 라우터 등록: `recommendation` (알림), `about` (페이지).
    *   설정 수정: 정적 파일 경로(`BASE_DIR`) 절대 경로로 수정하여 배포 환경 호환성 확보.
*   **`models.py`**:
    *   `User` 모델: 소셜 로그인(`provider`), 지역(`region`) 컬럼 추가.
    *   `UserAction` 모델: 유저-정책 반응(좋아요/패스) 관계 설정.
*   **`routers/auth.py`**:
    *   **OAuth Fix**: 구글/네이버 로그인 리다이렉트 URI 수정 및 한글 이름 인코딩 적용.
    *   **Bug Fix**: 회원가입 시 지역 데이터 누락 방지를 위한 기본값('전국') 처리.
*   **`routers/recommendation.py` (신규)**:
    *   알림 시스템 로직: DB 조회 없이 기존 데이터(`being_test`, `UserAction`)를 활용해 개인화 알림 생성.

### 🔵 Frontend (UI/UX)
*   **`templates/nav.html`**:
    *   **UI 개편**: 아바타 스타일 알림 리스트, 읽음/삭제 기능, 뱃지(Badge) 카운팅.
    *   **Logic**: 클라이언트 사이드(`localStorage`) 로그인 상태 동기화 완벽 구현.
*   **`templates/about.html`**:
    *   **Fix**: 하드코딩된 네비게이션을 제거하고 공통 컴포넌트(`nav.html`) include로 교체.
*   **`templates/components/auth_modal.html`**:
    *   **Validation**: 이메일 유효성 실시간 검증 UI 및 피드백 메시지 추가.
*   **`static/script.js`**:
    *   **UX 개선**: 엔터키 로그인 지원, 회원가입 지역 뱃지 연동.
    *   **Mobile**: 지도 뷰포트 최적화 및 바텀 시트(Bottom Sheet) 인터랙션 추가.

### 🟡 Documentation (문서화)
*   기존 거대했던 `jisang_new.md`를 삭제하고 작업 단위별로 분리하여 정리했습니다:
    *   `jisang_landing.md`: 랜딩 페이지 및 지도 개선 내역
    *   `jisang_auth_modal.md`: 회원가입/로그인 모달 및 로직 개선 내역
    *   `jisang_nav.md`: 네비게이션 및 알림 시스템 구축 내역

---
*2026-01-07 PM 3:45 작성됨*
