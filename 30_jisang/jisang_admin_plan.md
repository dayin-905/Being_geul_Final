# [Plan] 관리자(Admin) 페이지 고도화 계획

## 1. 개요 (Overview)
현재 구현된 `templates/admin/` 및 `routers/admin.py`는 **MVP(최소 기능 제품)** 수준으로, 실제 서비스를 운영하기 위해서는 **보안 강화**와 **데이터 관리의 편의성**을 높이는 작업이 필요합니다.

## 2. 고도화 제안 사항 (Advancement Plan)

### 🔒 1단계: 보안 및 인증 강화 (Security)
*   **DB 기반 관리자 관리 (Role-Based)**:
    *   **변경**: 별도의 컬럼(`is_admin`) 추가 없이, 기존 **`subscription_level`** 컬럼에 **`admin`** 등급을 추가하여 구분.
    *   **로직**: 로그인 시 `subscription_level == 'admin'`인 유저만 관리자 대시보드 접근 허용.
*   **세션 보안 (Session Security)**:
    *   현재: 단순 쿠키(`admin_session=valid`) 체크 방식 (보안 취약).
    *   **개선**: `auth.py`의 JWT 토큰 로직을 재사용하거나, `users` 테이블 기반의 세션 검증 로직으로 교체.

## 4. 영향 범위 및 수정 파일 리스트 (Impact Analysis)

이 계획(subscription_level 활용)으로 진행 시 수정이 필요한 파일 목록입니다.

### 📝 수정 대상 파일
1.  **`routers/admin.py`**:
    *   **로그인 로직 전면 수정**: 하드코딩된 `ADMIN_CREDENTIALS` 삭제 -> DB `users` 테이블 조회로 변경 (`email` & `password` 검증).
    *   **권한 체크(Dependency)**: `get_current_admin` 같은 의존성 함수를 만들어, 모든 admin 라우터 접근 시 `user.subscription_level == 'admin'` 확인.
2.  **`templates/admin/login.html`**:
    *   **Form 수정**: `username` 필드를 `email` 필드로 변경 (DB의 User 테이블과 매치).
3.  **`templates/admin/users.html` (및 `users/update` API)**:
    *   **권한 관리 UI**: 유저 수정 모달의 'Subscription Level' 드롭다운에 `admin` 옵션 추가 (단, 최고 관리자만 부여 가능하도록 UI 로직 필요 가능성).
4.  **`routers/auth.py` (회원가입)**:
    *   **유효성 검사**: 일반 회원가입 시 `subscription_level`을 `admin`으로 조작해서 보내는 요청 방어 (Backend Validation).

### 🆕 신규 생성 필요 없음
*   `models.py` 수정 불필요 (`subscription_level`은 이미 String 타입이므로 'admin' 저장 가능).

### 📊 2단계: 대시보드 시각화 (Dashboard Visualization)
*   **Chart.js 연동 심화**:
    *   현재: HTML/CSS로 구현된 단순 막대 차트.
    *   **개선**:
        *   **가입자 추이 그래프**: 최근 7일/30일간 일별 신규 가입자 수 변화 (Line Chart).
        *   **카테고리별 선호도**: 유저들이 가장 많이 찜한 정책 카테고리 분포 (Pie Chart).
*   **실시간 로그 모니터링**:
    *   **개선**: "새로고침" 없이도 최신 유저 행동(가입, 찜하기 등)이 올라오는 **Live Log** 위젯 구현 (Polling 또는 HTMX 활용).

### 👥 3단계: 유저 관리 기능 심화 (User Management)
*   **상세 활동 조회**:
    *   현재: 단순 정보 수정(이름, 지역 등)만 가능.
    *   **개선**: 특정 유저 클릭 시, **"최근 본 정책", "찜한 목록"** 등 활동 히스토리를 모달로 조회하여 유저 성향 파악 가능.
*   **블랙리스트 관리**:
    *   **개선**: 악성 유저에 대한 **"계정 정지(Ban)"** 또는 **"강제 탈퇴"** 기능 추가.

### 📑 4단계: 정책 데이터 관리 (Policy CRUD)
*   **직접 수정/삭제 기능** (가장 시급):
    *   현재: 정책 조회 및 검색만 가능 (Read-Only).
    *   **개선**:
        *   **수정(Edit)**: 오타 제보나 마감일 변경 시 관리자 페이지에서 바로 수정.
        *   **삭제(Delete)**: 만료되거나 잘못된 정책 숨김 처리.
        *   **신규 등록(Create)**: 크롤링 외에 수동으로 급한 공지/정책 등록 기능.

## 3. 추천 우선순위
1.  **정책 데이터 수정 기능 (Policy Edit)**: 운영상 가장 빈번하게 발생할 니즈.
2.  **보안 인증 교체 (Security)**: 배포 전 필수.
3.  **대시보드 차트 (Chart)**: 시각적 만족도 및 보고용.

---
*이 계획서는 프로젝트 PM 및 이해관계자와의 논의를 위해 작성되었습니다.*
