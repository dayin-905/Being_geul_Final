# MyPage Filter & Search Implementation

## 1. 개요 (Overview)
마이페이지의 '내가 찜한 정책' 목록에서 사용자가 정책을 쉽게 찾을 수 있도록 **검색 및 필터 기능**을 구현했습니다.
기존의 '편집' 모드와 함께 작동하며, 검색어(키워드), 분야(Category), 지역(Region), 정렬(Sort) 기능을 제공합니다.

## 2. 작업 내역 (Changes)

### 2.1 Backend: API 수정 (`routers/mypage.py`)
`/api/mypage/likes` 엔드포인트에 필터링 파라미터(`keyword`, `category`, `region`, `sort`)를 추가하고, DB 쿼리에 적용했습니다.

```python
# routers/mypage.py

@router.get("/likes")
def get_liked_policies(
    user_email: str, 
    page: int = 1, 
    limit: int = 12, 
    keyword: Optional[str] = None,   # [NEW] 검색 키워드
    category: Optional[str] = None,  # [NEW] 분야 필터
    region: Optional[str] = None,    # [NEW] 지역 필터
    sort: Optional[str] = None,      # [NEW] 정렬 방식
    db: Session = Depends(get_db)
):
    """
    해당 유저가 'like'한 정책들의 상세 정보를 반환합니다. (검색/필터/정렬/페이지네이션 적용)
    """
    # 1. Base Query
    query = db.query(UserAction, Policy).join(Policy, UserAction.policy_id == Policy.id).filter(
        UserAction.user_email == user_email, 
        UserAction.type == 'like'
    )
    
    # 2. 필터 적용
    # 2-1. 키워드 검색 (제목 or 요약)
    if keyword:
        query = query.filter(
            (Policy.title.ilike(f"%{keyword}%")) | 
            (Policy.summary.ilike(f"%{keyword}%"))
        )

    # 2-2. 분야(Category) 필터
    if category and category != "전체":
        query = query.filter(Policy.genre.ilike(f"%{category}%"))

    # 2-3. 지역(Region) 필터
    if region and region != "전체" and region != "전국":
        query = query.filter(
            (Policy.region.ilike(f"%{region}%")) | 
            (Policy.region == "전국")
        )

    # 2-4. 정렬 방식
    if sort == 'deadline':
        query = query.order_by(Policy.end_date.asc())
    elif sort == 'popular':
        query = query.order_by(UserAction.created_at.desc()) # (임시) 최신순
    elif sort == 'closed':
        query = query.filter(Policy.end_date < date.today()).order_by(Policy.end_date.desc())
    else: # latest (기본)
        query = query.order_by(UserAction.created_at.desc())

    # ... (페이지네이션 및 응답 로직 유지) ...
```

### 2.2 Frontend: UI 구현 (`templates/mypage.html`)
기존 '편집' 버튼 옆에 **'필터' 버튼**을 추가하고, 확장 가능한 **검색창(Search Bar)** 영역을 구현했습니다.
또한 스타일 일관성을 위해 폰트 크기를 키웠습니다.

```html
<!-- templates/mypage.html -->

<!-- 상단 헤더 및 버튼 영역 -->
<div class="flex justify-between items-end mb-6 relative">
    <div>
        <h2 class="text-2xl font-bold mb-2">내가 찜한 정책 ❤️</h2>
        <p class="text-stone-500">관심 있는 정책을 모아보고 관리할 수 있어요.</p>
    </div>

    <!-- 버튼 그룹 -->
    <div class="flex items-center gap-3">
            <button id="btn-toggle-search"
            class="text-lg text-gray-500 hover:text-black font-bold transition-colors flex items-center gap-1.5 px-2 py-1 rounded-lg hover:bg-gray-100">
            <i class="fa-solid fa-magnifying-glass"></i>
            필터
        </button>
        <div class="w-[1px] h-4 bg-gray-300"></div>
        <button id="btn-manage-likes"
            class="text-lg text-gray-500 hover:text-black font-bold transition-colors px-2 py-1 rounded-lg hover:bg-gray-100">
            편집
        </button>
    </div>
</div>

<!-- 검색창 영역 (숨김 상태로 시작) -->
<div id="mypage-search-bar" class="hidden mb-8 animate-fade-in origin-top">
    <div class="max-w-3xl mx-auto">
        <div class="flex items-center gap-2 p-1.5 bg-white rounded-full border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
            <!-- 돋보기 아이콘 -->
            <div class="pl-4 text-gray-400">
                <i class="fa-solid fa-magnifying-glass"></i>
            </div>
            <!-- 검색어 입력 -->
            <input type="text" id="mypage-search-input" 
                class="flex-1 bg-transparent border-none outline-none text-gray-700 h-10"
                placeholder="키워드를 입력해보세요 (예: 주거지원, 취업)">
            
            <!-- 필터 버튼 그룹 (분야, 지역, 정렬) -->
             <div class="flex items-center gap-1 pr-1">
                <!-- 분야 필터/드롭다운 -->
                <div class="relative">
                    <button id="btn-filter-category" class="...">
                        <span id="label-category">분야</span>
                        <i class="fa-solid fa-chevron-down"></i>
                    </button>
                    <!-- 드롭다운 메뉴 생략 -->
                </div>
                <!-- 지역 필터 -->
                <button id="btn-filter-region" class="...">
                    <i class="fa-solid fa-map"></i>
                    <span id="label-region">지역</span>
                </button>
                <!-- 정렬 필터 -->
                <div class="relative">
                     <button id="btn-filter-sort" class="...">
                        <i class="fa-solid fa-sort"></i>
                        <span id="label-sort">정렬</span>
                    </button>
                    <!-- 드롭다운 메뉴 생략 -->
                </div>
            </div>
        </div>
    </div>
</div>

<!-- 지역 선택 모달 추가 (Body 하단) -->
<div id="region-modal" class="... hidden ...">
    <!-- ... (지역 버튼들) ... -->
</div>
```

### 2.3 Frontend: 로직 구현 (`static/script.js`)
`MyPageManager` 객체를 확장하여 필터 상태(`currentKeyword`, `currentCategory` 등)를 관리하고, 이벤트 바인딩 및 API 호출 로직을 업데이트했습니다.

```javascript
// static/script.js

const MyPageManager = {
    // ... 기존 설정 ...
    
    // [NEW] 필터 상태
    currentKeyword: '',
    currentCategory: null,
    currentRegion: null,
    currentSort: 'latest',

    // 요소 바인딩 및 초기화
    init: function () {
        this.fetchLikes(1);
        this.bindEvents();        // 편집 관련
        this.bindFilterEvents();  // [NEW] 필터 관련
    },

    bindFilterEvents: function() {
        // 검색창 토글
        this.btnToggleSearch?.addEventListener('click', () => {
            this.searchBar.classList.toggle('hidden');
        });

        // 엔터키 검색
        this.inputSearch?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.currentKeyword = e.target.value;
                this.fetchLikes(1);
            }
        });

        // 카테고리/정렬 드롭다운 토글 및 지역 모달 제어 로직
        // ... (생략) ...
        
        // 인라인 함수 연결 (window 객체 활용)
        window.selectCategory = (cat) => { /* ... */ this.fetchLikes(1); };
        window.selectSort = (sort) => { /* ... */ this.fetchLikes(1); };
    },

    // [UPDATED] API 호출
    fetchLikes: function (page) {
        // ... (유저 체크) ...

        const params = new URLSearchParams();
        params.append('user_email', userEmail);
        params.append('page', page);
        params.append('limit', this.itemsPerPage);
        
        // 필터 파라미터 추가
        if (this.currentKeyword) params.append('keyword', this.currentKeyword);
        if (this.currentCategory) params.append('category', this.currentCategory);
        if (this.currentRegion) params.append('region', this.currentRegion);
        if (this.currentSort) params.append('sort', this.currentSort);

        fetch(`/api/mypage/likes?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                // UI 렌더링 (리스트, 페이지네이션)
            });
    }
}
```

## 3. 결과 (Result)
- **사용자 경험 개선**: 이제 사용자는 수많은 찜한 정책 중에서 원하는 조건(분야, 지역 등)의 정책을 빠르게 필터링하여 찾아볼 수 있습니다.
- **디자인 통일성**: Main 페이지의 검색 UX와 일관된 디자인을 마이페이지에도 적용하여 통일감을 주었습니다.
