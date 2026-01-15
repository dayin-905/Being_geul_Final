# 마감 정책 데이터 분리 및 관리 (is_active 도입) 구현 일지

이 문서는 데이터베이스 내 정책 데이터를 **모집 중(Active)**과 **마감(Inactive)** 상태로 구분하고, 이를 서비스에 반영한 작업 내역을 기술합니다.

## 1. 개요 및 목표
*   **목표**: 기존 `end_date`에 의존하던 로직을 보완하여, 명시적인 `is_active` 상태 값을 통해 정책의 노출 우선순위를 제어합니다.
*   **기대 효과**:
    *   사용자가 목록 조회 시 **모집 중인 정책을 최상단에서 먼저** 확인할 수 있습니다.
    *   마감된 정책도 삭제하지 않고 하단에 배치하거나 필터링할 수 있어 데이터 자산을 유지할 수 있습니다.
    *   **[신규]** 마감된 정책은 카드 썸네일에 "모집 마감" 배지와 흑백 효과를 적용하여 사용자가 직관적으로 구분할 수 있습니다.

## 2. 작업 구현 상세

### 2.1 마감 기준 및 로직 (Policy)
마감된 정책을 판단하는 기준은 DB의 **`end_date`** 컬럼과 **현재 날짜(Today)**를 비교하여 결정됩니다.

| 케이스 | 조건 | 판별 결과 (is_active) | 의미 |
| :--- | :--- | :--- | :--- |
| **마감됨** | `end_date` < **오늘** | **False** | 날짜가 지난 정책 (어제까지였던 정책 포함) |
| **모집 중** | `end_date` >= **오늘** | **True** | 오늘 마감이거나, 아직 기간이 남은 정책 |
| **상시 모집**| `end_date`가 **없음 (Null)** | **True** | 마감일이 정해지지 않은 상시 모집 정책 |

---

### 2.2 구현 코드

#### [Step 1] DB 모델 스키마 변경 (`models.py`)
`Policy` 모델(테이블명: `being_test`)에 `is_active` 컬럼을 추가했습니다.

```python
# /apps/Being_geul_Final/models.py

from sqlalchemy import Column, Integer, Text, String, DateTime, Date, ForeignKey, Boolean
# ...
class Policy(Base):
    # ...
    # [NEW] 공개 여부 (True: 모집중, False: 마감)
    is_active = Column(Boolean, default=True)
```

#### [Step 2] 데이터 마이그레이션 및 초기화 (`update_is_active_db.py`)
운영 중인 DB에 컬럼을 추가하고 데이터를 초기화하는 스크립트를 작성 및 실행했습니다.

```python
# /apps/Being_geul_Final/10_dain/ect/update_is_active_db.py

def update_db_schema_and_data():
    # ...
    # 1. 컬럼 추가 (DDL)
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE being_test ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
        conn.commit()

    # 2. 데이터 업데이트 로직
    today = date.today()
    for policy in all_policies:
        if policy.end_date and policy.end_date < today:
            policy.is_active = False # 마감 처리
        else:
            policy.is_active = True # 모집 중
    # ...
```
**실행 결과**:
*   전체 정책 수: 1090개
*   **모집 중 (Active)**: 1000개
*   **모집 마감 (Inactive)**: 90개 (약 8.3%)

#### [Step 3] 백엔드 정렬 로직 고도화 (`routers/all.py`)
어떤 정렬 옵션을 선택하더라도 `is_active`가 True인 항목이 항상 먼저 나오도록 정렬 우선순위를 변경했습니다.

```python
# /apps/Being_geul_Final/routers/all.py

@router.get("/api/cards")
async def api_get_cards(...):
    # ...
    # 정렬 기능 - [수정] 모든 정렬 기준에 '모집 중(is_active=True)' 우선 적용
    if sort == 'latest':
        # 최신순: 모집중 우선 -> 생성일 내림차순
        query = query.order_by(Policy.is_active.desc(), Policy.created_at.desc().nulls_last())
    # ...
    
    # 응답 데이터에 is_active 필드 추가
    result.append({
        # ...
        "is_active": p.is_active  # [NEW] 프론트엔드 활용용
    })
```

#### [Step 4] UI/UX 개선 (마감 배지 및 흑백 처리) (`templates/all.html`)
마감된 정책(`is_active: false`) 카드를 사용자가 쉽게 식별할 수 있도록 스타일을 적용했습니다.

```javascript
/* templates/all.html */

// 1. 매핑 로직에 is_active 추가
policyData = data.map(item => {
    return {
        // ...
        is_active: item.is_active // [NEW] 상태 매핑
    };
});

// 2. 렌더링 로직 (renderCards) 수정
const isClosed = item.is_active === false;

// 2-1. 마감 배지 (이미지 위 오버레이)
const badgeHtml = isClosed ? `
    <div class="absolute inset-0 bg-black/60 flex items-center justify-center z-10 backdrop-blur-[1px]">
         <span class="text-white font-bold text-lg border border-white/80 px-4 py-1.5 rounded-full tracking-wider">모집 마감</span>
    </div>` : '';

// 2-2. 이미지 흑백 효과 및 투명도 조절
const imageClass = isClosed ? 'grayscale opacity-80' : '';

// 2-3. 날짜 텍스트 강조 (붉은색)
const dateClass = isClosed ? 'text-red-500 font-bold' : '';
```

## 3. 결론
이번 작업을 통해 전체 데이터를 분리하지 않고도, 하나의 목록에서 효율적으로 **"모집 중"** 정책을 강조하고 **"마감된"** 정책을 시각적으로 구분하여 제공할 수 있게 되었습니다. 이는 사용자 경험을 해치지 않으면서 데이터 자산을 효과적으로 관리하는 방법입니다.

---

## 4. 테스트 및 검증 가이드 (QA)

다음의 세 가지 단계로 구현이 정상적으로 동작하는지 확인할 수 있습니다.

### 4.1 데이터베이스(DB) 확인
터미널에서 Python 쉘을 열어 실제 데이터가 업데이트되었는지 확인합니다.

```bash
# 1. Python 쉘 실행 (프로젝트 루트에서)
python3

# 2. 다음 코드 입력하여 확인
from database import SessionLocal
from models import Policy

db = SessionLocal()

# 모집 중인 데이터 개수 (is_active=True)
active_count = db.query(Policy).filter(Policy.is_active == True).count()

# 마감된 데이터 개수 (is_active=False)
inactive_count = db.query(Policy).filter(Policy.is_active == False).count()

print(f"모집 중: {active_count}개, 마감됨: {inactive_count}개")
# 예상 결과: 모집 중 1000개, 마감됨 90개 (데이터 상황에 따라 다름)
```

### 4.2 API 응답 확인
서버를 실행한 후(`python3 main.py`), 브라우저 주소창에 다음 URL을 입력하여 JSON 응답을 확인합니다.

*   **URL**: `http://localhost:8000/api/cards`
*   **검증 포인트**:
    1.  리스트의 **첫 번째 아이템**의 `is_active` 값이 `true`인지 확인합니다.
    2.  리스트의 **가장 마지막 아이템**의 `is_active` 값이 `false`인지 확인합니다. (정렬 로직 검증)

### 4.3 UI(화면) 확인
`http://localhost:8000/all.html` 페이지에 접속하여 시각적 요소를 확인합니다.

1.  **배지 표시**: 페이지의 가장 마지막 페이지로 이동해봅니다. (또는 정렬이 제대로 되었다면 맨 뒤쪽에 있음)
2.  **스타일 확인**:
    *   이미지 위에 **"모집 마감"**이라는 검은색 반투명 배지가 떠 있는지 확인합니다.
    *   이미지가 흑백(GrayScale)으로 변해 있는지 확인합니다.
    *   하단 날짜 텍스트가 **빨간색**으로 표시되어 있는지 확인합니다.

---

## 5. 논의 사항 및 분석 (2026-01-06 추가)

### 5.1 현안: 데이터 품질 문제 (Period Parsing)
현재 `end_date` 추출 로직(텍스트 파싱)의 한계와 원본 데이터(`period`)의 비정형성으로 인해, 실제로는 마감되었으나 시스템 상에서 '모집 중'으로 분류된 정책이 다수 발견됨.

**QA 발견 사항**:
*   사용자 검증 결과, 2024~2025년 초 기준으로 마감된 정책들이 `True` 상태로 남아 상단에 노출되는 문제 확인.
*   **원인**: 온통청년 API에서 가져온 `period` 텍스트가 매우 다양하고 불규칙하여 단순 파싱으로는 모든 케이스를 커버하지 못함.

### 5.2 해결 방안 검토: 크롤링 기반 상태 동기화
*   **아이디어**: 원본 링크(`link` 컬럼)를 타고 들어가 '온통청년' 웹페이지의 HTML을 분석. 마감된 정책에만 붙는 CSS 클래스(`btn-state09`, 붉은색 스타일 등) 유무를 확인.
*   **장점**: 텍스트 파싱보다 월등히 높은 정확도로 마감 여부(`is_active`)를 판별 가능.
*   **단점**: 대량의 요청(1,090회 이상) 필요. 실시간 처리는 불가능하며, 배치 스크립트로 수행해야 함. IP 차단 위험 존재.

### 5.3 추가 데이터 입수 계획에 따른 분석
**상황**:
*   현재 DB: 2025-12-12 기준 데이터.
*   예정: 2025-12-13 ~ 2026-01-09 최신 데이터 추가 확보 및 DB 병합 예정.

**분석 및 제언**:
데이터 추가 시에도 데이터 형태(불규칙성)는 동일할 것이므로, DB 병합 작업 후 '크롤링 기반 데이터 검증'을 수행하는 것이 데이터 품질을 높이는 가장 확실한 방법임을 확인함.

## 6. 향후 일정 및 계획 (Roadmap)
팀 논의를 통해 다음과 같은 일정으로 진행하기로 합의함 (2026.01.06 기준).

*   **1단계 (2026.01.09)**: 팀원에 의한 신규 데이터(2025/12/13 ~ 2026/01/09) 추출 작업.
*   **2단계 (2026.01.12)**: 기존 DB와 신규 추출 DB의 병합(Migration) 작업 진행.
*   **3단계 (병합 직후)**: '크롤링 기반 마감 상태 동기화' 스크립트 실행 여부 최종 결정.
    *   이때 데이터 상태를 보고 크롤링을 수행할지 결정.
*   **4단계 (후속 논의)**: 데이터 정제가 완료된 후, `main.html` 및 `mypage.html` 등 다른 페이지에도 '마감 배지(Step 4)' UI를 확대 적용할지 논의 및 결정.

### 6.1 (2026-01-07 추가) '마감 정책' 탭 구현
사용자 요청에 따라 마감된 정책만 별도로 모아볼 수 있는 기능을 추가하였습니다.

#### 1. UI 변경 (`all.html`)
정렬 모달창에 **'마감 정책'** 버튼을 추가했습니다 (`data-sort="closed"`).
이 버튼을 클릭하면 `is_active` 상태가 `False`인(마감된) 정책들만 필터링되어 표시됩니다.

#### 2. 백엔드 로직 추가 (`routers/all.py`)
`api_get_cards` 함수에 `closed` 정렬 옵션을 추가했습니다.
```python
elif sort == 'closed':
    # 마감 정책 탭: 마감된 정책(is_active=False)만 모아보기
    # 최신 마감일 순(최근에 끝난 것부터)으로 정렬
    query = query.filter(Policy.is_active == False).order_by(Policy.end_date.desc().nulls_last())
```

#### 3. 추가 테스트 가이드
*   **API 확인**: `http://localhost:8000/api/cards?sort=closed` 로 접속 시 모든 아이템의 `is_active`가 `false`여야 합니다.
*   **UI 확인**: 정렬 메뉴에서 '마감 정책' 선택 시, 화면에 보이는 모든 카드가 흑백 처리 및 '모집 마감' 배지가 붙어 있어야 합니다.
