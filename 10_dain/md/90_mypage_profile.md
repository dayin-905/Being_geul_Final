
# 마이페이지 활동 지수 및 유동적 칭호 시스템 구현

## 1. 개요
마이페이지에 하드코딩되어 있던 프로필 정보와 활동 지수를 DB와 연동하여 실시간으로 표시하는 작업입니다. 사용자의 활동(찜하기) 비율에 따라 칭호가 자동으로 변경되는 시스템을 포함합니다.

---

## 2. 작업 상세 내용

### [완료] Step 1: Backend API 구현 (`routers/mypage.py`)
사용자 기본 정보(이름, 이메일, 지역)와 활동 지수를 계산하여 반환하는 API 엔드포인트를 구현했습니다.

### [완료] Step 2: Frontend 연동 (`static/script.js`)
API에서 받아온 데이터를 화면의 각 요소에 매핑하는 작업을 완료했습니다.

### [완료] Step 3: 실시간 연동 (Real-time Updates)
찜하기(Like) 또는 찜 취소(Unlike) 시 DB 변경 사항을 즉시 반영하여, 새로고침 없이도 활동 지수와 칭호가 변경되도록 구현합니다.

### [완료] Step 4: 프로필 캐릭터 선택 기능 구현
사용자가 프로필 사진 대신 **트렌디한 2030 인물 캐릭터 아이콘**을 선택할 수 있도록 기능을 구현했습니다.
초기에는 CSS Sprite 기법을 시도했으나 확대 시 화질 저하가 발생하여, **고화질 개별 PNG 파일(6종)**로 분할 저장하여 적용했습니다.

#### 1. DB Model 수정 (`models.py`)
`User` 테이블에 프로필 아이콘 식별자를 저장할 컬럼을 추가했습니다.
```python
class User(Base):
    # ...
    # [NEW] 프로필 아이콘 (avatar_1 ~ avatar_6)
    profile_icon = Column(String, default="avatar_1")
    # ...
```

#### 2. Backend API 구현 (`routers/mypage.py`)
프로필 아이콘 업데이트를 위한 스키마와 API 엔드포인트를 추가했습니다.
```python
class IconUpdate(BaseModel):
    user_email: str
    icon_name: str

# 5. 프로필 아이콘 변경
@router.put("/profile/icon")
def update_profile_icon(data: IconUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.profile_icon = data.icon_name
    db.commit()
    
    return {"message": "Profile icon updated", "icon": user.profile_icon}
```

#### 3. Frontend HTML 수정 (`templates/mypage.html`)
프로필 이미지를 `<img>` 태그로 유지하며, 캐릭터 선택 모달에서도 개별 이미지를 사용하도록 구현했습니다.
```html
<!-- 프로필 이미지 영역 -->
<img id="user-profile-img" src="/static/images/avatars/avatar_1.png" alt="Profile" ... >

<!-- Avatar Selection Modal -->
<div id="avatar-modal" class="...">
    <!-- ... 모달 내용 및 캐릭터 선택 버튼들 ... -->
    <button class="avatar-option ..." data-icon="avatar_1">
       <img src="/static/images/avatars/avatar_1.png" ...>
    </button>
    <!-- ... -->
</div>
```

#### 4. Frontend Script 수정 (`static/script.js`)
선택된 아이콘 이름에 따라 이미지 경로(`src`)를 업데이트하도록 구현했습니다.
```javascript
// 프로필 로드 시 아이콘 적용
const profileImg = document.getElementById('user-profile-img');
if (profileImg) {
    const iconName = data.profile_icon || "avatar_1";
    profileImg.src = `/static/images/avatars/${iconName}.png`;
}

// 모달 로직 (Open, Select, Save) 등의 이벤트 핸들러 구현 완료
```

---

## 3. 테스트 방법 (Testing Guide)

### 1단계: API 직접 호출 테스트
... (기존 내용) ...

### 2단계: 화면 확인
... (기존 내용) ...

### 3단계: 실시간 연동 테스트
... (기존 내용) ...

### 4단계: 프로필 변경 테스트 (New)
1. 마이페이지 프로필 사진 옆의 **연필 아이콘**을 클릭합니다.
2. "캐릭터 선택" 모달이 뜨는지 확인합니다.
3. 원하는 캐릭터(예: 부엉이)를 선택하고 "저장"을 누릅니다.
4. 프로필 이미지가 선택한 캐릭터로 즉시 변경되는지 확인합니다.
5. 페이지를 새로고침해도 변경된 캐릭터가 유지되는지 확인합니다.
#### 5. 트러블슈팅 (Troubleshooting) - [해결됨]
**문제 상황:**
`Step 4` 구현 후 API 호출 시 `500 Internal Server Error` 발생. 로그 확인 결과 `user.profile_icon` 컬럼이 없다는 DB 오류 확인.
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) column users.profile_icon does not exist
```

**원인 분석:**
첫 번째 마이그레이션 스크립트 실행 시 트랜잭션 커밋(`commit()`)이 명시적으로 호출되지 않아, 변경 사항이 실제 DB에 반영되지 않았던 것으로 추정됨.

**해결 방법:**
`connection.begin()`으로 명시적 트랜잭션을 시작하고 `trans.commit()`을 수행하는 개선된 마이그레이션 스크립트(`migrate_db_v2.py`)를 작성하여 실행함.

```python
# migrate_db_v2.py 핵심 로직
def migrate_force():
    with engine.connect() as connection:
        trans = connection.begin() # 트랜잭션 시작
        try:
            # ... 컬럼 추가 쿼리 실행 ...
            trans.commit() # ★ 중요: 명시적 커밋
            print("💾 Changes committed to DB.")
        except:
            trans.rollback()
```
실행 결과 `✅ Column added successfully.` 메시지와 함께 컬럼이 정상 추가되었으며, 이후 API가 정상 작동함.
