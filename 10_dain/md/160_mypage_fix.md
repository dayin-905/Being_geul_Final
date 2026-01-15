# 마이페이지 및 전체 정책 페이지 수정 사항 (160_mypage_fix)

## 개요
전체 정책 보기 페이지(`all.html`)에서 정렬 필터의 UI/UX를 개선했습니다.
주요 수정 사항은 "마감 정책" 텍스트 잘림 현상 해결과 버튼 간의 여백(Padding) 통일입니다.

## 수정 내용

### 1. 정렬 버튼 텍스트 잘림 해결 & 여백 통일
*   **문제점**: 기존 정렬 버튼이 고정 너비(`width: 73px`)와 고정 글자 수(`3ch`)로 설정되어 있어, "마감 정책"과 같이 긴 텍스트가 잘리는 현상이 발생했음. 또한, "지역" 버튼과의 여백이 일치하지 않아 시각적으로 불안정함.
*   **해결**:
    *   버튼과 텍스트 `span`의 고정 너비 스타일을 제거하고 `width: auto`로 변경하여 콘텐츠에 맞게 늘어나도록 수정.
    *   "지역" 버튼 기준의 여백(약 24px)에 맞춰 정렬 버튼의 패딩을 `pl-4 pr-6` (왼쪽 1rem, 오른쪽 1.5rem)으로 조정하여 시각적 균형을 맞춤.

#### `templates/all.html` (HTML)
```html
<!-- 수정 전 -->
<!-- <button id="sort-btn" style="min-width: 73px; width: 73px; ..."> ... </button> -->

<!-- 수정 후 -->
<button id="sort-btn"
    class="shrink-0 pl-4 pr-6 py-2 h-full text-gray-600 text-sm font-bold transition-all flex items-center gap-1">
    <i class="fa-solid fa-sort" style="flex-shrink: 0;"></i> 
    <span class="sort-text" style="display: inline-block; width: auto; text-align: left; flex: 1;">정렬</span>
</button>
```

### 2. JavaScript 로직 개선
*   **기능 추가**:
    *   '마감 정책'(`closed`) 선택 시 올바른 텍스트가 표시되도록 로직 추가.
    *   정렬 텍스트가 길어질 경우(예: "마감 정책"), 검색바 내부의 '지우기(X)' 버튼과 텍스트가 겹치지 않도록 검색 `input`의 우측 패딩과 '지우기' 버튼의 위치를 동적으로 조정하는 로직 추가.
    *   선택 시 버튼 스타일(패딩 등)을 스크립트에서도 동일하게 `pl-4 pr-6` (`1rem`, `1.5rem`)으로 강제 적용하여 일관성 유지.

#### `templates/all.html` (Script)
```javascript
btn.addEventListener('click', async () => {
    // ... (생략)
    
    // DOM 요소 가져오기
    const searchInput = document.getElementById('search-input');
    const clearBtn = document.getElementById('clear-btn');

    if (sortBtn) {
        // 버튼 크기 유동적으로 변경 (고정폭 제거) 및 패딩 업데이트
        sortBtn.style.minWidth = 'auto';
        sortBtn.style.width = 'auto';
        sortBtn.style.paddingLeft = '1rem'; // pl-4
        sortBtn.style.paddingRight = '1.5rem'; // pr-6

        // ...

        // 레이아웃 리셋 Helper
        const resetLayout = () => {
            if (searchInput) searchInput.classList.replace('pr-56', 'pr-44');
            if (clearBtn) clearBtn.classList.replace('right-56', 'right-44');
        };
        
        // 레이아웃 확장 Helper ("마감 정책" 등 텍스트가 길어질 때)
        const expandLayout = () => {
                if (searchInput) {
                    searchInput.classList.remove('pr-44');
                    searchInput.classList.add('pr-56');
                }
                if (clearBtn) {
                    clearBtn.classList.remove('right-44');
                    clearBtn.classList.add('right-56');
                }
        };

        if (selectedSort === 'reset') {
            // ...
            resetLayout();
            // ...
        } else {
            // ...
            if (selectedSort === 'latest') {
                textContent = '최신순';
                resetLayout();
            } else if (selectedSort === 'popular') {
                textContent = '인기순';
                resetLayout();
            } else if (selectedSort === 'deadline') {
                textContent = '마감순';
                resetLayout();
            } else if (selectedSort === 'closed') { // [NEW] 마감 정책 추가
                textContent = '마감 정책';
                expandLayout(); // 레이아웃 확장 적용
            }
        }
        
        // ...
    }
    // ...
});
```

### 3. 마이페이지 텍스트 크기 수정
*   **문제점**: 마이페이지 "나의 관심 지수" 섹션의 뱃지 텍스트(예: #지원금_사냥꾼)가 옆의 퍼센트 숫자(예: 38%)에 비해 글씨 크기가 작아 시각적 균형이 맞지 않음.
*   **해결**: 뱃지 텍스트의 크기를 기존(`text-sm`)보다 조금 키운 `text-base`로 변경하고 굵기(`font-bold`)를 추가하여 가독성을 개선함.

#### `templates/mypage.html` (HTML)
```html
<!-- 수정 전 -->
<!-- <p id="activity-score-text" class="text-xl font-bold text-gray-800">0% <span class="text-sm font-normal text-gray-500">계산 중...</span></p> -->

<!-- 수정 후 -->
<p id="activity-score-text" class="text-xl font-bold text-gray-800">
    0% <span class="text-base font-bold text-gray-500">계산 중...</span>
</p>
```

#### `static/script.js` (Script)
```javascript
// 수정 전
// scoreTextEl.innerHTML = `${data.activity_index}% <span class="text-sm font-normal text-gray-500">${data.level_badge}</span>`;

// 수정 후
scoreTextEl.innerHTML = `${data.activity_index}% <span class="text-base font-bold text-gray-500">${data.level_badge}</span>`;
```
