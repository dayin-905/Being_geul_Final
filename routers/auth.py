import os
import traceback
from urllib.parse import urlencode, quote
from dotenv import load_dotenv

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from starlette.responses import RedirectResponse
import httpx

# 데이터베이스 관련 임포트 (사용자 환경에 맞게 유지)
from database import get_db
from models import User

# .env 파일 로드 (서버 실행 시 환경변수를 읽어옴)
load_dotenv()

router = APIRouter(prefix="/api/auth", tags=["auth"])

# ============================================================
# 1. 설정 및 보안
# ============================================================

# 비밀번호 암호화 (argon2가 설치되어 있다고 가정)
# 만약 에러나면 schemes=["bcrypt"] 로 변경하세요.
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Pydantic 모델
class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    region: str | None = None

class UserLogin(BaseModel):
    email: str
    password: str

# 환경 변수 가져오기 (없으면 에러가 아니라 빈 문자열 반환)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "")

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")
NAVER_REDIRECT_URI = os.getenv("NAVER_REDIRECT_URI", "")

# 프론트엔드 메인 주소 (로그인 성공 후 여기로 보냅니다)
FRONTEND_URL = "https://newsync.shop"

# ============================================================
# 2. 일반 회원가입 / 로그인 API
# ============================================================

@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # 중복 체크
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다.")
        
        # 비밀번호 해싱
        hashed_password = pwd_context.hash(user.password)
        
        # DB 저장
        new_user = User(
            email=user.email,
            password=hashed_password,
            name=user.name,
            region=user.region,
            provider="local"
        )
        db.add(new_user)
        db.commit()
        
        return {"message": "회원가입 성공", "email": new_user.email}

    except HTTPException:
        raise
    except Exception as e:
        error_msg = traceback.format_exc()
        with open("server_error.log", "w", encoding="utf-8") as f:
            f.write(error_msg)
        print(f"[ERROR] Signup Failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error")

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    
    if not db_user:
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 틀립니다.")
    
    if db_user.provider != "local":
        raise HTTPException(status_code=400, detail=f"{db_user.provider} 계정으로 로그인해주세요.")

    if not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 틀립니다.")
    
    return {
        "message": "로그인 성공",
        "user": {
            "email": db_user.email,
            "name": db_user.name,
            "region": db_user.region
        }
    }

@router.get("/verify")
def verify_session():
    return {"message": "Session is valid"}


# ============================================================
# 3. Google OAuth
# ============================================================

@router.get("/google/login")
def google_login():
    """구글 로그인 페이지로 리다이렉트"""
    if not GOOGLE_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="서버 설정 오류: GOOGLE_REDIRECT_URI가 없습니다.")

    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI, # 구글 콘솔과 일치해야 함 (api.newsync.shop)
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(url)

@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """구글 로그인 후 돌아오는 처리"""
    if not code:
        raise HTTPException(status_code=400, detail="Code not found")

    # 1. 토큰 교환
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": GOOGLE_REDIRECT_URI,
    }
    
    async with httpx.AsyncClient() as client:
        token_res = await client.post(token_url, data=data)
        if token_res.status_code != 200:
            print(f"[Google Error] {token_res.text}")
            raise HTTPException(status_code=400, detail="Google Login Failed (Token)")
        
        token_json = token_res.json()
        access_token = token_json.get("access_token")

        # 2. 유저 정보 조회
        user_info_res = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if user_info_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Google Login Failed (UserInfo)")
        user_info = user_info_res.json()

    # 3. DB 처리
    email = user_info.get("email")
    name = user_info.get("name")
    
    db_user = db.query(User).filter(User.email == email).first()
    
    if not db_user:
        new_user = User(
            email=email,
            name=name,
            provider="google",
            region="전국"
        )
        db.add(new_user)
        db.commit()
    
    # 4. 로그인 완료 페이지로 이동 (메인 도메인 사용)
    encoded_name = quote(name) if name else "Member"
    
    # [수정됨] https://newsync.shop/main.html 로 이동
    redirect_url = f"{FRONTEND_URL}/main.html?social_login=success&email={email}&name={encoded_name}&provider=google"
    
    return RedirectResponse(redirect_url)


# ============================================================
# 4. Naver OAuth
# ============================================================

@router.get("/naver/login")
def naver_login():
    """네이버 로그인 페이지로 리다이렉트"""
    if not NAVER_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="서버 설정 오류: NAVER_REDIRECT_URI가 없습니다.")

    state = "random_state_string_1234" 
    params = {
        "client_id": NAVER_CLIENT_ID,
        "redirect_uri": NAVER_REDIRECT_URI, # 네이버 콘솔과 일치해야 함 (api.newsync.shop)
        "response_type": "code",
        "state": state,
    }
    url = f"https://nid.naver.com/oauth2.0/authorize?{urlencode(params)}"
    return RedirectResponse(url)

@router.get("/naver/callback")
async def naver_callback(code: str, state: str, db: Session = Depends(get_db)):
    """네이버 로그인 후 돌아오는 처리"""
    if not code:
        raise HTTPException(status_code=400, detail="Code not found")

    # 1. 토큰 교환
    token_url = "https://nid.naver.com/oauth2.0/token"
    params = {
        "grant_type": "authorization_code",
        "client_id": NAVER_CLIENT_ID,
        "client_secret": NAVER_CLIENT_SECRET,
        "code": code,
        "state": state,
    }
    
    async with httpx.AsyncClient() as client:
        token_res = await client.get(token_url, params=params)
        if token_res.status_code != 200:
            print(f"[Naver Error] {token_res.text}")
            raise HTTPException(status_code=400, detail="Naver Login Failed (Token)")
        
        token_json = token_res.json()
        access_token = token_json.get("access_token")

        # 2. 유저 정보 조회
        user_info_res = await client.get(
            "https://openapi.naver.com/v1/nid/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if user_info_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Naver Login Failed (UserInfo)")
        
        user_info = user_info_res.json().get("response")

    # 3. DB 처리
    email = user_info.get("email")
    name = user_info.get("name")
    
    db_user = db.query(User).filter(User.email == email).first()
    
    if not db_user:
        new_user = User(
            email=email,
            name=name,
            provider="naver",
            region="전국"
        )
        db.add(new_user)
        db.commit()

    # 4. 로그인 완료 페이지로 이동 (메인 도메인 사용)
    encoded_name = quote(name) if name else "Member"

    # [수정됨] https://newsync.shop/main.html 로 이동
    redirect_url = f"{FRONTEND_URL}/main.html?social_login=success&email={email}&name={encoded_name}&provider=naver"
    
    return RedirectResponse(redirect_url)