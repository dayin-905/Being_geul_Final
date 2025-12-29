"""
전체 정책 보기 페이지 (all.html) 관련 라우터
"""
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import os

from database import get_db
from models import (
    Policy, 
    FRONT_TO_DB_CATEGORY, categoryColorMap, 
    normalize_region_name, get_image_for_category
)

router = APIRouter(tags=["all"])

# 템플릿 디렉토리 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=template_dir)

@router.get("/api/cards")
async def api_get_cards(
    region: Optional[str] = None,  # 지역 필터 (전체보기 페이지용)
    user_id: Optional[str] = None,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    sort: Optional[str] = None,  # 'latest', 'popular', 'deadline', None
    db: Session = Depends(get_db)
):
    """
    전체보기 페이지용 정책 카드 데이터 조회
    category 또는 keyword로 검색, sort로 정렬
    """
    query = db.query(Policy)
    
    # 지역 필터링 (전체보기 페이지용)
    if region and region != 'national' and region != '전체':
        if region == '전국':
            # 전국 선택 시: region="전국"인 정책만 필터링
            query = query.filter(Policy.region == '전국')
            print(f"🗺️ 지역 필터링: 전국 (region='전국'인 정책만)")
        else:
            # 특정 지역 선택 시: 해당 지역의 정책만 필터링
            norm_region = normalize_region_name(region)
            query = query.filter(Policy.region == norm_region)
            print(f"🗺️ 지역 필터링: '{region}' -> '{norm_region}'")
    else:
        # 전체 선택 시: 필터링 없음 (모든 지역 포함)
        print(f"🗺️ 지역 필터링: 전체 (필터링 없음)")
    
    if category and category != 'all':
        # 프론트엔드 카테고리를 DB genre 값으로 매핑
        db_category = FRONT_TO_DB_CATEGORY.get(category, category)
        # 정확한 매칭으로 필터링
        query = query.filter(Policy.genre == db_category)
        print(f"🔍 카테고리 필터링: '{category}' -> '{db_category}'")
    
    if keyword:
        search_pattern = f"%{keyword}%"
        query = query.filter(or_(
            Policy.title.like(search_pattern),
            Policy.summary.like(search_pattern)
        ))
    
    # 정렬 기능
    if sort == 'latest':
        # 최신순: created_at 내림차순 (NULL은 마지막)
        query = query.order_by(Policy.created_at.desc().nulls_last())
        print(f"📅 정렬: 최신순 (created_at DESC)")
    elif sort == 'popular':
        # 인기순: view_count 내림차순 (NULL은 마지막)
        query = query.order_by(Policy.view_count.desc().nulls_last())
        print(f"🔥 정렬: 인기순 (view_count DESC)")
    elif sort == 'deadline':
        # 마감순: end_date 오름차순 (NULL은 마지막)
        query = query.order_by(Policy.end_date.asc().nulls_last())
        print(f"⏰ 정렬: 마감순 (end_date ASC)")
    else:
        # 기본 정렬: id 오름차순
        query = query.order_by(Policy.id.asc())
        print(f"📋 정렬: 기본 (id ASC)")
        
    # 전체보기 페이지에서는 모든 데이터를 가져옴
    policies = query.all()

    # JSON 응답 포맷 (프론트엔드와 호환)
    result = []
    for p in policies:
        # 날짜 포맷팅
        date_str = "상시 모집"
        try:
            if p.end_date:
                # end_date가 있으면 마감일 표시
                if isinstance(p.end_date, str):
                    date_str = f"{p.end_date} 마감"
                else:
                    date_str = f"{p.end_date.strftime('%Y.%m.%d')} 마감"
            elif p.period:
                date_str = p.period
        except Exception as e:
            # 날짜 포맷팅 오류 시 period 사용
            date_str = p.period or "상시 모집"
        
        result.append({
            "id": p.id,
            "title": p.title or "",
            "desc": p.summary or "상세 내용을 확인하세요.",
            "category": p.genre or "기타",
            "date": date_str,
            "image": get_image_for_category(p.genre),  # 랜덤 이미지 할당
            "link": p.link or "#",
            "region": p.region or "전국",
            "colorCode": categoryColorMap.get(p.genre or "", "#777777")
        })
        
    return result
