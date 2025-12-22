from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os  # [추가] 운영체제 경로 모듈

app = FastAPI()

# --- [핵심 수정] 절대 경로 계산 ---
# 현재 파일(main.py)이 있는 폴더의 절대 경로를 구합니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. 정적 파일 연결 (절대 경로 사용)
# "static" 폴더가 main.py와 같은 위치에 있다고 가정
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# 2. HTML 템플릿 연결 (절대 경로 사용)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# --- 페이지 접속 경로 설정 (기존과 동일) ---

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/main.html")
async def read_main(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

@app.get("/mypage.html")
async def read_mypage(request: Request):
    return templates.TemplateResponse("mypage.html", {"request": request})

@app.get("/about.html")
async def read_about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/all.html")
async def read_all_policies(request: Request):
    return templates.TemplateResponse("all.html", {"request": request})