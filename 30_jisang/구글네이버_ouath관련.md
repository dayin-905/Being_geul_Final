# 프로젝트 업데이트 리포트 (For PM)

본 문서는 **구글/네이버 OAuth 연동** 작업 완료에 따른 변경 사항 및 전달 파일 목록입니다.

---

## 1. 전달 파일 목록

| 파일 경로 | 파일명 | 상태 | 구분 | 비고 |
| :--- | :--- | :--- | :--- | :--- |
| `/apps/db_main_project/` | **.env** | **New** | 전체 전달 | **[중요]** 보안 키 포함. 서버에 배포 시 필수 생성. |
| `/apps/db_main_project/routers/` | **auth.py** | **Modified** | 부분 수정 | 소셜 로그인 API 로직 추가 |
| `/apps/db_main_project/static/` | **script.js** | **Modified** | 부분 수정 | 소셜 로그인 UI 연동 스크립트 추가 |
| `/root/.gemini/antigravity/brain/...` | **oauth_setup_guide.md** | **New** | 참고 자료 | 키 발급 및 설정 방법 가이드 |

---

## 2. 상세 변경 내역

### 1) .env (신규)
> **이 파일은 전체가 새로 생성되었습니다.**
> 서버 구동을 위해 아래 템플릿에 맞게 실제 키 값을 넣어주셔야 합니다.

```properties
# Google OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Naver OAuth
NAVER_CLIENT_ID=...
NAVER_CLIENT_SECRET=...
NAVER_REDIRECT_URI=http://localhost:8000/api/auth/naver/callback

# JWT Secret
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 2) routers/auth.py (수정)
> 기존 파일 하단에 아래 내용이 **추가**되었습니다. (Import 구문은 상단에 추가)

**Imports 추가:**
```python
import os
import httpx
from urllib.parse import urlencode
from dotenv import load_dotenv
from starlette.responses import RedirectResponse

load_dotenv()
```

**OAuth 환경 변수 및 엔드포인트 로직 추가:**
```python
# ============================================================
# [OAuth 설정] 환경 변수 로드
# ============================================================
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
# ... (중략: 네이버 설정 포함)

# ============================================================
# [Google OAuth] Login & Callback
# ============================================================
@router.get("/google/login")
def google_login():
    # ... 구글 로그인 페이지 리다이렉트 로직

@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    # ... 토큰 교환, 유저 정보 조회, 회원가입/로그인 처리, 메인 리다이렉트

# ============================================================
# [Naver OAuth] Login & Callback
# ============================================================
@router.get("/naver/login")
def naver_login():
    # ... 네이버 로그인 페이지 리다이렉트 로직

@router.get("/naver/callback")
async def naver_callback(code: str, state: str, db: Session = Depends(get_db)):
    # ... 유사한 네이버 처리 로직
```

### 3) static/script.js (수정)
> 아래 두 부분이 **추가/수정**되었습니다.

**[추가] 소셜 로그인 트리거 함수:**
```javascript
// [NEW] Social Login Trigger (Global)
window.socialLogin = function(provider) {
    if (!['google', 'naver'].includes(provider)) return;
    window.location.href = `/api/auth/${provider}/login`;
};
```

**[수정] `checkLoginState` 함수 도입부:**
```javascript
async function checkLoginState() {
    // [NEW] 0. OAuth 리다이렉트 복귀 처리
    const urlParams = new URLSearchParams(window.location.search);
    const socialLogin = urlParams.get('social_login'); // success
    
    if (socialLogin === 'success') {
        // ... (파라미터에서 정보 추출 및 localStorage 저장) ...
        
        alert(`${name}님, 소셜 로그인 성공! 환영합니다.`);
        
        // [NEW] 메인 페이지로 이동
        window.location.href = '/main.html';
    }
    
    // ... (기존 검증 로직 등) ...
}
```
