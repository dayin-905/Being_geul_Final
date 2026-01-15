# 찜한 정책 삭제 및 관리 기능 구현 (완료)

## 1. 개요 (Overview)
마이페이지의 '내가 찜한 정책' 섹션에서 기존의 '모두 보기' 기능을 제거하고, **페이지네이션(Pagination)** 및 **일괄 삭제(Bulk Delete)** 기능을 갖춘 관리 UI를 구현합니다.

## 2. 작업 내역 및 실행 순서 (Execution Steps)

### 1단계: 백엔드 API 수정 (`routers/mypage.py`)
- **목표**: `GET /likes` 엔드포인트에 페이지네이션(Page, Limit) 로직 추가.
- **내용**:
    - `page` (기본 1), `limit` (기본 12) 쿼리 파라미터 추가.
    - 전체 찜 개수(`total_count`)와 총 페이지 수(`total_pages`) 계산.
    - 응답 형식을 리스트 `[]`에서 `{ "policies": [], "total_count": 0, "total_pages": 0, "current_page": 1 }` 형태로 변경.

### 2단계: 프론트엔드 UI 수정 (`templates/mypage.html`)
- **목표**: 정책 리스트 하단에 페이지네이션 컨트롤 컨테이너 추가.
- **내용**:
    - `#mypage-list` `<div>` 아래에 `<div id="pagination-container" class="flex justify-center flex-wrap gap-2 py-8 mt-4"></div>` 추가.

### 3단계: 프론트엔드 로직 수정 (`static/script.js`)
- **목표**: 페이지네이션 처리, 데이터 로드 방식 변경, 삭제 후 페이지 갱신 로직 수정.
- **내용**:
    - `MyPageManager` 객체에 `currentPage`, `itemsPerPage` 상태 변수 추가.
    - `fetchLikes(page)` 메서드 구현: API 호출 후 리스트 렌더링 및 `renderPagination` 호출.
    - `renderPagination(totalCount)` 메서드 구현: `all.html`의 로직을 참고하여 페이지 번호 버튼 생성 및 이벤트 바인딩.
    - `deleteSelected` 수정: 삭제 성공 후 `fetchLikes(currentPage)`를 재호출하여 현재 페이지 갱신 (빈 페이지가 되면 이전 페이지로 이동).

---

## 3. 적용된 코드 (Code Changes)

### 1. 백엔드 (`routers/mypage.py`)

**수정된 `get_liked_policies` 엔드포인트:**
```python
@router.get("/likes")
def get_liked_policies(
    user_email: str, 
    page: int = 1, 
    limit: int = 12, 
    db: Session = Depends(get_db)
):
    # 1. 쿼리 베이스
    query = db.query(UserAction).filter(
        UserAction.user_email == user_email, 
        UserAction.type == 'like'
    )
    
    # 2. 전체 개수 계산
    total_count = query.count()
    if total_count == 0:
        return {
            "policies": [],
            "total_count": 0,
            "total_pages": 0,
            "current_page": page
        }

    total_pages = (total_count + limit - 1) // limit
    
    # 페이지 보정
    if page < 1: page = 1
    if page > total_pages: page = total_pages

    offset = (page - 1) * limit

    # 3. 페이지네이션 적용 (최신순)
    actions = query.order_by(UserAction.created_at.desc())\
                   .offset(offset)\
                   .limit(limit)\
                   .all()
    
    if not actions:
        return {
            "policies": [],
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": page
        }

    # ... (기존 정책 정보 조회 및 매핑 로직 유지) ...
    
    return {
        "policies": result,
        "total_count": total_count,
        "total_pages": total_pages,
        "current_page": page
    }
```

### 2. 프론트엔드 JS (`static/script.js`)

**`MyPageManager` 수정:**
```javascript
const MyPageManager = {
    isEditMode: false,
    currentPage: 1,
    itemsPerPage: 12,
    // ... (기존 변수들) ...
    paginationContainer: document.getElementById('pagination-container'),

    init: function () {
        if (!this.btnManage) return;
        this.bindEvents();
        this.fetchLikes(1); // 초기 로드
    },

    // [데이터 로드 & 렌더링]
    fetchLikes: async function(page) {
        this.currentPage = page;
        const userEmail = localStorage.getItem('userEmail');
        if(!userEmail) return;

        try {
            const res = await fetch(`/api/mypage/likes?user_email=${userEmail}&page=${page}&limit=${this.itemsPerPage}`);
            const data = await res.json();
            
            // 응답 포맷이 변경되었으므로 처리
            const policies = data.policies || []; // 기존 배열 응답 호환성을 위해 체크
            
            if (policies.length === 0) {
                 this.listContainer.innerHTML = `<div class="empty-state"><i class="fa-regular fa-folder-open"></i><p>아직 찜한 정책이 없어요.</p></div>`;
                 this.paginationContainer.innerHTML = "";
            } else {
                this.listContainer.innerHTML = policies.map(item => createCardHTML(item, false)).join('');
                this.renderPagination(data.total_count);
                
                // 편집 모드라면 체크박스 다시 생성
                if(this.isEditMode) {
                    this.addCheckboxesToCards();
                }
                
                // 애니메이션
                if (typeof gsap !== 'undefined') {
                    gsap.from("#mypage-list .policy-card", { y: 20, opacity: 0, duration: 0.4, stagger: 0.05 });
                }
            }
        } catch (e) {
            console.error("Load Error:", e);
        }
    },

    // [페이지네이션 렌더링] (renderPagination 함수 로직 재사용)
    renderPagination: function(totalItems) {
        // ... (all.html의 renderPagination과 유사하게 구현, 클릭 시 this.fetchLikes(pageNum) 호출) ...
    },
    
    // ... (기존 메서드들) ...

    // [삭제 후 처리]
    deleteSelected: async function () {
        // ... (삭제 API 호출 로직) ...
        
        if (res.ok) {
            // 현재 페이지 다시 로드
            this.fetchLikes(this.currentPage);
            // 활동 지수 업데이트
            window.loadUserProfile(); 
            // 편집 모드 해제 또는 유지 (선택 사항)
            this.checkAll.checked = false;
        }
    }
};

// [중요] 초기화 호출 추가
MyPageManager.init();
```

## 4. 트러블슈팅 및 수정 (Troubleshooting & Fixes)

구현 과정에서 발생한 오류와 해결 내역입니다.

### 1. 백엔드 500 오류 (NameError)
- **증상**: `/api/mypage/likes` 호출 시 500 Internal Server Error 발생.
- **원인**: `get_liked_policies` 함수 내에서 정의되지 않은 변수 `categoryColorMap`을 참조하여 `colorCode`를 설정하려 함.
- **해결**: `routers/mypage.py`에서 `colorCode` 필드 할당 로직을 제거함 (프론트엔드에서 색상 처리를 담당하거나 기본값을 사용).

**수정 전:**
```python
"colorCode": categoryColorMap.get(policy.genre, "#777777") # NameError 발생
```
**수정 후:**
```python
# 해당 라인 제거
```

### 2. 프론트엔드 초기화 누락
- **증상**: 페이지 로드 후 찜한 정책 목록이 보이지 않고 아무런 반응이 없음.
- **원인**: `MyPageManager` 객체는 정의되었으나, `MyPageManager.init()`을 호출하는 코드가 누락되거나 이전에 지워짐.
- **해결**: `static/script.js` 파일 하단(DOMContentLoaded 내부)에 초기화 코드를 명시적으로 추가함.

```javascript
// Initialize
MyPageManager.init(); // [추가됨]
```
