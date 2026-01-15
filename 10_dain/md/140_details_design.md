# 디자인 세부사항 및 컴포넌트

## 1. 알림 시스템 (네비게이션 바)
**파일**: `templates/nav.html`

알림 시스템은 서버 통합 API 호출과 LocalStorage를 사용하여 읽음/삭제 상태를 관리합니다.

### 주요 로직
- **UI 구조**:
  - `div#noti-bubble`: 애니메이션 효과가 있는 플로팅 버블 아이콘.
  - `div#noti-menu`: 클릭 시 토글되는 콘텐츠 드롭다운 메뉴.
- **자바스크립트 (`initNotifications`)**:
  - `/api/recommend/status`에서 데이터를 가져옵니다.
  - `localStorage.getItem('deletedAlertIds')`를 사용하여 "삭제된" 알림을 필터링합니다.
  - 리스트 항목을 최대 7개로 제한합니다.
  - 읽지 않은 항목이 있으면 빨간색 배지를 표시합니다.
  - "읽음 표시" 및 "삭제" 동작을 로컬에서 처리합니다.

### 코드 스니펫 (UI + 스크립트)
```html
<!-- 알림 버블 -->
<div id="noti-bubble" class="absolute ...">
    <!-- 아이콘 -->
    <div id="noti-dot" class="...">...</div>

    <!-- 드롭다운 메뉴 -->
    <div id="noti-menu" class="hidden absolute top-8 left-0 w-[450px] ...">
        <!-- 리스트 헤더 -->
        <div class="...">...</div>
        <!-- 리스트 컨테이너 -->
        <ul id="noti-list" class="..."></ul>
    </div>
</div>

<script>
    async function initNotifications() {
        // API 호출
        const res = await fetch(`/api/recommend/status?user_email=${...}`);
        // 렌더링 로직 ...
    }
</script>
```

---

## 2. 스와이프 가이드 (메인 페이지)
**파일**: `templates/main.html`

스와이프 가이드는 사용자가 틴더 스타일 카드와 상호작용하는 방법을 안내하는 오버레이입니다.

### 디자인 업데이트
- **스타일**: 커스텀 색상, 글래스모피즘(Glassmorphism), 그림자 효과
- **배경**: `bg-[#9a9a9a]/60` (세련된 회세, 유리 효과를 위한 반투명 처리)
- **손 아이콘**: `text-[#f8f8f8]` (고스트 화이트)
- **제목 텍스트**: `text-white`, `drop-shadow-md` 적용 (대비 향상)
- **PASS 텍스트**: `text-[#333333]`, `font-bold`, `drop-shadow-sm` 적용
- **LIKE 텍스트**: `text-[#ff5a5f]`, `font-bold` (코랄 레드, 명확한 강조)
- **블러 효과**: `backdrop-blur-md`
- **애니메이션**: 상호작용 후 페이드 아웃 (스크립트로 제어됨)

### 코드 스니펫
```html
<div id="swipe-guide"
    class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-30 pointer-events-none opacity-0 flex flex-col items-center justify-center
           bg-[#9a9a9a]/60 backdrop-blur-md px-12 py-10 rounded-[30px] border border-white/10 shadow-2xl transition-all">
    
    <!-- 아이콘 -->
    <div class="flex items-center justify-center mb-6">
        <i class="fa-solid fa-hand-pointer text-6xl text-[#f8f8f8] drop-shadow-md" id="hand-icon"></i>
    </div>

    <!-- 안내 문구 -->
    <div class="text-center">
        <p class="text-xl font-bold text-white whitespace-nowrap tracking-wider mb-2 drop-shadow-md">
            카드를 좌우로 밀어보세요
        </p>
        <div class="flex items-center justify-center gap-4 text-[#333333] font-medium text-base drop-shadow-sm">
            <span class="flex items-center gap-1 font-bold"><i class="fa-solid fa-arrow-left"></i> PASS</span>
            <span class="w-[1px] h-4 bg-gray-600"></span>
            <span class="flex items-center gap-1 text-[#ff5a5f] font-bold">LIKE <i class="fa-solid fa-heart"></i></span>
        </div>
    </div>
</div>
```

---

## 3. 트러블슈팅 로그
**날짜**: 2026-01-09

### 이슈: 스와이프 가이드 HTML 태그 깨짐
- **설명**: `templates/main.html`에서 스와이프 가이드의 배경 투명도를 조정하던 중, 여는 `<div>` 태그가 실수로 삭제되었습니다.
- **결과**: 브라우저가 컨테이너를 올바르게 렌더링하지 못해, 원시 HTML 속성 텍스트(예: `class="absolute ...`)가 화면의 스와이프 카드 영역 근처에 그대로 노출되었습니다.
- **해결**: 누락된 `<div id="swipe-guide" ...>` 태그를 복구하여 속성들이 요소의 일부로 올바르게 파싱되도록 수정했습니다.

### 업데이트: 색상 테마 및 타이포그래피 변경
- **배경**: 글래스모피즘 룩을 완성하기 위해 **`#9a9a9a`** 색상과 **60% 투명도**로 개선했습니다.
- **아이콘**: 대비를 위해 고스트 화이트(`text-[#f8f8f8]`)로 변경했습니다.
- **텍스트 (PASS)**: 가독성을 높이기 위해 다크 그레이(`text-[#333333]`)와 **볼드체**(`font-bold`)를 적용했습니다.
- **텍스트 (LIKE)**: 색상 코드를 표준화하기 위해 코랄 레드(`text-[#ff5a5f]`)로 변경했습니다.
- **텍스트 그림자**: 밝은 배경에서의 가독성 문제를 해결하기 위해 텍스트 요소에 `drop-shadow-md`를 추가했습니다.

---

## 4. 관리자 로그인 페이지
**파일**: `templates/admin/login.html`

### 디자인 업데이트
- **이메일 입력창**: 흰색 입력 배경에서 가독성을 보장하기 위해 텍스트 색상을 `text-black`으로 변경했습니다.
- **이메일 라벨**: 어두운 배경에서 더 잘 보이도록 텍스트 색상을 `text-gray-400`으로 변경했습니다.

### 코드 스니펫
```html
<div>
    <label for="email" class="block text-sm font-medium text-gray-400">Email Address</label>
    <input type="email" name="email" id="email" required
        class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-[#4A9EA8] focus:border-[#4A9EA8] sm:text-sm text-black"
        placeholder="admin@example.com">
</div>
```

---

## 5. 마이페이지 로직 변경 (신청 완료 → 마감 임박)
**날짜**: 2026-01-09

### 변경 사항
- **기존**: "신청 완료" (항상 0으로 고정되거나 실제 데이터 연동이 어려웠던 항목)
- **변경**: **"마감 임박"** (내가 찜한 정책 중, 오늘 기준 D-7 이내에 마감되는 정책 수 확인)
- **목적**: 사용자에게 더 실질적이고 긴급한 정보를 제공하여 행동 유도.

### 코드 스니펫

#### 1. Backend (`routers/mypage.py`)
`datetime` 모듈을 사용하여 오늘 날짜(`today`)와 7일 후(`deadline`)를 계산하고, 해당 기간 내에 `end_date`가 있는 `UserAction(like)` 항목을 카운트합니다.

```python
from datetime import datetime, date, timedelta

# ... (생략)

@router.get("/profile")
def get_user_profile(user_email: str, db: Session = Depends(get_db)):
    # ... (기존 로직 생략)

    # [NEW] 마감 임박 (D-7) 개수 계산
    today = date.today()
    deadline = today + timedelta(days=7)
    
    closing_soon_count = db.query(UserAction)\
        .join(Policy, UserAction.policy_id == Policy.id)\
        .filter(
            UserAction.user_email == user_email,
            UserAction.type == 'like',
            Policy.end_date >= today,
            Policy.end_date <= deadline
        ).count()
        
    return {
        # ...
        "closing_soon_count": closing_soon_count, # [NEW]
        # ...
    }
```

#### 2. Frontend (`templates/mypage.html`)
아이콘을 '종이비행기'에서 '알림 벨'로 변경하고, 라벨을 수정했습니다.

```html
<div class="text-center">
    <div class="text-gray-300 text-2xl mb-1 transition-colors group-hover:text-primary-teal">
        <!-- 아이콘 변경: fa-paper-plane -> fa-bell -->
        <i class="fa-solid fa-bell"></i>
    </div>
    <p class="text-xs text-gray-400 font-bold mb-1">마감 임박</p>
    <p id="user-closing-count" class="text-xl font-extrabold text-gray-800">-</p>
</div>
```

#### 3. Script (`static/script.js`)
API에서 받아온 `closing_soon_count` 값을 UI에 바인딩합니다.

```javascript
// 4) 카운트
const likeCountEl = document.getElementById('user-like-count');
const closingCountEl = document.getElementById('user-closing-count'); // [NEW]

if (likeCountEl) likeCountEl.innerText = data.like_count;
if (closingCountEl) closingCountEl.innerText = data.closing_soon_count || 0; // [NEW]
```
