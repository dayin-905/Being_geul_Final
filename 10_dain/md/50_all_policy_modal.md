# `all.html` 정책 모달 통합 작업 내역

## 개요
기존 `all.html` (전체 정책 보기) 페이지에서 정책 카드를 클릭했을 때 새 창으로 링크가 열리던 방식을 수정하여, `main.html`과 동일하게 **정책 상세 정보 모달**이 뜨도록 변경했습니다. 이를 위해 모달 컴포넌트를 포함시키고, 카드 클릭 이벤트를 수정했습니다.

## 상세 변경 내용

### 1. 카드 클릭 이벤트 핸들러 변경 (`renderCards` 함수 내)
Javascript로 동적 생성되는 카드 엘리먼트의 `onclick` 속성을 변경했습니다.

- **기존 코드**: `window.open`을 사용하여 직접 링크 이동
  ```javascript
  <div class="perspective-wrap h-full cursor-pointer group" onclick="window.open('${item.link || '#'}', '_blank')" data-json="${itemJson}" style="z-index: 1;">
  ```

- **변경 후**: `openCardModal(this)`를 호출하여 모달 실행
  ```javascript
  <div class="perspective-wrap h-full cursor-pointer group" onclick="openCardModal(this)" data-json="${itemJson}" style="z-index: 1;">
  ```

### 2. 모달 컴포넌트 및 스크립트 추가
`all.html` 파일 하단 `</body>` 태그 직전에 모달 HTML 템플릿과 제어 스크립트를 추가했습니다. `main.html`과 코드 스타일을 통일했습니다.

**추가된 코드:**
```html
    <!-- policy-modal -->

    {% include "components/policy_modal.html" %}

    <script src="/static/policy_modal.js"></script>
</body>
```

### 3. 중복/더미 함수 제거
`all.html` 내부에 임시로 정의되어 있던 테스트용 `openCardModal` 함수를 제거하여, `policy_modal.js`에 정의된 실제 함수가 호출되도록 정리했습니다.

**제거된 코드:**
```javascript
// 기존에 존재했던 더미 함수 (삭제됨)
function openCardModal(element) {
    console.log("모달 열기:", element.dataset.json);
}
```

### 4. JSON 데이터 인코딩 방식 수정 (Bug Fix)
`all.html`에서 모달이 작동하지 않는 문제를 해결했습니다. 기존 `encodeURIComponent` 방식은 `main.html`의 로직과 달라 `JSON.parse` 에러를 유발했습니다. 이를 `main.html`과 동일하게 HTML 엔티티 이스케이프 방식으로 변경하여 모달에 데이터가 정상적으로 전달되도록 수정했습니다.

- **원인**: `encodeURIComponent`로 인코딩된 데이터는 모달 스크립트에서 바로 파싱할 수 없었습니다.
- **해결**: `JSON.stringify(item).replace(/"/g, '&quot;')` 로 변경하여 속성값에 안전하게 삽입되도록 했습니다.

**변경 코드:**
```javascript
// 변경 전
const itemJson = encodeURIComponent(JSON.stringify(item));

// 변경 후
const itemJson = JSON.stringify(item).replace(/"/g, '&quot;');
```

## 테스트 방법

수정 사항이 올바르게 적용되었는지 확인하기 위해 다음 절차를 따르세요.

1.  **서버 실행**: 터미널에서 `uvicorn main:app --reload` 명령어로 서버를 실행합니다.
2.  **페이지 접속**: 웹 브라우저에서 `http://localhost:8000/all.html` (또는 해당 라우트)로 접속합니다.
3.  **카드 클릭**:
    *   화면에 표시된 임의의 정책 카드를 클릭합니다.
    *   **기대 결과**: 새 창이나 새 탭이 열리지 않고, 현재 페이지 위에 **정책 상세 정보 모달**이 뜹니다.
4.  **모달 내용 확인**:
    *   모달에 해당 카드의 제목, 설명, 이미지, 카테고리 등의 정보가 올바르게 표시되는지 확인합니다.
    *   '원문 보러 가기', '공유하기', '찜하기' 등의 버튼이 정상적으로 작동하는지 확인합니다.
5.  **모달 닫기**:
    *   모달의 우측 상단 'X' 버튼을 클릭하거나, 모달 외부 배경(dimmed 영역)을 클릭했을 때 모달이 정상적으로 닫히는지 확인합니다.
