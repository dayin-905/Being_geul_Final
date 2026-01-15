# 정책 카드 디자인 및 레이아웃 수정 사항

사용자 요청에 따라 정책 카드의 디자인(카테고리별 색상)을 변경하고, 반응형 레이아웃 이슈를 해결했습니다. 또한 불필요한 해시태그(`#`)를 제거하여 UI를 개선했습니다.

## 1. 카테고리별 색상 정의 (Color Palette)

| 카테고리 | Main Color (Text/Border) | Background Color (Light) |
| :--- | :--- | :--- |
| **취업** | `#4A9EA8` (Teal) | `#F0FDFA` (Teal-50) |
| **주거** | `#F48245` (Orange) | `#FFF7ED` (Orange-50) |
| **금융** | `#D9B36C` (Beige) | `#FEFCE8` (Yellow-50) |
| **창업** | `#FF5A5F` (Red) | `#FEF2F2` (Red-50) |
| **복지** | `#A855F7` (Purple) | `#FAF5FF` (Purple-50) |
| **교육** | `#3B82F6` (Blue) | `#EFF6FF` (Blue-50) |
| **기타** | `#777777` (Gray) | `#F3F4F6` (Gray-100) |

---

## 2. 주요 변경 사항 및 코드

### 2.1 카테고리별 색상 적용
`all.html`과 `static/script.js`에 공통으로 `GENRE_COLORS` 상수를 정의하고, 이를 통해 카드 생성 시 동적으로 스타일을 적용하도록 수정했습니다.

**적용된 코드 (Javascript):**
```javascript
// 카테고리별 색상 매핑
const GENRE_COLORS = {
    "취업": { main: "#4A9EA8", bg: "#F0FDFA" },
    "취업/직무": { main: "#4A9EA8", bg: "#F0FDFA" },
    
    "주거": { main: "#F48245", bg: "#FFF7ED" },
    "주거/자립": { main: "#F48245", bg: "#FFF7ED" },
    
    "금융": { main: "#D9B36C", bg: "#FEFCE8" },
    "금융/생활비": { main: "#D9B36C", bg: "#FEFCE8" },
    
    "창업": { main: "#FF5A5F", bg: "#FEF2F2" },
    "창업/사업": { main: "#FF5A5F", bg: "#FEF2F2" },
    
    "복지": { main: "#A855F7", bg: "#FAF5FF" },
    "복지/문화": { main: "#A855F7", bg: "#FAF5FF" },

    "교육": { main: "#3B82F6", bg: "#EFF6FF" },
    "교육/자격증": { main: "#3B82F6", bg: "#EFF6FF" },

    "default": { main: "#777777", bg: "#F3F4F6" }
};
```

### 2.2 레이아웃 수정 (배열 문제 해결)
반응형 그리드(2열, 3열, 4열) 환경에서 마지막 줄에 빈 공간이 생기지 않도록, 페이지당 표시되는 카드 개수를 조정했습니다.

- **기존**: 8개 (4열에만 최적화, 3열 시 3-3-2 배열로 어색함)
- **변경**: 12개 (2, 3, 4의 최소공배수)

**적용된 코드 (all.html):**
```javascript
// --- 1. 설정 및 유틸리티 ---
// [수정] 카드 개수 조정: 2, 3, 4열 그리드 모두에서 딱 떨어지도록 12로 변경 (최소공배수)
const ITEMS_PER_PAGE = 12;
```

### 2.3 UI 개선 (해시태그 제거)
`all.html` 목록에서 카테고리 뱃지에 표시되던 불필요한 해시태그(`#`)를 제거하여, 텍스트가 더 깔끔하게 보이도록 수정했습니다.

**변경 전:** `#취업/직무`  
**변경 후:** `취업/직무`

---

## 3. 테스트 방법

### 3.1 색상 및 UI 확인
1.  **전체 보기 페이지 (`all.html`)**
    -   각 카드의 뱃지(카테고리 태그) 배경색이 위 표의 색상과 일치하는지 확인하십시오.
    -   **뱃지 텍스트 앞에 '#' 기호가 없는지 확인하십시오.**
    -   카드에 마우스를 올렸을 때(Hover), 제목과 화살표 아이콘이 해당 카테고리 색상으로 변하는지 확인하십시오.
2.  **메인 페이지 (`main.html`) & 마이 페이지 (`mypage.html`)**
    -   추천 정책 슬라이드 및 찜한 정책 카드에서도 동일한 색상이 적용되는지 확인하십시오.

### 3.2 레이아웃 확인 (`all.html`)
1.  브라우저 창 크기를 조절하여 그리드 컬럼 수가 변하는지 확인하십시오 (모바일 1열 -> 태블릿 2열 -> PC 3~4열).
2.  **3열 보기 상태(약 1024px ~ 1280px)**에서 한 페이지에 카드가 12개(3x4) 배치되어 마지막 줄이 꽉 차는지 확인하십시오.

---

## 4. (2026-01-07 추가) 마감 정책 카드 디자인 수정 (날짜 색상)

### 4.1 개요
*   **배경**: 기존 마감된 정책 카드의 날짜가 **붉은색(Red)**으로 표시되어 "긴급함"을 강조하는 느낌이 있었습니다. 이미 종료된 정책이므로 **"비활성화/종료됨"**의 의미를 전달하기 위해 무채색 계열로 변경을 요청받았습니다.
*   **변경 내용**: 마감된 정책의 날짜 텍스트 색상을 `text-red-500`에서 **`text-gray-600`** (진한 회색)으로 변경합니다. 취소선은 적용하지 않고 깔끔하게 처리합니다.

### 4.2 코드 변경 내역 (`templates/all.html`)

**변경 전 (Before)**
```javascript
// 2-3. 날짜 텍스트 강조 (붉은색)
const dateClass = isClosed ? 'text-red-500 font-bold' : '';
```

**변경 후 (After)**
```javascript
// 2-3. 날짜 텍스트 강조 (진한 회색)
const dateClass = isClosed ? 'text-gray-600 font-bold' : '';
```

### 4.3 적용 결과 비교
*   **기존**: 붉은색 텍스트로 인해 마감되었음에도 시선이 집중되고 위험/경고의 느낌을 줌.
*   **변경 후**: 진한 회색 텍스트로 변경되어, 흑백(Grayscale) 처리된 카드 이미지와 자연스럽게 어우러지며 "종료됨"의 느낌을 차분하게 전달함.

---

### 4.4 (2026-01-07 추가) 호버 시 글자 색상 변경 기능 복구 (롤백)

**요청 사항**: "호버 시 글자 색상 변경 기능이 산만하다"는 의견으로 기능을 제거했으나, 팀원들의 "이전 버전이 훨씬 예쁘다"는 피드백으로 인해 재차 **롤백(Revert)**을 요청.

**코드 변경 내역 (`templates/all.html`)**:

제거했던 동적 색상 클래스 생성 로직을 다시 복구하였습니다.

```javascript
/* 복구된 코드 */
const hoverTextClass = `group-hover:text-[${colors.main}]`;
const hoverBorderClass = `group-hover:border-[${colors.main}]`;

// ...
<div class="... ${hoverBorderClass}">
<h3 class="... ${hoverTextClass}">
<i class="... ${hoverTextClass}">
```

이로써 다시 카드를 호버할 때 해당 카테고리의 고유 색상(Main Color)으로 제목과 테두리 색상이 변경됩니다.

---

## 5. (2026-01-07 추가) 정책 모달(Policy Modal) 카테고리별 색상 적용

### 5.1 개요
*   **배경**: 기존 정책 모달은 주황색(Orange)으로 색상이 고정되어 있어, 다양한 카테고리의 정책을 보여줄 때 시각적인 일관성이 부족했습니다. 목록에서 보는 카드의 색상과 모달의 색상을 일치시키기 위해 동적 색상 적용을 구현했습니다.
*   **변경 내용**: 모달을 열 때(`openCardModal`), 해당 정책의 카테고리(genre)를 분석하여 미리 정의된 테마 색상(GENRE_COLORS)을 모달 내부 요소에 적용합니다.

### 5.2 적용된 요소 및 색상 로직
1.  **카테고리 뱃지**:
    *   배경색 (`backgroundColor`): `GENRE_COLORS[genre].bg` (연한 파스텔톤)
    *   글자색/테두리 (`color`, `borderColor`): `GENRE_COLORS[genre].main` (진한 메인 컬러)
2.  **'원문 보러 가기' 버튼**:
    *   배경색 (`backgroundColor`): `GENRE_COLORS[genre].main`

### 5.3 주요 코드 (`static/policy_modal.js`)

```javascript
/* 1. 상단에 GENRE_COLORS 정의 (all.html과 동일) */
const GENRE_COLORS = { "취업": { main: "...", bg: "..." }, ... };

/* 2. openCardModal 함수 내부 */
const genre = data.genre || '기타';
const colors = GENRE_COLORS[genre] || GENRE_COLORS['default'];

// [카테고리 뱃지 스타일 적용]
if (els.category) {
    els.category.innerText = genre;
    els.category.style.backgroundColor = colors.bg;
    els.category.style.color = colors.main;
    els.category.style.borderColor = colors.main;
}

// [버튼 스타일 적용]
if (els.linkBtn) {
    els.linkBtn.style.backgroundColor = colors.main;
}
```

### 5.4 테스트 방법
1.  `all.html`에서 서로 다른 카테고리(예: 취업, 주거, 복지)의 카드를 각각 클릭합니다.
2.  모달이 뜨면 다음 요소의 색상이 카테고리 색상과 일치하는지 확인합니다.
    *   좌측 상단 **카테고리 뱃지** (예: 취업이면 청록색 배경/글씨)
    *   하단 **'원문 보러 가기' 버튼** (예: 취업이면 청록색 배경)
3.  기타 카테고리나 분류가 없는 카드를 눌렀을 때 회색(Default)으로 잘 나오는지 확인합니다.

---

### 5.5 (2026-01-07 추가) '원문 보러 가기' 버튼 색상 롤백 및 버그 수정

**이슈 보고**: `GENRE_COLORS` 상수를 `static/policy_modal.js`의 전역 스코프에 추가한 직후, `main.html`과 `mypage.html`에서 모달이 열리지 않는 현상이 발생함. 원인은 선언된 변수(`const`)의 중복 선언 또는 스크립트 로드 시점 충돌로 추정됨.

**조치 내용**:
1.  **변수 스코프 조정**: `GENRE_COLORS` 상수를 `window.openCardModal` 함수 내부로 이동하여 전역 충돌을 방지함.
2.  **UI 롤백**: '원문 보러 가기' 버튼의 배경색을 카테고리 색상으로 변경하던 로직을 제거하고, 기존의 회색(Gray) 버튼으로 복구함. (단, 카테고리 뱃지 색상은 유지)

**수정된 코드 (`static/policy_modal.js`)**:
```javascript
window.openCardModal = function (element) {
    // ...
    // [수정] 함수 내부에서 정의하여 충돌 방지
    const GENRE_COLORS = { ... };

    // ...
    // [롤백] 버튼 색상 변경 코드 삭제
    // if (els.linkBtn) els.linkBtn.style.backgroundColor = colors.main; (삭제됨)
};
```

---

### 5.6 (2026-01-07 추가) 모달 닫기 버튼 미작동 버그 수정

**이슈 보고**: `GENRE_COLORS` 위치 변경 및 `replace_file_content` 적용 과정에서 파일 상단의 `DOMContentLoaded` 이벤트 리스너(모달 초기화 및 닫기 버튼 이벤트 바인딩) 코드가 통째로 삭제되는 사고가 발생함. 이로 인해 모달을 열 수는 있지만, X 버튼이나 배경을 눌러도 닫히지 않는 치명적인 버그가 생김.

**수정 조치**:
삭제되었던 `DOMContentLoaded` 블록을 `static/policy_modal.js` 파일 최상단에 다시 복구하였습니다.

**복구된 코드 구조**:
```javascript
/**
 * static/policy_modal.js
 */

// 1. 초기화 및 이벤트 바인딩 (복구됨)
document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById('policy-modal');
    const closeBtn = document.getElementById('modal-close-x-btn');
    
    // 닫기 함수 및 이벤트 연결
    // ...
});

// 2. 카드 클릭 시 호출되는 함수
window.openCardModal = function (element) {
    // ...
}
```

이제 모달 열기/닫기 및 스타일 적용이 모두 정상적으로 동작합니다.

---

### 5.7 (2026-01-07 추가) 링크 복사(공유) 기능 개선 (Fallback 추가)

**이슈 보고**: 개발 환경 또는 특정 브라우저 보안 컨텍스트(HTTPS가 아닌 경우 등)에서 `navigator.clipboard.writeText` API가 작동하지 않아 링크 복사가 실패하는 현상이 발생함.
*   **실제 오류 로그**: `Uncaught TypeError: Cannot read properties of undefined (reading 'writeText')`
    *   **원인**: `navigator.clipboard` 객체는 보안 컨텍스트(HTTPS, localhost)에서만 브라우저가 제공합니다. 그렇지 않은 환경에서는 이 객체가 `undefined`가 되며, 여기에 `writeText` 메서드를 호출하려다 보니 TypeError가 발생한 것입니다.
    *   **해결**: 수정된 코드는 `if (navigator.clipboard && window.isSecureContext)` 조건문을 통해 객체가 존재할 때만 해당 API를 사용하고, 없을 경우 `execCommand` 방식(Fallback)으로 우회하므로 이 오류를 완벽하게 방지합니다.

**수정 조치**:
최신 Clipboard API 사용을 우선으로 하되, 지원하지 않거나 실패할 경우 `document.execCommand('copy')`를 사용하는 **Fallback(대체) 로직**을 추가하여 호환성을 확보했습니다. 만약 이것조차 실패하면 `prompt` 창을 띄워 사용자가 직접 링크를 복사할 수 있도록 유도합니다.

**개선된 코드 (`static/policy_modal.js`)**:
```javascript
els.shareBtn.onclick = () => {
    // ...
    const copyToClipboard = (text) => {
        // 1. 최신 API 시도 (Secure Context 필요)
        if (navigator.clipboard && window.isSecureContext) {
            return navigator.clipboard.writeText(text);
        } else {
            // 2. Fallback: 임시 textarea 생성 후 execCommand 사용
            const textArea = document.createElement("textarea");
            // ... (생성 및 선택)
            return new Promise((resolve, reject) => {
                try {
                    const successful = document.execCommand('copy');
                    if(successful) resolve(); else reject();
                } catch (e) { reject(e); }
                finally { document.body.removeChild(textArea); }
            });
        }
    };
    
    copyToClipboard(shareUrl)
        .then(() => alert('성공!'))
        .catch(() => prompt('직접 복사해주세요.', shareUrl));
};
```

---

### 5.8 (2026-01-07 추가) 모달 높이 최적화 및 구분선 제거

**요청 사항**: 정책 제목이나 내용이 길어질 경우 모달의 윗부분이 화면에서 잘리는 현상이 발생함. 이를 방지하기 위해 불필요한 공백과 구분선을 제거하여 모달 전체 높이를 줄이고, 내용과 하단 요소(날짜, 버튼) 간의 간격을 좁혀달라는 요청.

**수정 내용 (`templates/components/policy_modal.html`)**:
1.  **구분선 제거**: 본문(`modal-desc`)과 하단 날짜(`modal-date`) 사이에 있던 `<div class="border-b ..."></div>` 요소를 삭제했습니다.
2.  **간격 축소**: 본문 영역의 하단 여백을 `mb-6`에서 `mb-2`로 대폭 줄여, 내용 바로 아래에 날짜와 버튼이 위치하도록 조정했습니다.

**코드 변경 비교**:

**변경 전:**
```html
<div class="mb-6"> <!-- 넓은 여백 -->
    <p id="modal-desc">...</p>
</div>
<div class="w-full border-b border-gray-100 mb-4"></div> <!-- 구분선 존재 -->
```

**변경 후:**
```html
<div class="mb-2"> <!-- 좁은 여백 -->
    <p id="modal-desc">...</p>
</div>
<!-- 구분선 제거됨 -->
```

이로써 모달의 내용 밀도가 높아지고 세로 길이가 줄어들어, 내용이 많아도 한 화면에 더 안정적으로 표시됩니다.

### 5.9 정책 모달 기능 및 레이아웃 테스트 가이드 (종합)

위에서 진행한 모든 모달 관련 수정 사항(색상, 버그 수정, 레이아웃 최적화)을 검증하기 위한 테스트 절차입니다.

**1. 레이아웃 및 디자인 확인 (높이 최적화)**
*   **구분선 제거 확인**: 모달을 열었을 때 본문 텍스트와 하단 '마감일(상시 모집 등)' 뱃지 사이에 **회색 가로 구분선이 보이지 않아야** 합니다.
*   **간격 축소 확인**: 본문 내용이 끝나는 지점과 하단 요소들(날짜, 버튼) 사이의 간격이 이전보다 **확연히 좁아졌는지 (mb-6 -> mb-2)** 확인합니다.
*   **긴 내용 표시 확인**: 내용이 긴 정책을 클릭했을 때, 모달 창이 화면 위쪽으로 넘쳐서 **이미지나 카테고리 뱃지가 잘리지 않는지** 확인합니다. (모달 전체 높이가 줄어들어 이전보다 더 많은 내용을 한 화면에 보여줍니다.)

**2. 기능 정상 작동 확인 (버그 수정 검증)**
*   **닫기 기능**: 우측 상단의 'X' 버튼을 누르거나, 모달 바깥의 어두운 배경을 클릭했을 때 모달이 **즉시 닫혀야** 합니다. (초기화 코드 복구 검증)
*   **링크 복사**: '공유하기' 버튼을 클릭했을 때 "정책 링크가 복사되었습니다!" 알림창이 떠야 하며, 메모장 등에 `Ctrl+V` 했을 때 링크가 정상적으로 붙여넣어져야 합니다. (Fallback 로직 검증)
*   **다른 페이지 연동**: `main.html`이나 `mypage.html`에서도 카드를 클릭했을 때 모달이 정상적으로 열리고 닫히는지 확인합니다. (전역 변수 충돌 해결 검증)

**3. 색상 로직 확인**
*   **카테고리 뱃지**: 모달 좌측 상단의 카테고리 뱃지가 클릭한 카드의 장르 색상(예: 취업-청록, 주거-주황)과 일치하는지 확인합니다.
*   **버튼 색상**: '원문 보러 가기' 버튼은 **기본 회색(Gray)**으로 유지되어야 합니다. (색상 변경 롤백 검증)

---

### 5.10 (2026-01-07 추가) 정책 모달 '지역' 뱃지 추가

**요청 사항**: 정책 모달 내에서 카테고리(장르)뿐만 아니라, 해당 정책이 속한 **지역 정보(예: 서울, 경기, 전국)**도 함께 직관적으로 보여주기를 요청. 디자인은 메인 화면의 'Home' 알약 버튼과 유사한 깔끔한 화이트 스타일로 통일.

**수정 내용**:

**1. HTML 구조 변경 (`templates/components/policy_modal.html`)**
기존에 절대 위치(`absolute`)로 배치되었던 카테고리 뱃지를 `flex` 컨테이너로 감싸고, 그 옆에 '지역 뱃지'를 추가했습니다.
```html
<div class="absolute top-5 left-5 flex gap-2 z-10">
    <!-- 카테고리 뱃지 -->
    <span id="modal-category" class="...">카테고리</span>
    
    <!-- [NEW] 지역 뱃지 (Home 알약 스타일) -->
    <span id="modal-region"
        class="bg-white/90 backdrop-blur-sm text-slate-600 px-3 py-1 rounded-lg text-xs font-bold border border-gray-100 shadow-sm">
        지역
    </span>
</div>
```

**2. JS 로직 추가 (`static/policy_modal.js`)**
DB에서 가져온 `region` 데이터가 있을 경우 뱃지를 표시하고, 없을 경우(`null` 또는 빈 값) 숨기는 로직을 추가했습니다.
```javascript
// 요소 매핑
const els = {
    // ...
    region: document.getElementById('modal-region')
};

// ...

// [지역 데이터 바인딩]
if (els.region) {
    if (data.region) {
        els.region.innerText = data.region;
        els.region.style.display = ''; // 데이터가 있으면 표시
    } else {
        els.region.style.display = 'none'; // 없으면 숨김
    }
}
```

**3. 테스트 방법**
1.  지역 정보가 있는 정책(예: 서울시 청년수당)을 클릭하여 모달 좌측 상단 카테고리 옆에 '서울' 뱃지가 뜨는지 확인합니다.
2.  지역 정보가 없는 정책이나 데이터를 클릭하여 지역 뱃지가 보이지 않는지(숨김 처리) 확인합니다.
3.  디자인이 흰색 배경에 회색 글씨(Home 버튼 스타일)로 깔끔하게 나오는지 확인합니다.

---

### 5.11 (2026-01-07 추가) 정책 카드/모달 '지역' 뱃지 적용 및 모달 디자인 수정

**추가 요청 사항**:
1.  **지역 뱃지 노출**: 모달뿐만 아니라 **정책 카드 리스트**에서도 카테고리 옆에 지역 정보(예: 서울, 부산)를 표시해달라는 요청.
2.  **디자인 통일**: 지역 뱃지는 메인 화면의 'Home' 알약 버튼과 유사한 **화이트/그레이 스타일** 사용.
3.  **모달 디자인 수정**: 모달 내부 카테고리 뱃지에 적용된 **유색 테두리(Border)가 보기 싫다는 피드백**에 따라, 테두리를 제거하고 기존(카드와 동일한) 디자인으로 롤백.

**수정 내용**:

**1. 정책 카드 (`templates/all.html`)**
카드 내부 카테고리 뱃지 옆에 지역 뱃지를 추가했습니다.
```javascript
<div class="flex items-center gap-2 mb-2">
    <!-- 카테고리 뱃지 -->
    <span class="..." style="${badgeStyle}">${genre}</span>
    
    <!-- [NEW] 지역 뱃지 -->
    ${item.region ? `<span class="bg-white/90 backdrop-blur-sm text-slate-600 px-2 py-0.5 rounded text-xs font-bold border border-gray-100 shadow-sm">${item.region}</span>` : ''}
</div>
```

**2. 모달 디자인 수정 (`static/policy_modal.js` & `html`)**
*   **테두리 제거**: 카테고리 뱃지의 `border-color`를 메인 색상으로 변경하던 JS 로직을 삭제하고, HTML 클래스에서도 `border` 관련 클래스를 제거하여 **깔끔한 무테 스타일**로 변경했습니다.
*   **지역 뱃지**: 앞서 적용한 지역 뱃지 로직이 정상적으로 동작함을 재확인했습니다. (데이터가 `null`인 경우 숨김 처리)

**3. 테스트 방법**
1.  **카드 리스트 확인**: `all.html` 페이지에서 각 정책 카드 좌측 상단에 `[카테고리] [지역]` 형태의 두 개의 뱃지가 나란히 보이는지 확인합니다.
2.  **지역 뱃지 스타일**: 지역 뱃지가 **흰색 배경에 회색 글씨, 얇은 회색 테두리**로 'Home' 버튼과 유사한지 확인합니다.
3.  **모달 확인**: 카드를 클릭하여 모달을 열었을 때,
    *   좌측 상단에 지역 뱃지가 잘 뜨는지 확인합니다.
    *   카테고리 뱃지에 **진한 색상의 테두리가 사라졌는지** 확인합니다.

---

### 5.12 (2026-01-07 추가) 정책 카드 지역 뱃지 미노출 버그 수정

**이슈 보고**: `all.html`의 정책 카드 리스트에서 카테고리 옆에 지역 뱃지가 보이지 않는 문제가 지속됨.
*   **원인 분석**: `fetchPolicyData` 함수에서 API로부터 받은 원본 데이터를 `policyData` 배열로 가공(Mapping)할 때, `region` 필드를 누락하고 있었음. 이로 인해 화면 렌더링 시 `item.region` 값이 `undefined`가 되어 뱃지 생성 조건(`item.region ? ...`)을 만족하지 못함.

**수정 내용 (`templates/all.html`)**:
데이터 매핑 객체에 `region` 필드를 명시적으로 추가했습니다.

```javascript
policyData = data.map(item => {
    return {
        // ... 기존 필드
        is_active: item.is_active,
        region: item.region // [NEW] 누락되었던 지역 정보 추가
    };
});
```

이제 API에서 넘어온 지역 정보가 프론트엔드 데이터 객체에 정상적으로 담기며, 리스트에서도 지역 뱃지가 올바르게 표시됩니다.

---

### 5.13 (2026-01-07 추가) 지역 뱃지 스타일 변경 및 전체 페이지(Main/MyPage) 적용

**요청 사항**:
1.  **적용 범위 확대**: 'All Policies' 페이지뿐만 아니라, **Main 페이지(슬라이드, 스와이프)** 및 **Mypage(찜한 내역)**의 모든 카드에도 지역 뱃지를 표시해야 함.
2.  **디자인 수정**: 'Home' 알약 버튼의 **Hover되지 않은 상태**(`bg-gray-100`, `text-gray-600`)와 동일한 색상을 사용.
3.  **스타일 제거**: 테두리(Border)와 그림자(Shadow) 효과는 제거하여 깔끔한 플랫(Flat) 디자인 적용.

**수정 내용**:

**1. 스타일 정의**
지역 뱃지의 공통 스타일을 다음과 같이 정의하고 모든 페이지에 적용했습니다.
*   **Class**: `bg-gray-100 text-gray-600 px-2 py-0.5 rounded text-xs font-bold`
    *   `bg-gray-100`: 연한 회색 배경
    *   `text-gray-600`: 진한 회색 글씨
    *   `font-bold`: 굵은 글씨 (가독성 향상)
    *   `border-none`: 테두리 없음
    *   `shadow-none`: 그림자 없음

**2. 코드 변경 내역**

*   **`static/script.js` (Main/MyPage)**:
    `createCardHTML` 함수를 수정하여 DB 데이터에서 `region` 값을 읽어오고, 카테고리 뱃지 옆에 지역 뱃지를 추가했습니다. Tinder(스와이프) 카드와 Slide(일반) 카드 레이아웃 모두에 적용했습니다.
    ```javascript
    // DB에서 지역 정보 추출
    const displayRegion = item.region || "";

    // 뱃지 HTML 생성 (조건부 렌더링)
    ${displayRegion ? `<span class="bg-gray-100 text-gray-600 font-bold px-2 py-1 rounded-full text-sm">${displayRegion}</span>` : ''}
    ```

*   **`templates/all.html` (All Policies)**:
    기존에 적용했던 흰색/그림자 스타일을 제거하고, 위에서 정의한 회색/무테 스타일로 클래스를 교체했습니다.
    ```javascript
    <span class="bg-gray-100 text-gray-600 px-2 py-0.5 rounded text-xs font-bold">${item.region}</span>
    ```

*   **`templates/components/policy_modal.html` (Modal)**:
    모달 내부의 지역 뱃지 역시 동일한 디자인으로 업데이트했습니다.

**3. 테스트 방법**
1.  **Main 페이지**: 상단 스와이프 카드와 하단 슬라이드 카드들에서 '서울', '부산' 등의 지역 뱃지가 회색 알약 형태로 잘 보이는지 확인합니다.
2.  **My Page**: '내가 찜한 정책' 리스트에서도 동일하게 지역 뱃지가 표시되는지 확인합니다.
3.  **All 페이지**: 전체 보기 리스트에서 뱃지 디자인이 테두리/그림자 없이 깔끔한 회색으로 변경되었는지 확인합니다.
4.  **Modal**: 카드를 클릭했을 때 모달 좌측 상단에도 동일한 디자인의 지역 뱃지가 뜨는지 확인합니다.

---

### 5.14 (2026-01-07 추가) 정책 카드 지역 뱃지 색상 반전 (Main/MyPage)

**추가 요청 사항**:
*   **배경 색상 고려**: Main 페이지의 슬라이드 카드와 MyPage의 카드는 기본 배경색이 **회색(`bg-[#F6F6F7]`)**이고, 마우스를 올렸을 때(Hover) **흰색(`bg-white`)**으로 변하는 디자인임.
*   **색상 반전 적용**: 카드 배경색과의 대비를 위해 지역 뱃지의 색상을 다음과 같이 조건부로 적용 요청.
    *   **기본 상태 (회색 카드)**: 뱃지는 **흰색 (`bg-white`)**.
    *   **호버 상태 (흰색 카드)**: 뱃지는 **회색 (`bg-gray-100`)**.

**수정 내용 (`static/script.js`)**:
`createCardHTML` 함수의 슬라이드/일반 카드 생성 로직(`else` 블록)을 수정하여 `group-hover` 클래스를 활용한 색상 반전을 구현했습니다.

```javascript
// [수정] 슬라이드/MyPage 카드 지역 뱃지 스타일
<div class="flex items-center gap-2">
    <!-- 기본 bg-white, 호버 시 bg-gray-100 -->
    ${displayRegion ? 
        `<span class="bg-white text-gray-600 font-bold px-2 py-1 rounded-md text-xs group-hover:bg-gray-100 transition-colors">
            ${displayRegion}
        </span>` 
    : ''}
</div>
```

**참고**:
*   Tinder(스와이프) 카드는 기본 배경이 흰색(`bg-white`)이므로, 가독성을 위해 기존의 **회색 뱃지(`bg-gray-100`)** 상태를 유지했습니다. (흰색 카드 위에 흰색 뱃지를 두면 보이지 않음)
*   All Policies 카드는 배경이 흰색이므로 기존의 **회색 뱃지**를 유지합니다.

**테스트 방법**:
1.  **Main/MyPage 확인**: 마우스를 올리지 않은 상태에서 카드의 지역 뱃지가 **흰색**인지 확인합니다.
2.  **Hover 확인**: 카드에 마우스를 올렸을 때, 카드 배경이 흰색으로 변하면서 동시에 지역 뱃지가 **연한 회색**으로 변하는지(Visible 유지) 확인합니다.

---

### 5.15 (2026-01-07 추가) 정책 카드 뱃지 간격 조정

**요청 사항**:
카테고리 뱃지와 지역 뱃지 사이의 간격이 너무 넓어 UI적으로 불안정해 보인다는 피드백. 두 뱃지 사이의 거리를 좁혀서 시각적인 연관성을 높이길 요청.

**수정 내용**:
모든 관련 파일(`all.html`, `main.html`용 JS, 모달 HTML)에서 뱃지를 감싸는 Flex 컨테이너의 간격 클래스를 `gap-2` (8px)에서 **`gap-1` (4px)**로 축소했습니다.

*   **`templates/all.html`**:
    ```html
    <div class="flex items-center gap-1 mb-2"> ... </div>
    ```
*   **`static/script.js`** (Main Swipe/Slide Card):
    ```javascript
    <div class="flex items-center gap-1 mb-3"> ... </div>
    ```
*   **`templates/components/policy_modal.html`**:
    ```html
    <div class="absolute top-5 left-5 flex gap-1 z-10"> ... </div>
    ```

**테스트 방법**:
모든 페이지 및 모달에서 카테고리 뱃지와 지역 뱃지가 서로 가깝게 붙어 있는지 확인합니다.

---

### 5.16 (2026-01-07 추가) 모달 뱃지 정렬 및 크기 최적화

**요청 사항**:
정책 모달 내부의 지역 뱃지가 카테고리 뱃지보다 작고 위치가 미묘하게 어긋나 보여(Vertical Misalignment), UI적으로 불편하다는 피드백. 두 뱃지의 크기와 높이를 통일시켜 시각적 안정감을 주길 요청.

**수정 내용 (`templates/components/policy_modal.html`)**:
1.  **Flex 정렬 수정**: 뱃지들을 감싸는 컨테이너에 `items-center` 클래스를 추가하여 수직 중앙 정렬을 강제했습니다.
2.  **스타일 통일**: 지역 뱃지의 패딩과 모서리 둥글기를 카테고리 뱃지와 동일하게 맞췄습니다.
    *   **Padding**: `px-2 py-0.5` → **`px-3 py-1`**
    *   **Border Radius**: `rounded` → **`rounded-lg`**

**코드 변경 비교**:
```html
<!-- 변경 전 -->
<div class="flex gap-1">
    <span class="... px-3 py-1 rounded-lg">카테고리</span> <!-- 큼 -->
    <span class="... px-2 py-0.5 rounded">지역</span>     <!-- 작음 -->
</div>

<!-- 변경 후 -->
<div class="flex items-center gap-1"> <!-- 수직 높이 맞춤 -->
    <span class="... px-3 py-1 rounded-lg">카테고리</span>
    <span class="... px-3 py-1 rounded-lg">지역</span>     <!-- 크기 맞춤 -->
</div>
```

**테스트 방법**:
정책 모달을 열었을 때, 좌측 상단의 '카테고리'와 '지역' 알약 버튼이 **정확히 같은 높이와 크기**로 나란히 정렬되어 있는지 확인합니다.
