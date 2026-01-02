# 메인 페이지 및 DB 연동 구현 기록 (main_DB.md)

## 1. 개요
*   **목표**: 메인 페이지 DB 연동 및 로그인 500 에러 해결, 카드 셔플 로직 복구, UI 성능 최적화, 사용성 개선(키보드).
*   **수정 내역**:
    1. `routers/auth.py` 500 에러 원인인 `User.provider` 컬럼 누락 문제 해결 (Schema Update & Table Reset).
    2. 메인 페이지 틴더 카드가 장르별로 정렬되어 나오는 문제 해결 (Shuffle 로직 복구).
    3. 틴더 카드 등장 애니메이션 렉 현상 완화 (대상 축소).
    4. **[New]** 키보드(화살표)를 이용한 카드 스와이프 기능 추가.

---

## 2. 작업 내역 및 코드 상세

### [Critical Fix] User 모델 수정 (`models.py`)
*   **문제점**: 로그인 로직에서 사용되는 `provider` 필드가 누락되어 500 에러 발생.
*   **해결**: `models.py`에 `provider` 컬럼 추가 및 DB 테이블 재생성.
    ```python
    provider = Column(String, default="local")
    ```

### [Bug Fix] 틴더 카드 셔플 로직 복구 (`routers/main_page.py`)
*   **문제점**: 슬라이드용 데이터 추가 작업 도중, `random.shuffle(all_picks)` 코드가 실수로 삭제됨. 이로 인해 카드가 카테고리 순서대로(취업 -> 창업 -> ...) 노출됨.
*   **해결**: 셔플 코드 재삽입.
    ```python
    # 2. 각 카테고리별 추출 (루프)
    # ...
    all_picks.extend(policies)

    # 3. [복구] 전체 리스트 셔플
    random.shuffle(all_picks) 

    # 4. 슬라이드 데이터 조회...
    ```

### [Optimization] 틴더 카드 애니메이션 최적화 (`static/script.js`)
*   **문제점**: 18개 이상의 카드가 동시에 GSAP `from` 애니메이션(위치 이동 및 투명도 변경)을 수행하면서 브라우저 렌더링 렉(Lag) 발생.
*   **해결**: 전체 카드가 아닌, 사용자가 보게 될 **최상위 5장(DOM상 마지막 5개)**에만 애니메이션을 적용하도록 선택자 수정.
    ```javascript
    // 수정 전: ".tinder-card" (모두 선택)
    // 수정 후: ".tinder-card:nth-last-child(-n+5)" (상위 5개만 선택)
    gsap.from(".tinder-card:nth-last-child(-n+5)", { ... });
    ```
    
### [Feature] 키보드 스와이프 기능 추가 (`static/script.js`)
*   **목표**: 마우스/터치 대신 키보드 방향키로도 카드를 넘길 수 있게 하여 접근성 및 편의성 향상.
*   **구현**: `CardSwiper.setupEvents` 메서드에 `keydown` 리스너 추가.
    ```javascript
    document.addEventListener('keydown', (e) => {
        // 현재 스택의 최상단 카드(DOM 마지막 요소) 식별
        const topCard = document.querySelectorAll('.tinder-card')[length - 1];
        if (e.key === 'ArrowLeft') this.swipeCard(topCard, 'left');
        if (e.key === 'ArrowRight') this.swipeCard(topCard, 'right');
    });
    ```

---

## 3. 진행 상황 로그
*   [x] `models.py` 수정 & DB `users` 테이블 리셋 완료.
*   [x] `routers/main_page.py` 셔플 로직 복구 완료.
*   [x] `static/script.js` 애니메이션 최적화 완료.
*   [x] `static/script.js` 키보드 제어 기능 추가 완료.
