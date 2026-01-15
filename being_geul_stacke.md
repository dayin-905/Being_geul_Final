# Being Geul (빙글) 기능 기술서

## 1. 프로젝트 개요
**Being Geul (빙글)**은 청년 주거, 금융, 취업 등 다양한 정책 정보를 사용자 친화적인 인터페이스로 제공하는 맞춤형 정책 추천 플랫폼입니다. '틴더(Tinder)' 스타일의 스와이프 방식과 개인화된 추천 알고리즘을 통해 정책 탐색의 재미와 편의성을 극대화하였습니다.

---

## 2. 기술 스택 (Tech Stack)

### 백엔드 (Backend)
- **프레임워크**: FastAPI (Python 3.10+)
- **데이터베이스**: 
  - SQLite (로컬 개발용)
  - SQLAlchemy ORM (데이터 모델링 및 쿼리)
- **인증(Auth)**: 
  - Argon2 (비밀번호 해싱)
  - 세션/쿠키 + 로컬스토리지 하이브리드 방식
  - **OAuth 2.0**: 구글(Google), 네이버(Naver) 소셜 로그인 지원

### 프론트엔드 (Frontend)
- **템플릿 엔진**: Jinja2 (서버 사이드 렌더링)
- **스타일링**: 
  - **Tailwind CSS** (CDN 로드, 커스텀 config 설정)
  - Vanilla CSS (`static/style.css` - 애니메이션 및 세부 디테일)
- **라이브러리**:
  - **GSAP (GreenSock)**: 고급 인터랙션 및 애니메이션 (ScrollTrigger 포함)
  - **Chart.js**: 마이페이지 관심사 통계 차트 (Radar/Bar Chart)
  - **Lottie**: 로딩 및 인트로 애니메이션 (JSON 기반)
  - **Hammer.js**: 모바일 터치 제스처 처리 (스와이프)
  - **html2canvas**: MBTI 결과 카드 이미지 저장 기능

---

## 3. 템플릿 구조 (Templates Structure)

FastAPI의 Jinja2Templates를 사용하여 렌더링되며, 컴포넌트 재사용성을 고려하여 구조화되었습니다.

### 3.1. 메인 페이지 (`templates/main.html`)
- **역할**: 서비스의 진입점, 스와이프 UX 제공.
- **주요 섹션**:
  - **Intro Header**: `GSAP` 애니메이션이 적용된 타이틀 및 비디오.
  - **Tinder Section**: `CardSwiper` 클래스(JS)가 적용된 스와이프 영역. 정책 카드를 좌우로 넘기며 `Like/Pass` 액션 수행.
  - **Recommend Slider**: 마키(Marquee) 애니메이션을 활용한 자동 슬라이드 추천 배너.
- **데이터 주입**: `window.tinderData`, `window.allSlideData` 변수에 Jinja2를 통해 JSON 데이터 사전 주입.

### 3.2. 전체 정책 (`templates/all.html`)
- **역할**: 검색, 필터링, 정렬 기능을 갖춘 정책 탐색 페이지.
- **주요 기능**:
  - **검색 바**: 키워드 검색 및 최근 검색어(LocalStorage) 기능.
  - **3D Card Effect**: 마우스 호버 시 카드가 3D로 기울어지는 인터랙션 구현.
  - **스마트 필터**: 카테고리(탭), 지역(모달), 정렬(드롭다운) 복합 필터 지원.
  - **무한 스크롤/더보기**: AJAX 기반으로 추가 데이터 로드 (`/api/main/more-cards`).

### 3.3. 마이페이지 (`templates/mypage.html`)
- **역할**: 사용자 대시보드 및 개인화 데이터 관리.
- **주요 기능**:
  - **프로필**: 아바타 변경(6종), 닉네임, 지역 뱃지 표시.
  - **P-MBTI 카드**: 활동 내역 기반 성향 분석 결과 표시 및 이미지 저장 기능.
  - **활동 통계**: `Chart.js`를 이용한 관심 카테고리 시각화.
  - **찜한 정책 관리**: 편집 모드를 통한 다중 선택 및 일괄 삭제 기능.

### 3.4. 공통 컴포넌트
- **`templates/nav.html`**: 반응형 내비게이션 바. 로그인 상태(`localStorage`)에 따라 UI 분기 처리.
- **`templates/components/policy_modal.html`**: 모든 페이지에서 공통으로 사용되는 정책 상세 모달.
  - **기능**: 상세 정보 표시, 원문 링크 이동, 찜하기(Like/Unlike) 토글, 공유하기 등.

---

## 4. 데이터베이스 스키마

### 4.1. 정책 테이블 (`being_test`)
정책 정보를 담고 있는 핵심 데이터입니다.
- **주요 컬럼**: 
  - `id` (PK): 정책 고유 ID
  - `title`, `summary`: 제목 및 요약
  - `genre`: 카테고리 (취업, 창업, 주거, 금융, 복지, 교육)
  - `region`: 대상 지역 (서울, 경기 등)
  - `period`, `end_date`: 모집 기간 및 마감일
  - `is_active`: 마감 여부 (Boolean)
  - `view_count`: 조회수 (인기순 정렬용)

### 4.2. 사용자 테이블 (`users`)
- **주요 컬럼**: 
  - `email` (Unique), `password`, `name`
  - `region`: 관심 지역
  - `provider`: `local`, `google`, `naver`
  - `subscription_level`: `free`, `premium`, `admin`
  - `profile_icon`: 프로필 아바타 파일명

### 4.3. 사용자 활동 테이블 (`users_action`)
추천 알고리즘의 핵심이 되는 로그 데이터입니다.
- **주요 컬럼**:
  - `user_email` (FK), `policy_id` (FK)
  - `type`: `like`(찜), `pass`(패스), `unlike`(취소)
  - `created_at`: 생성 일시

---

## 5. 프론트엔드 핵심 로직 (Frontend Logic)

### 5.1. 스와이프 (Tinder Logic)
- **파일**: `static/script.js` 내 `CardSwiper` 클래스
- **동작 원리**:
  1. 마우스/터치 이벤트(`mousedown`, `touchstart`)로 드래그 감지.
  2. 드래그 거리에 따라 카드 회전(`rotate`) 및 불투명도 조절.
  3. 놓았을 때(`mouseup`, `touchend`) 임계값(±150px)을 넘으면 액션 트리거.
  4. 오른쪽 스와이프 -> `like`, 왼쪽 스와이프 -> `pass` API 호출 (`POST /api/mypage/action`).

### 5.2. 상태 관리 (State Management)
- **세션 유지**: 
  - JWT 등을 사용하지 않는 MVP 단계로, `localStorage`에 `isLoggedIn`, `userEmail`을 저장하여 클라이언트 상태 관리.
  - 페이지 로드 시 `/api/auth/verify`를 호출하여 서버 측 세션 유효성 검증.
- **지역 선택**: `sessionStorage`에 사용자가 선택한 지역(`sseuk_selected_region`)을 저장하여 페이지 이동 간 필터 유지.

### 5.3. 동적 데이터 로딩
- **초기 로딩**: Jinja2 `tojson` 필터를 사용해 HTML 렌더링 시점에 JS 변수(`window.tinderData`)로 데이터 주입.
- **추가 로딩**: 스와이프 데이터 소진 시 또는 전체보기 페이지에서 `fetch`로 `/api/main/more-cards` 등을 호출하여 AJAX로 데이터 충전.

---

## 6. 주요 API 엔드포인트

| 모듈 | 메서드 | 엔드포인트 | 설명 |
| :--- | :--- | :--- | :--- |
| **인증(Auth)** | POST | `/api/auth/signup` | 회원가입 처리 |
| | POST | `/api/auth/login` | 로그인 처리 (세션 생성) |
| | GET | `/api/auth/{provider}/login` | 소셜 로그인 리다이렉트 |
| **메인(Main)** | GET | `/main.html` | 메인 페이지 HTML 서빙 (Swipe 데이터 포함) |
| | GET | `/api/main/more-cards` | 스와이프 카드 추가 데이터 조회 (AJAX) |
| **전체(All)** | GET | `/api/cards` | 검색/필터/정렬 조건에 맞는 정책 리스트 반환 |
| **마이페이지** | GET | `/api/mypage/profile` | 유저 프로필, 활동 지수, MBTI 분석 결과 반환 |
| | GET | `/api/mypage/likes` | 찜한 정책 목록 조회 (페이지네이션) |
| | POST | `/api/mypage/action` | 사용자 액션(Like/Pass) 기록 저장 |
| | POST | `/api/mypage/likes/delete` | 찜한 정책 일괄 삭제 |
| **추천** | GET | `/api/recommend/status` | 개인화 알림(신규/마감임박/추천) 조회 |

---

## 7. 관리자 시스템 (Admin)
- **URL**: `/admin/login`, `/admin/dashboard`
- **구현 내용**: `routers/admin.py`
- **기능**:
  - 대시보드: 가입자 추이, 인기 정책 TOP 5 등 통계 확인.
  - 유저 관리: 회원 등급 수정, 강제 탈퇴 등.
  - 정책 관리: 정책 데이터의 등록, 수정, 삭제(CRUD) UI 제공.

---
*작성일: 2026-01-12*
*작성자: AntiGravity Agent*
