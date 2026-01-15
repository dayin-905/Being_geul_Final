# [jisang_nav.md] 네비게이션 및 추천/알림 시스템

## 3. [nav.html] 네비게이션 및 추천/알림 시스템 (Original Goal)
- [x] **네비게이션 순서 재배치**:
    - [x] 변경 전: (현재 순서)
    - [x] 변경 후: **Home** -> **Mypage/login** -> **All Policies** -> **About** 
- [x] **알림 뱃지(Badge) & 말풍선**:
    - [x] 알림 아이콘에 빨간 점(Badge) 추가
    - [x] 클릭 시 말풍선 표시 및 뱃지 제거 로직 구현
- [x] **알림 데이터 스키마 설계**: 알림/추천 기능을 위한 클라이언트/서버 데이터 구조 정의 (Stateless 구현 완료)
- [x] **추천 및 리마인드 알고리즘 구현**:
    - [x] **관심사 기반 추천**: "최근 본 '청년 수당'과 유사한 '취업 장려금' 추천"
    - [ ] **유사 사용자 기반(Collaborative Filtering)**: (No-DB/Stateless 구조로 인해 관심사/인기 기반 추천으로 대체됨)
    - [x] **마감 임박 리마인드**: "찜해둔 정책 마감 3일 전 알림"

## 상세 작업 이력 (Work Log)

### [2026-01-06] 네비게이션 & 알림 시스템 UI (Nav Bar)
1.  **UI 구조 변경**:
    - 메뉴 순서 변경: Home -> My Page (Login) -> All Policies -> About
    - **드롭다운 메뉴**: 데스크탑에서 My Page 호버 시 '마이페이지 이동' 및 '로그아웃' 버튼이 있는 드롭다운 구현.
    - **알림 말풍선 (Notification Bubble)**: 로고 우측 상단에 "..." 말풍선 배치 및 Mock 인터랙션 구현.

2.  **로그인 상태 동기화 (Client-side Auth)**
    - **문제**: 서버 사이드 렌더링(`{% if user %}`)이 클라이언트 로그인 상태(`localStorage`)와 동기화되지 않음.
    - **해결**: `nav.html`의 모든 조건부 렌더링을 클라이언트 사이드 JS(`localStorage.getItem('isLoggedIn')`)로 변경하여 Guest/User UI 분기 처리.

3.  **UI 디테일 및 버그 수정**
    - **Duplicate ID Fix**: `main.html`에서 `auth_modal.html` 중복 제거.
    - **Flicker Fix**: 로그인 상태 확인 전 UI가 깜빡이는 현상을 방지하기 위해 모든 Guest 요소를 기본 `hidden` 처리.
    - **Mobile UI**: 모바일 프로필 영역의 "My Page" 버튼을 **"로그아웃"** 버튼으로 변경하고 텍스트 한글화.

### [2026-01-06] (신규) Troubleshooting: 서버 및 스크립트 충돌 해결
1.  **증상**: 코드 수정 후에도 브라우저에서 변경 사항("로그아웃" 버튼 등)이 반영되지 않음.
2.  **원인 1 (Port Conflict)**: 기존 서버 프로세스(Zombie Process)가 백그라운드에서 포트(8000)를 점유 중이라 새 코드가 실행되지 않음. -> **PID 강제 종료**로 해결.
3.  **원인 2 (Script Conflict)**: `script.js` 내부의 `checkLoginState` 함수가 `innerHTML`로 네비게이션 DOM을 강제로 덮어쓰고 있었음 (Legacy Code). -> **해당 로직 주석 처리**하여 `nav.html`의 자체 코드가 동작하도록 조치.
4.  **결과**: 수정 사항 정상 반영 확인 완료.

### [2026-01-06] (신규) Stateless 추천 알림 시스템 구현
1.  **Backend (`routers/recommendation.py`)**:
    - **No-DB 방식**: 별도 Notification 테이블 생성 없이, `being_test` 및 `users` 테이블을 실시간 조회(Query)하여 알림 생성.
    - **4가지 시나리오 통합**:
        - **신규(New)**: 지역 내 최근 7일 신규 정책 (`created_at`).
        - **마감(Deadline)**: 찜한 정책 중 3일 내 마감 임박 건 (`end_date`).
        - **취향(Interest)**: 찜 내역 분석 -> 선호 장르의 인기 정책 추천 (`UserAction`).
        - **인기(Best)**: 지역 내 조회수 1위 정책 (`view_count`).

2.  **Frontend (`nav.html`) 진행**:
    - **UI 변경**: 단순 클릭 이동 방식에서 **"리스트형 드롭다운"** 방식으로 변경하여 여러 알림을 동시에 노출.
    - **API 연동**: `/api/recommend/status` 호출하여 알림 갯수(Red Dot) 표시 및 리스트 렌더링.
    - **Animation**: `float` 애니메이션 유지하며 클릭 시 메뉴 토글링 구현.
    - **Personalization (Polishing)**: 
        - 알림창 상단에 **"[사용자명]님에게 도착한 알림"** 문구 추가하여 개인화 느낌 강화.
        - **Data Highlighting**: 이름(Orange), 숫자(Teal), 카테고리(Blue) 등 주요 정보에 색상 강조 처리.
        - 취향 기반 추천 메시지에도 **"[사용자명]님 취향저격!"** 멘트 적용.
    - **Refinement**:
        - **읽음 처리(Read Logic - Advanced)**:
            - **개별 읽음(Granular Read)**: 말풍선 전체가 아닌, **클릭한 특정 알림만 '읽음' 처리**되도록 개선.
            - **UI 구분**: 읽은 알림은 회색 배경/흐린 텍스트로, 안 읽은 알림은 흰색 배경/진한 텍스트로 시각적 구분.
            - **수량 제한**: 최대 **7개**까지만 리스트에 노출 (읽은 것 포함).
            - **뱃지(Badge)**: 전체 갯수가 아닌 **'읽지 않은 알림 갯수'**만 빨간색 숫자로 표시.
            - **삭제(Delete) 기능 추가**: 알림 항목에 '휴지통' 아이콘 추가. 사용자가 직접 삭제한 알림은 **영구적으로 숨김(Blacklist)** 처리하여 피로도 해소.
        - **리다이렉트 개선 (Redirect Logic Change)**:
            - **마감 임박 알림 (Deadline)**: 기존 `all.html` 이동에서 **`mypage.html`로 이동 후 해당 정책 모달 자동 팝업**으로 변경. (User UX 강화)
            - **추천/인기 알림 (Interest/Best)**: `all.html` 이동 시 **자동으로 해당 정책 상세 모달 팝업**.
                - *충돌 방지 전략(No-Conflict)*: `all.html` 파일 수정 없이, **`nav.html`에 전용 스크립트를 탑재**하여 구현.
                - *API 신설*: `routers/recommendation.py`에 단일 정책 조회용 `/api/recommend/policy/{id}` 추가.
            - **수정 파일**: `routers/recommendation.py`, `templates/nav.html`, `templates/mypage.html`
            - **작업 시간**: 2026-01-07 15:15

        - **UI 디자인 개선 (Refinement)**:
            - **아바타 아이콘 적용**: 아이콘을 원형 아바타 스타일(`w-9 h-9 rounded-full`)로 변경하여 시각적 인지도 유지.
            - **밀도 조정 (Rollback)**: 사용자의 요청으로 패딩(`p-3`)과 폰트 크기(`text-xs`), 뱃지 스타일(`마감임박`)은 기존의 컴팩트한 스타일로 복구.
            - **작업 시간**: 2026-01-07 15:30

