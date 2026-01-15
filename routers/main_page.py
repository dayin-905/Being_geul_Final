from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from typing import Optional
import os
import random
import json  # [추가] JSON 변환을 위해 필요

from database import get_db
from models import Policy, categoryColorMap, get_image_for_category

router = APIRouter(tags=["main"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# [헬퍼 함수] 랜딩페이지 지역 ID를 DB 지역명으로 변환
def convert_region_id_to_db_name(region_id: str) -> Optional[str]:
    """
    랜딩페이지 지역 ID를 DB 지역명으로 변환
    예: 'detail_seoul' -> '서울', 'detail_chungnam' -> '충남'
    """
    region_id_to_db_name = {
        'detail_seoul': '서울',
        'detail_incheon': '인천',
        'detail_gyeonggi': '경기',
        'detail_daejun': '대전',
        'detail_saejong': '세종',
        'detail_chungnam': '충남',
        'detail_gwangju': '광주',
        'detail_jeonnam': '전남',
        'detail_daegu': '대구',
        'detail_gyeongbug': '경북',
        'detail_busan': '부산',
        'detail_ulsan': '울산',
        'detail_gyeongnam': '경남',
        'gangwon': '강원',
        'chungbug': '충북',
        'jeonbug': '전북',
        'jeju': '제주'
    }
    return region_id_to_db_name.get(region_id, None)

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
async def read_main(
    request: Request, 
    region: Optional[str] = None,  # URL 파라미터: 랜딩페이지에서 선택한 지역 ID
    exclude_ids: Optional[str] = None,  # 새로 추가: 쉼표로 구분된 ID 문자열
    db: Session = Depends(get_db)
):
    target_categories = ["취업", "창업", "주거", "금융", "교육", "복지"]
    all_picks = []
    
    # 지역 필터 설정: 선택한 지역 + 전국
    filter_regions = ['전국']  # 기본값: 전국만
    if region:
        db_region_name = convert_region_id_to_db_name(region)
        if db_region_name:
            filter_regions = [db_region_name, '전국']  # 선택 지역 + 전국
    
    # 제외할 ID 목록 파싱
    exclude_id_list = []
    if exclude_ids:
        try:
            exclude_id_list = [int(id.strip()) for id in exclude_ids.split(',') if id.strip()]
        except ValueError:
            exclude_id_list = []
    
    # 1. 카테고리별 랜덤 추출 (지역 필터 적용)
    for cat in target_categories:
        query = db.query(Policy)\
            .filter(Policy.genre.contains(cat))\
            .filter(Policy.region.in_(filter_regions))
        
        # 제외할 ID가 있으면 필터 추가
        if exclude_id_list:
            query = query.filter(~Policy.id.in_(exclude_id_list))
        
        policies = query\
            .order_by(func.random())\
            .limit(3)\
            .all()
        all_picks.extend(policies)

    # 2. 섞기
    random.shuffle(all_picks)
        
    # 3. 슬라이드용 데이터 (지역 필터 적용)
    slider_policies = db.query(Policy)\
        .filter(Policy.region.in_(filter_regions))\
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

@router.get("/api/main/more-cards")
async def get_more_cards(
    request: Request,
    region: Optional[str] = None,
    exclude_ids: Optional[str] = None,  # 쉼표로 구분된 ID 목록
    db: Session = Depends(get_db)
):
    """
    스와이프 카드 더보기 API
    기존 read_main과 동일한 로직으로 카테고리별 3개씩 총 18개 정책 반환
    exclude_ids가 있으면 해당 ID를 제외
    """
    target_categories = ["취업", "창업", "주거", "금융", "교육", "복지"]
    all_picks = []
    
    # 지역 필터 설정: 선택한 지역 + 전국
    filter_regions = ['전국']  # 기본값: 전국만
    if region:
        db_region_name = convert_region_id_to_db_name(region)
        if db_region_name:
            filter_regions = [db_region_name, '전국']  # 선택 지역 + 전국
    
    # 제외할 ID 목록 파싱
    exclude_id_list = []
    if exclude_ids:
        try:
            exclude_id_list = [int(id.strip()) for id in exclude_ids.split(',') if id.strip()]
        except ValueError:
            exclude_id_list = []
    
    # 1. 카테고리별 랜덤 추출 (지역 필터 및 제외 ID 적용)
    for cat in target_categories:
        query = db.query(Policy)\
            .filter(Policy.genre.contains(cat))\
            .filter(Policy.region.in_(filter_regions))
        
        # 제외할 ID가 있으면 필터 추가
        if exclude_id_list:
            query = query.filter(~Policy.id.in_(exclude_id_list))
        
        policies = query\
            .order_by(func.random())\
            .limit(3)\
            .all()
        all_picks.extend(policies)
    
    # 2. 섞기
    random.shuffle(all_picks)
    
    # 3. 직렬화
    cards_list = [serialize_policy(p) for p in all_picks]
    
    return {"cards": cards_list}