# 청년 정책 MBTI (P-MBTI) 로직 구현 명세서

## 1. 개요
사용자가 찜(Like)한 정책들의 카테고리를 분석하여 1순위, 2순위 관심사를 도출하고, 이를 바탕으로 16가지 P-MBTI 유형 중 하나를 매핑하여 마이페이지에 노출합니다.

---

## 2. 구현 상태 (Status)
- [x] **백엔드 로직 구현** (`routers/mypage.py`): 점수 산출 및 16가지 유형 매핑 완료
- [x] **API 연동** (`/api/mypage/profile`): 프로필 조회 시 `mbti` 필드 반환
- [x] **프론트엔드 바인딩** (`static/script.js`): 실데이터 연동 및 모달 표출 개선
- [x] **동적 이미지 매핑**: 1순위 장르에 맞춰 카드 이미지가 랜덤하게 변경되도록 구현 완료

---

## 3. 핵심 구현 코드 (Backend Logic)

### 파일: `routers/mypage.py`

#### 1) MBTI 유형 정의 데이터 (`MBTI_DEFINITIONS`)
1순위와 2순위 카테고리 조합을 Key로 하여 유형 정보를 매핑합니다.

#### 2) MBTI 계산 및 이미지 코드 매핑 (`calculate_mbti_result`)
사용자의 찜 데이터를 분석하고, **1순위 카테고리에 맞는 이미지 코드**를 추가로 반환합니다.

```python
def calculate_mbti_result(user_email: str, db: Session):
    # ... (점수 집계 및 1, 2순위 추출 로직 생략) ...
    
    # 결과 매핑
    result = MBTI_DEFINITIONS.get((primary, secondary))
    
    # [NEW] 이미지 매핑을 위한 영문 카테고리 코드 추가
    cat_code_map = {
        "취업": "job",
        "창업": "startup",
        "주거": "housing",
        "금융": "finance",
        "교육": "growth", # 파일명은 growth 사용
        "복지": "welfare"
    }
    result["category_code"] = cat_code_map.get(primary, "welfare")
        
    return result
```

---

## 4. 프론트엔드 이미지 처리 (Frontend Logic)

### 파일: `templates/mypage.html` (Inline Script)

백엔드에서 받은 `category_code`를 사용하여 실제 존재하는 카드 이미지 경로를 생성합니다.

```javascript
function setMbtiResult(data) {
    // ... (텍스트 바인딩 생략) ...

    // [New] 1순위 장르 기반 랜덤 이미지 설정
    // 예: /static/images/card_images/job_3.webp
    const catCode = data.category_code || "welfare";
    const imgNum = Math.floor(Math.random() * 5) + 1; // 1~5번 랜덤
    const imgPath = `/static/images/card_images/${catCode}_${imgNum}.webp`;
    
    const resultImg = document.getElementById('result-img');
    const exportImg = document.getElementById('export-img'); // 공유 이미지용
    
    if(resultImg) resultImg.src = imgPath;
    if(exportImg) exportImg.src = imgPath;
}
```

---

## 5. 테스트 가이드 (How to Test)

### 방법 A: 실제 UI에서 테스트 (사용자 방식)
1. **로그인**: 웹사이트에 로그인합니다.
2. **찜하기(Swipe/Like)**: 의도하는 카테고리(예: 취업) 정책을 찜합니다.
3. **확인**: '마이페이지' MBTI 카드를 클릭합니다.
4. **검증**: 
    - 텍스트 내용이 '연봉 협상의 달인' 등으로 나오는지 확인.
    - **중요**: 배경 이미지가 '취업' 관련 이미지(녹색 계열 등)로 나오는지 확인합니다.
    - 모달을 껐다 켜면 이미지가 바뀔 수도 있습니다(랜덤 1~5번).

### 방법 B: API 데이터 검증 (개발자 방식)
API 응답에 `category_code`가 포함되어 있는지 확인합니다.

**명령어:**
```bash
curl "http://localhost:8000/api/mypage/profile?user_email=test@example.com"
```

**예상 응답 (JSON):**
```json
{
  ...
  "mbti": {
    "type_name": "...",
    "category_code": "job"  <-- 이 필드 확인
  }
}
```
