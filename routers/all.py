import os
import random
from typing import Optional
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import SessionLocal
from models import Policy, get_image_for_category

# 라우터 생성
router = APIRouter()

# 템플릿 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# DB 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== [유틸리티 및 매핑] ====================

# 카테고리 색상 매핑
categoryColorMap = {
    "주거": "#F48245", "주거/자립": "#F48245",
    "취업": "#4A9EA8", "취업/직무": "#4A9EA8",
    "금융": "#D9B36C", "금융/생활비": "#D9B36C",
    "복지": "#9F7AEA", "복지/문화": "#9F7AEA",
    "창업": "#FF5A5F", "창업/사업": "#FF5A5F",
    "교육": "#4299E1", "교육/자격증": "#4299E1"
}

# 프론트엔드 카테고리 -> 데이터베이스 genre 매핑
FRONT_TO_DB_CATEGORY = {
    "취업": "취업/직무",
    "주거": "주거/자립",
    "금융": "금융/생활비",
    "창업": "창업/사업",
    "복지": "복지/문화",
    "교육": "교육/자격증"
}

# 프론트엔드 지역 ID (SVG) -> DB 저장용 한글 명칭
FRONT_TO_DB_REGION = {
    'national': '전국',
    'detail_seoul': '서울', 'detail_gyeonggi': '경기', 'detail_incheon': '인천',
    'gangwon': '강원', 'chungbug': '충북', 'chungnam': '충남', 'detail_chungnam': '충남',
    'jeonbug': '전북', 'jeonnam': '전남', 'detail_jeonnam': '전남',
    'gyeongbug': '경북', 'detail_gyeongbug': '경북',
    'gyeongnam': '경남', 'detail_gyeongnam': '경남',
    'jeju': '제주',
    'detail_busan': '부산', 'detail_daegu': '대구', 'detail_daejun': '대전',
    'detail_gwangju': '광주', 'detail_ulsan': '울산', 'detail_saejong': '세종'
}

def normalize_region_name(input_str: str) -> str:
    """
    JSON 파일 로딩 시 '전라남도' -> '전남' 등으로 변환.
    프론트에서 오는 ID ('detail_seoul')도 '서울'로 변환.
    """
    if not input_str:
        return "전국"
    
    # 1. 프론트 ID인 경우 매핑 테이블 사용
    if input_str in FRONT_TO_DB_REGION:
        return FRONT_TO_DB_REGION[input_str]
        
    # 2. 한글 긴 이름인 경우 (앞 2글자로 축약)
    if len(input_str) >= 2:
        return input_str[:2]
        
    return input_str



# ==================== [라우터 엔드포인트] ====================

# 전체 정책 페이지 렌더링
@router.get("/all.html", response_class=HTMLResponse)
async def read_all_policies(request: Request):
    return templates.TemplateResponse("all.html", {"request": request})

# 정책 카드 데이터 조회 API (전체보기 페이지용)
@router.get("/api/cards")
async def api_get_cards(
    region: Optional[str] = None,  # 지역 필터
    category: Optional[str] = None,  # 카테고리 필터
    keyword: Optional[str] = None,  # 검색 키워드
    sort: Optional[str] = None,  # 정렬: 'latest', 'popular', 'deadline'
    db: Session = Depends(get_db)
):
    """
    전체보기(All) 페이지용 API
    category 또는 keyword로 검색, sort로 정렬, region으로 지역 필터링
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
    
    # 카테고리 필터링
    if category and category != 'all':
        # 프론트엔드 카테고리를 DB genre 값으로 매핑
        db_category = FRONT_TO_DB_CATEGORY.get(category, category)
        # 정확한 매칭으로 필터링
        query = query.filter(Policy.genre == db_category)
        print(f"🔍 카테고리 필터링: '{category}' -> '{db_category}'")
    
    # 키워드 검색
    if keyword:
        search_pattern = f"%{keyword}%"
        query = query.filter(or_(
            Policy.title.like(search_pattern),
            Policy.summary.like(search_pattern)
        ))
        print(f"🔎 키워드 검색: '{keyword}'")
    
    # 정렬 기능 - [수정] 모든 정렬 기준에 '모집 중(is_active=True)' 우선 적용
    if sort == 'latest':
        # 최신순: 모집중 우선 -> 생성일 내림차순
        query = query.order_by(Policy.is_active.desc(), Policy.created_at.desc().nulls_last())
        print(f"📅 정렬: 최신순 (Active First -> created_at DESC)")
    elif sort == 'popular':
        # 인기순: 모집중 우선 -> 조회수 내림차순
        query = query.order_by(Policy.is_active.desc(), Policy.view_count.desc().nulls_last())
        print(f"🔥 정렬: 인기순 (Active First -> view_count DESC)")
    elif sort == 'deadline':
        # 마감순: 모집중 우선 -> 마감 임박순 (end_date 오름차순)
        query = query.order_by(Policy.is_active.desc(), Policy.end_date.asc().nulls_last())
        print(f"⏰ 정렬: 마감순 (Active First -> end_date ASC)")
    elif sort == 'closed':
        # [NEW] 마감 정책 탭: 마감된 정책(is_active=False)만 모아보기
        # 마감된 정책만 필터링 후, 최신 마감일 순(최근에 끝난 것부터)으로 정렬
        query = query.filter(Policy.is_active == False).order_by(Policy.end_date.desc().nulls_last())
        print(f"🚫 정렬: 마감 정책 (is_active=False Only -> end_date DESC)")
    else:
        # 기본 정렬: 모집중 우선 -> ID 오름차순
        query = query.order_by(Policy.is_active.desc(), Policy.id.asc())
        print(f"📋 정렬: 기본 (Active First -> id ASC)")
    
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
            "colorCode": categoryColorMap.get(p.genre or "", "#777777"),
            "is_active": p.is_active  # [NEW] 프론트엔드에서 마감 배지 표시 등에 사용
        })
    
    return result
