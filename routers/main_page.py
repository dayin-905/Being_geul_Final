from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
import os
import random
import json  # [추가] JSON 변환을 위해 필요

from database import get_db
from models import Policy, categoryColorMap, get_image_for_category

router = APIRouter(tags=["main"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# [헬퍼 함수] SQLAlchemy 객체를 안전한 Dict로 변환
def serialize_policy(policy):
    return {
        "id": policy.id,
        "title": policy.title,
        # 내용이 없으면 빈 문자열, 줄바꿈은 공백으로 치환 (안전장치)
        "summary": (policy.summary or "").replace("\n", " ").replace("\r", ""), 
        "genre": policy.genre,
        "period": policy.period or "상시 모집",
        "image": get_image_for_category(policy.genre), # 여기서 이미지 결정
        "link": policy.link or "",
        "region": policy.region or "전국",
        "colorCode": categoryColorMap.get((policy.genre or "")[:2], '#777777')
    }

@router.get("/main.html")
async def read_main(request: Request, db: Session = Depends(get_db)):
    target_categories = ["취업", "창업", "주거", "금융", "교육", "복지"]
    all_picks = []
    
    # 1. 카테고리별 랜덤 추출
    for cat in target_categories:
        policies = db.query(Policy)\
            .filter(Policy.genre.contains(cat))\
            .order_by(func.random())\
            .limit(3)\
            .all()
        all_picks.extend(policies)

    # 2. 섞기
    random.shuffle(all_picks)
        
    # 3. 슬라이드용 데이터
    slider_policies = db.query(Policy)\
        .order_by(func.random())\
        .limit(20)\
        .all()
    
    # [핵심 수정] 객체를 Dict 리스트로 변환 (직렬화)
    tinder_data_list = [serialize_policy(p) for p in all_picks]
    slider_data_list = [serialize_policy(p) for p in slider_policies]

    # 4. 템플릿 렌더링 (데이터를 JSON 그대로 넘김)
    return templates.TemplateResponse("main.html", {
        "request": request,
        # [중요] 여기서 Python 리스트를 그대로 넘깁니다. 
        # HTML에서 tojson 필터를 쓰면 안전하게 변환됩니다.
        "tinder_data_list": tinder_data_list,
        "slider_data_list": slider_data_list
    })