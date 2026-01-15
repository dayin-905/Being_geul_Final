# Admin 페이지 통합 및 DB 모델 수정 기록 (greg3.md)

## 1. 개요
*   **작업 날짜**: 2025-12-30
*   **목표**: `admin` 기능 추가 과정에서 발생한 `models.py`의 `NameError` 및 클래스 중복 정의 에러 해결, 그리고 `main.py`의 import 에러 해결.
*   **관련 파일**:
    *   `models.py`: SQLAlchemy 모델 정의
    *   `routers/admin.py`: 관리자 페이지 라우터
    *   `main.py`: 앱 엔트리 포인트

---

## 2. 에러 로그 및 원인 분석

### Error 1: `NameError: name 'relationship' is not defined`
*   **로그**:
    ```
    File "/apps/Being_geul_Final/models.py", line 37, in User
      actions = relationship("UserAction", back_populates="user", cascade="all, delete")
    NameError: name 'relationship' is not defined
    ```
*   **원인**: `models.py` 상단에 `from sqlalchemy.orm import relationship` 구문이 누락됨.

### Error 2: `UserAction` 클래스 중복 및 통합 문제
*   **현상**: `models.py` 하단에 독립적으로 `user = relationship(...)` 코드만 남아있거나, `UserAction` 클래스가 두 번 정의되려는 흔적이 있었음.
*   **원인**: Admin 기능용 `UserAction` (또는 `user_actions`) 테이블 정의를 추가하려다가, 기존 코드와 충돌하거나 코드가 꼬임.

### Error 3: `NameError: name 'admin' is not defined`
*   **로그**:
    ```
    File "/apps/Being_geul_Final/main.py", line 35, in <module>
    app.include_router(admin.router)      # [NEW] 관리자 페이지 기능 (admin.html)
                       ^^^^^
    NameError: name 'admin' is not defined
    ```
*   **원인**: `main.py`에서 `admin` 라우터를 포함(`include_router`)하려 했으나, 상단 import 구문에 `admin`을 추가하지 않음.

---

## 3. 수정 내역 및 결과 코드

### `models.py` 수정
1.  **Import 추가**: `relationship`, `ForeignKey` 추가.
2.  **`UserAction` 테이블 관계 설정 명확화**:
    *   기존에는 `user_email`이 단순 문자열 컬럼이었으나, `relationship`을 맺기 위해 `ForeignKey("users.email")`로 변경. (User 테이블의 email이 PK는 아니지만 Unique Key이므로 참조 가능)
    *   하단에 흩어져 있던 `user = relationship(...)` 코드를 `UserAction` 클래스 내부로 이동.

#### [수정된 models.py 핵심 부분]
```python
from sqlalchemy import Column, Integer, Text, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship # [Fix] 추가됨
from database import Base

class User(Base):
    __tablename__ = "users"
    # ...
    email = Column(String, unique=True, index=True, nullable=False)
    # ...
    actions = relationship("UserAction", back_populates="user", cascade="all, delete")

class UserAction(Base):
    __tablename__ = "users_action"
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # [Fix] ForeignKey 설정하여 User 테이블과 연결
    # user_email = Column(String, ForeignKey("users.email"), nullable=False, index=True)
    # (주의: User 님이 직접 수정한 파일에서는 user_email을 유지하면서도 FK를 설정하려 했음)
    
    # ...
    
    # [Fix] 관계 설정 통합
    user = relationship("User", back_populates="actions")
```

### `main.py` 수정
1.  **Import 추가**: `from routers import ..., admin`

#### [수정된 main.py]
```python
from routers import landing, auth, about, main_page, all, mypage, admin # [Fix] admin 추가
```

---

## 4. 향후 체크리스트
*   [ ] `users_action` 테이블도 스키마가 변경되었으므로(Foreign Key 추가 등), 서버 재시작 시 에러가 난다면 테이블 초기화(DROP & Create)가 필요할 수 있음.
*   [ ] `routers/admin.py`에서 `UserAction`을 쿼리할 때 컬럼명이 모델과 일치하는지 확인.
    *   `timestamp` vs `created_at`
    *   `action_type` vs `type`
