# 170. Final Fix: 마이페이지 차트 업데이트 누락 수정

## 1. 문제 상황 (Problem)
마이페이지의 "찜한 정책 관리"에서 정책을 삭제했을 때, 아래 두 가지 항목은 정상적으로 업데이트되었으나 **"관심 키워드 트렌드(레이더 차트)"**는 변하지 않는 문제가 발생했습니다.

1. **찜한 정책 목록**: 삭제된 항목이 사라짐 (정상)
2. **나의 관심 지수(게이지 바)**: `window.loadUserProfile()` 호출로 업데이트됨 (정상)
3. **관심 키워드 트렌드(그래프)**: 삭제 후에도 기존 모양 그대로 유지됨 (오류)

그래프가 변경되려면 페이지를 새로고침(F5)해야만 했습니다.

## 2. 원인 분석 (Cause)
`static/script.js`의 `deleteSelected` 함수(삭제 처리 로직)에서 데이터 삭제 성공 후 UI를 갱신하는 과정에서 **차트 업데이트 함수 호출이 누락**되어 있었습니다.

- **기존 코드**:
  ```javascript
  // 활동 지수(프로필) 업데이트는 있었음
  if (typeof window.loadUserProfile === 'function') {
      setTimeout(() => window.loadUserProfile(), 500);
  }
  
  // 목록 재로딩도 있었음
  this.fetchLikes(this.currentPage);
  
  // -> 하지만 window.updateMyPageChart() 호출이 없었음!
  ```

이로 인해 삭제 API가 성공하여 백엔드 데이터는 변경되었지만, 프론트엔드의 차트 컴포넌트는 다시 그려지지(re-render) 않았습니다.

## 3. 해결 방법 (Solution)
`deleteSelected` 함수의 성공(`res.ok`) 처리 블록에 `window.updateMyPageChart()` 호출을 추가하여, 정책 삭제 직후 차트 데이터를 새로 받아오고 다시 그리도록 수정했습니다.

### 수정된 코드 (`static/script.js`)

```javascript
deleteSelected: async function () {
    // ... (삭제 API 호출 및 확인 로직) ...

    if (res.ok) {
        // [기존] 활동 지수 업데이트
        if (typeof window.loadUserProfile === 'function') {
            setTimeout(() => window.loadUserProfile(), 500);
        }

        // [추가됨] 차트 업데이트 (삭제 반영) ★
        if (typeof window.updateMyPageChart === 'function') {
            setTimeout(() => window.updateMyPageChart(), 500);
        }

        // [기존] 리스트 재로딩
        this.fetchLikes(this.currentPage);
    }
    // ...
}
```

이제 정책 삭제 시 그래프 데이터도 즉시 동기화되어 사용자에게 정확한 관심사 분포를 보여줍니다.

## 4. 마이페이지 0점 데이터 그래프 오류 수정 (Data Distortion Fix)

### 4.1 문제 상황 (Problem)
- **찜한 정책 개수 불일치**: 찜한 정책이 실제로는 없는데(리스트 0개), 카운트는 '15'로 표시됨.
- **유령 그래프**: 데이터가 모두 0임에도 불구하고 그래프가 육각형 모양으로 유지됨.
- **캐시 문제**: 수정 사항이 브라우저에 즉시 반영되지 않음.

### 4.2 원인 분석 (Cause)
1.  **Orphaned Data (고아 데이터)**: `UserAction`(좋아요 기록) 테이블에는 데이터가 남아있으나, 해당 `Policy`(정책)가 삭제되어 조인되지 않는 '찌꺼기 데이터'가 존재했습니다. 단순 카운트 쿼리는 이를 걸러내지 못했습니다.
2.  **Chart.js Auto-scaling**: 데이터가 `[0, 0, 0, 0, 0, 0]`일 때, Chart.js가 y축의 최소/최대 범위를 임의로 설정(예: -1 ~ 1)하면서 **0점이 차트의 정중앙이 아닌 중간 지점**에 찍히는 왜곡이 발생했습니다.
3.  **Browser Caching**: `script.js` 파일이 브라우저에 캐시되어 있어 변경된 로직(안내 메시지 표시 등)이 실행되지 않았습니다.

### 4.3 해결 방법 (Solution)

#### [Backend] 1. 유효하지 않은 데이터 필터링 (`routers/mypage.py`)
좋아요 개수(`like_count`)를 셀 때, 정책 테이블(`Policy`)과 조인(Join)하여 실제 존재하는 정책에 대한 좋아요만 카운트하도록 수정했습니다.

```python
# routers/mypage.py

# [수정 전] 단순 카운트 (삭제된 정책도 포함됨)
# like_count = db.query(UserAction).filter(...).count()

# [수정 후] Policy 테이블과 조인하여 유효한 정책만 카운트
like_count = db.query(UserAction)\\
    .join(Policy, UserAction.policy_id == Policy.id)\\
    .filter(
        UserAction.user_email == user_email, 
        UserAction.type == 'like'
    ).count()
```

*(참고: 이미 존재하는 15개의 찌꺼기 데이터는 별도 스크립트로 DB에서 완전 삭제 처리함)*

#### [Frontend] 2. 0점 데이터 예외 처리 (`static/script.js`)
데이터가 모두 0일 경우, 왜곡된 그래프를 그리는 대신 차트를 파괴(destroy)하고 **안내 메시지**를 띄우도록 변경했습니다. 또한 차트의 스케일을 `0~100`으로 강제 고정하여 왜곡을 방지했습니다.

```javascript
/* static/script.js - window.updateMyPageChart 내부 */

// 1. 데이터 검증: 모든 값이 0인지 확인
const allZero = stats.data.every(val => val === 0);

// 2. 데이터가 0이면 그래프 대신 안내 메시지 표시
if (allZero) {
    if (existingChart) existingChart.destroy(); // 기존 차트 삭제
    
    ctx.style.display = 'none'; // 캔버스 숨김
    // 안내 메시지 요소(DOM) 생성 및 표시 로직...
    return; // 차트 생성 중단
}

// 3. 차트 생성 시 스케일 고정 (0점 왜곡 방지)
new Chart(ctx, {
    // ...
    options: {
        scales: {
            r: {
                min: 0,
                max: 100, // [중요] 최대값 100으로 고정
                beginAtZero: true
            }
        }
    }
});
```

#### [HTML] 3. 강력 새로고침 적용 (Cache Busting)
`mypage.html`에서 스크립트를 불러올 때 쿼리 스트링(`?v=...`)을 추가하여 브라우저가 강제로 새 파일을 받아오도록 조치했습니다.

```html
<!-- templates/mypage.html -->
<!-- [FIX] 버전 파라미터 추가로 캐시 문제 해결 -->
<script src="/static/script.js?v=20260115_fix"></script>
```

## 5. 차트 스케일 확장 및 UI 개선 (Chart Scale & UI Update)

### 5.1 개선 내용
1.  **그래프 최대치 확장**: 100점이 넘는 '초고관심' 분야를 표현하기 위해 **최대값을 120점으로 상향**했습니다. 이를 통해 그래프가 100점(육각형)을 뚫고 나가는 시각적 재미 요소를 추가했습니다.
2.  **불필요한 UI 제거**: '관심 키워드 트렌드' 카드 상단의 점 세 개(...) 아이콘 버튼을 삭제하여 깔끔한 헤더를 구성했습니다.

### 5.2 수정된 코드 (`static/script.js`)

```javascript
options: {
    scales: {
        r: {
            min: 0,
            max: 120, // [FIX] 120점까지 확장 (재미 요소)
            beginAtZero: true,
            ticks: {
                stepSize: 20,
                count: 7 // 0, 20, 40, 60, 80, 100, 120 (총 7단계)
            }
        }
    }
}
```

### 5.3 캐시 갱신
`mypage.html`의 스크립트 로드 버전을 업데이트하여 변경 사항이 즉시 반영되도록 했습니다.

```html
<script src="/static/script.js?v=20260116_max120"></script>
```

