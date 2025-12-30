from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
import os
import random

from database import get_db
from models import Policy, categoryColorMap, get_image_for_category

router = APIRouter(tags=["main"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# [NEW] 커스텀 필터 등록: 템플릿에서 get_image_for_category 함수를 'filter' 처럼 쓰기 위함
templates.env.globals.update(get_policy_image=get_image_for_category) 

@router.get("/main.html")
async def read_main(request: Request, db: Session = Depends(get_db)):
    # 1. 6개 주요 카테고리 정의
    target_categories = ["취업", "창업", "주거", "금융", "교육", "복지"]
    
    all_picks = []
    
    # 2. 각 카테고리별로 랜덤 3개씩 추출
    #    (DB에 데이터가 부족할 경우 있는 만큼만 가져옴)
    for cat in target_categories:
        policies = db.query(Policy)\
            .filter(Policy.genre.contains(cat))\
            .order_by(func.random())\
            .limit(3)\
            .all()
        all_picks.extend(policies)

    # 3. 전체 리스트를 무작위로 섞음 (누락된 로직 복구)
    random.shuffle(all_picks)
        
    # [NEW] 슬라이드용 추가 데이터 (랜덤하게 20개 정도)
    slider_policies = db.query(Policy)\
        .order_by(func.random())\
        .limit(20)\
        .all()
    
    # 4. 템플릿 렌더링 시 데이터 전달
    return templates.TemplateResponse("main.html", {
        "request": request,
        "policies": all_picks, # 틴더용
        "slider_policies": slider_policies, # [NEW] 슬라이드용
        "categoryColorMap": categoryColorMap
    })