from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from database import get_db
from models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

# 1. 비밀번호 암호화 도구 설정
# 기존 bcrypt 부분을 지우거나 주석 처리하고 아래처럼 바꾸세요
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# 2. 데이터 검증용 스키마 (Pydantic)
class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    region: str | None = None # 선택사항

class UserLogin(BaseModel):
    email: str
    password: str

# 3. [회원가입 API]
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # 이미 가입된 이메일인지 확인
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다.")
    
    # 비밀번호 암호화 (보안 필수!)
    hashed_password = pwd_context.hash(user.password)
    
    # DB 저장
    new_user = User(
        email=user.email,
        password=hashed_password,
        name=user.name,
        region=user.region,
        provider="local"  # 직접 가입이므로 local
    )
    db.add(new_user)
    db.commit()
    
    return {"message": "회원가입 성공", "email": new_user.email}

# 4. [로그인 API]
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # 이메일로 사용자 찾기
    db_user = db.query(User).filter(User.email == user.email).first()
    
    if not db_user:
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 틀립니다.")
    
    # 소셜 로그인 사용자인지 체크
    if db_user.provider != "local":
        raise HTTPException(status_code=400, detail=f"{db_user.provider} 계정으로 로그인해주세요.")

    # 비밀번호 확인 (암호화된 것끼리 비교)
    if not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 틀립니다.")
    
    # 로그인 성공! (실무에선 여기서 토큰을 발급하지만, 일단 성공 메시지와 유저 정보 반환)
    return {
        "message": "로그인 성공",
        "user": {
            "email": db_user.email,
            "name": db_user.name,
            "region": db_user.region
        }
    }

# ============================================================
# [OAuth 설정] 환경 변수 로드 및 설정
# ============================================================
import os
import httpx
from urllib.parse import urlencode
from dotenv import load_dotenv
from starlette.responses import RedirectResponse

load_dotenv()

# Google Config
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# Naver Config
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NAVER_REDIRECT_URI = os.getenv("NAVER_REDIRECT_URI")

# ============================================================
# [Google OAuth]
# ============================================================
@router.get("/google/login")
def google_login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(url)

@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
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
            raise HTTPException(status_code=400, detail="Google Login Failed (Token)")
        token_json = token_res.json()
        access_token = token_json.get("access_token")

        # 2. 사용자 정보 가져오기
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
    
    # 이미 존재하는 사용자인지 확인
    db_user = db.query(User).filter(User.email == email).first()
    
    if not db_user:
        # 신규 가입
        new_user = User(
            email=email,
            name=name,
            provider="google",
            region="전국" # 기본값
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        # return {"message": "구글 회원가입 성공", "user": email} # for debug
    else:
        # 기존 유저 -> provider가 다르면 에러? 일단 pass
        pass
    
    # 4. 프론트엔드로 리다이렉트 (로그인 성공 처리)
    # 쿼리 파라미터에 정보를 담아 보냅니다. (보안상 좋진 않지만 MVP용)
    redirect_url = f"/?social_login=success&email={email}&name={name}&provider=google"
    return RedirectResponse(redirect_url)

# ============================================================
# [Naver OAuth]
# ============================================================
@router.get("/naver/login")
def naver_login():
    state = "random_state_string" # 보안을 위해 랜덤 생성 권장
    params = {
        "client_id": NAVER_CLIENT_ID,
        "redirect_uri": NAVER_REDIRECT_URI,
        "response_type": "code",
        "state": state,
    }
    url = f"https://nid.naver.com/oauth2.0/authorize?{urlencode(params)}"
    return RedirectResponse(url)

@router.get("/naver/callback")
async def naver_callback(code: str, state: str, db: Session = Depends(get_db)):
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
        token_res = await client.get(token_url, params=params) # 네이버는 GET 권장? 문서마다 다름, 보통 GET/POST 둘다 됨
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Naver Login Failed (Token)")
        token_json = token_res.json()
        access_token = token_json.get("access_token")

        # 2. 사용자 정보 가져오기
        user_info_res = await client.get(
            "https://openapi.naver.com/v1/nid/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if user_info_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Naver Login Failed (UserInfo)")
        user_info = user_info_res.json().get("response") # 네이버는 response 키 안에 있음

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
    
    # 4. 프론트엔드로 리다이렉트
    redirect_url = f"/?social_login=success&email={email}&name={name}&provider=naver"
    return RedirectResponse(redirect_url)