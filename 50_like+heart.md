# 찜하기(Heart) & 스와이프(Like) 기능 연동 및 상태 유지 구현 문서

## 1. 개요
이 문서는 사용자가 정책 카드에서 **'하트 버튼(찜하기)'**을 눌렀을 때와 스와이프 인터페이스에서 **'오른쪽 스와이프(Like)'**를 했을 때의 기능을 통합하고, 모달을 다시 열었을 때 **'찜 상태'를 유지**하는 구현 내용을 다룹니다. 또한 찜하기/취소 시 화면 리스트와 **통계 그래프가 실시간으로 반영**되는 기능을 포함합니다.

### 주요 기능
1.  **통합 액션**: 모달 하트 클릭과 스와이프 Like는 동일한 DB 테이블(`users_action`)을 공유합니다.
2.  **상태 토글**: 하트를 다시 누르면 찜하기가 취소(`unlike`)되며, DB에서 데이터가 삭제됩니다.
3.  **상태 유지**: 이미 찜한 정책의 모달을 열면, 서버에서 상태를 확인하여 하트가 빨간색으로 활성화된 상태로 표시됩니다.
4.  **실시간 리스트 반영**: 마이페이지 등에서 찜하기를 취소하면 새로고침 없이 해당 카드가 즉시 리스트에서 사라집니다.
5.  **실시간 그래프 업데이트**: 찜하기/취소 액션 발생 시 '관심 키워드 트렌드' 그래프가 즉시 갱신됩니다.

---

## 2. 백엔드 코드 (`routers/mypage.py`)

### 2-1. 액션 저장 및 취소 API
`unlike` 요청 시 데이터를 삭제하고, `like` 요청 시 중복을 방지합니다.

```python
@router.post("/action")
def save_user_action(action: ActionCreate, db: Session = Depends(get_db)):
    """
    사용자의 스와이프 액션(like/pass) 또는 모달 찜하기(like/unlike)를 처리합니다.
    """
    # 1. 좋아요 취소 (unlike) 처리 -> DB에서 삭제
    if action.type == 'unlike':
        db.query(UserAction).filter(
            UserAction.user_email == action.user_email,
            UserAction.policy_id == action.policy_id,
            UserAction.type == 'like'
        ).delete()
        db.commit()
        return {"message": "Like removed"}

    # 2. 좋아요 (like) 중복 방지 처리
    if action.type == 'like':
        existing = db.query(UserAction).filter(
            UserAction.user_email == action.user_email,
            UserAction.policy_id == action.policy_id,
            UserAction.type == 'like'
        ).first()
        
        if existing:
            return {"message": "Already liked"}

    # 3. 새로운 액션 저장
    new_action = UserAction(
        user_email=action.user_email,
        policy_id=action.policy_id,
        type=action.type
    )
    db.add(new_action)
    db.commit()
    
    return {"message": "Action saved", "action_id": new_action.id}
```

### 2-2. 찜 상태 확인 API
모달을 열 때 해당 정책을 찜했는지 확인하기 위한 전용 API입니다.

```python
@router.get("/check")
def check_action_status(user_email: str, policy_id: int, db: Session = Depends(get_db)):
    """
    특정 유저가 특정 정책을 이미 'like' 했는지 확인합니다.
    """
    existing = db.query(UserAction).filter(
        UserAction.user_email == user_email,
        UserAction.policy_id == policy_id,
        UserAction.type == 'like'
    ).first()
    
    return {"liked": True if existing else False}
```

### 2-3. 찜한 정책 목록 조회 API
```python
@router.get("/likes")
def get_liked_policies(user_email: str, db: Session = Depends(get_db)):
    """
    해당 유저가 'like'한 정책들의 상세 정보를 반환합니다.
    """
    # ... (생략)
```

---

## 3. 프론트엔드 코드 (`static/script.js` & `policy_modal.js`)

### 3-1. 그래프 실시간 업데이트 (`static/script.js`)
그래프 생성 로직을 `window.updateMyPageChart` 함수로 캡슐화하여 전역에서 호출 가능하게 만들었습니다.

```javascript
// 전역 업데이트 함수 등록
window.updateMyPageChart = function() {
    const ctx = document.getElementById('myChart');
    if (!ctx || typeof Chart === 'undefined') return;

    fetch(`/api/mypage/stats?user_email=${userEmail}`)
        .then(res => res.json())
        .then(stats => {
            // [중요] 기존 차트 인스턴스 확인 (중복 생성 방지)
            const existingChart = Chart.getChart(ctx);

            if (existingChart) {
                // 기존 차트 데이터 갱신
                existingChart.data.labels = stats.labels;
                existingChart.data.datasets[0].data = stats.data;
                existingChart.update();
            } else {
                // 차트 신규 생성
                new Chart(ctx, { ... });
            }
        });
};

// 페이지 로드 시 최초 실행
window.updateMyPageChart();
```

### 3-2. 리스트/그래프 동기화 (`static/policy_modal.js`)
찜하기 및 취소 성공 시 `updateMyPageChart()`를 호출합니다.

```javascript
fetch('/api/mypage/action', { ... })
  .then(res => res.json())
  .then(res => {
      // 1. [Like일 때] UI 업데이트
      if (type === 'like') { /* ... */ }

      // 2. [Unlike일 때] 화면에서 카드 즉시 제거
      if (type === 'unlike') {
          const cards = document.querySelectorAll(`.policy-card[data-id='${policyId}']`);
          cards.forEach(card => card.remove());
      }
      
      // 3. [공통] 차트 실시간 업데이트
      if (window.updateMyPageChart) window.updateMyPageChart();
  });
```

---

## 4. 테스트 가이드

1.  **로그인**: 사이트에 접속해 로그인을 완료합니다.
2.  **그래프 확인**: 마이페이지의 육각형 그래프 상태를 기억합니다.
3.  **찜하기/취소**: 
    *   정책을 하나 클릭해 모달을 엽니다.
    *   하트를 눌러 상태를 변경합니다 (예: 취업 관련 정책을 찜하기).
4.  **실시간 반영 확인**:
    *   모달을 닫지 않고 뒤로 보이는 마이페이지 배경을 확인하거나, 모달을 닫고 그래프를 확인합니다.
    *   그래프의 해당 영역(예: 취업) 수치가 **즉시 변경**되었는지 확인합니다.
5.  **리스트 확인**: 취소했을 경우 리스트에서 카드가 바로 사라졌는지 확인합니다.
