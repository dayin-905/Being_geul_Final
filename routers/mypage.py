from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime, date, timedelta
from database import get_db
from models import UserAction, Policy, User, categoryColorMap, get_image_for_category, FRONT_TO_DB_CATEGORY, normalize_region_name

# 라우터 설정 (태그 및 프리픽스 설정)
router = APIRouter(prefix="/api/mypage", tags=["mypage"])

# ==================== [Pydantic 스키마] ====================

class ActionCreate(BaseModel):
    user_email: str
    policy_id: int
    type: str  # 'like', 'pass' 등

class PolicyDto(BaseModel):
    id: int
    title: str
    desc: str
    category: str
    date: str
    image: str
    link: str
    region: str
    colorCode: str

class StatsDto(BaseModel):
    labels: List[str]
    data: List[int]

# ==================== [MBTI 데이터 정의] ====================
MBTI_DEFINITIONS = {
    # A. 1순위: 취업 (JOB)
    ("취업", "금융"): {
        "type_name": "연봉 협상의 달인",
        "subtitle": "나의 가치는 통장 잔고로 증명한다.",
        "tags": ["#몸값올리기", "#재테크", "#현실주의"],
        "desc": "직무 전문성을 키워 고액 연봉을 달성하고, 자산을 불리는 데 관심이 많음."
    },
    ("취업", "주거"): {
        "type_name": "워라밸 밸런서",
        "subtitle": "회사는 강남, 집은 역세권.",
        "tags": ["#칼퇴기원", "#직주근접", "#안정추구"],
        "desc": "안정적인 직장 생활을 위해 출퇴근 거리와 주거 환경을 최우선으로 고려함."
    },
    ("취업", "교육"): {
        "type_name": "무한 성장 프로",
        "subtitle": "배움에는 끝이 없다.",
        "tags": ["#자격증수집", "#자기개발", "#스펙업"],
        "desc": "끊임없이 자격증을 따고 공부하며 자신의 커리어 경쟁력을 높이는 성장형 인재."
    },
    # B. 1순위: 창업 (STARTUP)
    ("창업", "금융"): {
        "type_name": "유니콘 꿈나무",
        "subtitle": "내 사업의 끝은 엑시트!",
        "tags": ["#투자유치", "#지원금사냥", "#사업확장"],
        "desc": "사업 아이템을 실현하기 위한 자금 조달과 투자 유치, 정부 지원금에 능통함."
    },
    ("창업", "복지"): {
        "type_name": "낭만 혁명가",
        "subtitle": "세상을 바꾸되, 지치진 않을래.",
        "tags": ["#소셜벤처", "#심리안정", "#지속가능성"],
        "desc": "사회적 가치를 창출하는 창업을 꿈꾸며, 번아웃 방지와 멘탈 케어도 중요시함."
    },
    ("창업", "기타"): {
         "type_name": "불도저 개척자",
        "subtitle": "길이 없으면 만들면 되지.",
        "tags": ["#도전정신", "#무한동력", "#열정만수르"],
        "desc": "실패를 두려워하지 않고 자신의 비전을 향해 무모할 정도로 돌진하는 스타일."
    },
    # C. 1순위: 주거 (HOUSING)
    ("주거", "금융"): {
        "type_name": "스마트 건축가",
        "subtitle": "내 집 마련 로드맵 완비.",
        "tags": ["#청약당첨", "#영끌금지", "#부동산눈"],
        "desc": "주거 안정을 기반으로 부동산 투자나 자산 증식에 대해 구체적인 계획을 세움."
    },
    ("주거", "복지"): {
         "type_name": "프로 집콕러",
        "subtitle": "집 밖은 위험해!",
        "tags": ["#집순이", "#주거안정", "#월세지원"],
        "desc": "집에서의 안락한 생활을 최우선으로 하며, 월세/보증금 지원 등 주거 복지에 민감함."
    },
    ("주거", "취업"): {
        "type_name": "독립 만세형",
        "subtitle": "독립해야 진짜 어른.",
        "tags": ["#1인가구", "#자취꿀팁", "#생존본능"],
        "desc": "부모님 품을 떠나 온전한 경제적/공간적 자립을 이루는 것을 목표로 함."
    },
    # D. 1순위: 금융 (FINANCE)
    ("금융", "창업"): {
        "type_name": "시드머니 사냥꾼",
        "subtitle": "돈이 돈을 번다.",
        "tags": ["#투자왕", "#시드머니", "#경제관념"],
        "desc": "창업이나 투자를 위한 종잣돈(Seed Money) 모으기에 집중하며 금융 지식이 높음."
    },
    ("금융", "교육"): {
         "type_name": "가성비 브레인",
        "subtitle": "최소 비용, 최대 효과.",
        "tags": ["#국비지원", "#환급반", "#알뜰살뜰"],
        "desc": "내 돈 들이지 않고 국비 지원 등을 통해 역량을 개발하는 효율적인 소비 패턴을 가짐."
    },
    ("금융", "복지"): {
        "type_name": "알뜰살뜰 살림꾼",
        "subtitle": "티끌 모아 태산.",
        "tags": ["#포인트적립", "#혜택수집", "#생활비방어"],
        "desc": "소소한 생활비 지원이나 문화 혜택 등을 빠짐없이 챙겨 생활비를 아끼는 스마트 컨슈머."
    },
    # E. 1순위: 교육(EDU) or 복지(WELFARE)
    ("교육", "취업"): {
        "type_name": "잡학다식 지식인",
        "subtitle": "아는 것이 힘이다.",
        "tags": ["#평생학습", "#취미부자", "#박학다식"],
        "desc": "취업 스펙뿐만 아니라 인문학, 교양 등 다양한 분야를 배우는 것을 즐김."
    },
    ("교육", "창업"): {
        "type_name": "아이디어 뱅크",
        "subtitle": "배워서 남 주나? 내 거 하자!",
        "tags": ["#창의력대장", "#지식창업", "#메이커"],
        "desc": "교육을 통해 얻은 인사이트를 바탕으로 자신만의 서비스나 제품을 만들고 싶어 함."
    },
    ("복지", "주거"): {
         "type_name": "소확행 수집가",
        "subtitle": "오늘의 행복이 가장 중요해.",
        "tags": ["#마음건강", "#문화생활", "#행복추구"],
        "desc": "마음의 안정과 쾌적한 공간에서의 휴식을 중요시하며 삶의 질을 최우선으로 둠."
    },
    ("복지", "기타"): {
        "type_name": "욜로(YOLO) 드리머",
        "subtitle": "인생은 한 번뿐!",
        "tags": ["#문화누리", "#여행지원", "#스트레스제로"],
        "desc": "힘든 경쟁보다는 현재 누릴 수 있는 문화 혜택과 여행, 휴식을 통해 에너지를 얻음."
    }
}

def calculate_mbti_result(user_email: str, db: Session):
    # 1. 유저의 Like 데이터 조회
    acciones = db.query(Policy.genre)\
        .join(UserAction, UserAction.policy_id == Policy.id)\
        .filter(UserAction.user_email == user_email, UserAction.type == 'like')\
        .all()
    
    if not acciones:
        return None 
        
    # 2. 점수 집계
    scores = {}
    base_categories = ["취업", "창업", "주거", "금융", "교육", "복지"]
    for cat in base_categories:
        scores[cat] = 0
        
    for (genre,) in acciones:
        if not genre: continue
        key = "기타"
        if "취업" in genre: key = "취업"
        elif "창업" in genre: key = "창업"
        elif "주거" in genre: key = "주거"
        elif "금융" in genre: key = "금융"
        elif "교육" in genre: key = "교육"
        elif "복지" in genre: key = "복지"
        
        if key in scores:
            scores[key] += 1
            
    # 3. 정렬 및 매핑
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary = sorted_scores[0][0]
    secondary = sorted_scores[1][0]
    
    if sorted_scores[0][1] == 0:
        return None

    result = MBTI_DEFINITIONS.get((primary, secondary))
    
    if not result:
        # Fallback 로직
        if primary == "창업": result = MBTI_DEFINITIONS.get(("창업", "기타"))
        elif primary == "복지": result = MBTI_DEFINITIONS.get(("복지", "기타"))
        elif primary == "교육": result = MBTI_DEFINITIONS.get(("교육", "취업"))
        elif primary == "취업": result = MBTI_DEFINITIONS.get(("취업", "금융"))
        elif primary == "주거": result = MBTI_DEFINITIONS.get(("주거", "금융"))
        elif primary == "금융": result = MBTI_DEFINITIONS.get(("금융", "복지"))
        else: result = MBTI_DEFINITIONS.get(("복지", "기타"))
    
    # [NEW] 이미지 매핑을 위한 영문 카테고리 코드 추가
    # static/images/card_images/{code}_{1~5}.webp 형식 사용
    cat_code_map = {
        "취업": "job",
        "창업": "startup",
        "주거": "housing",
        "금융": "finance",
        "교육": "growth", # 파일명은 growth 사용
        "복지": "welfare"
    }
    # 1순위 기준 매핑, 없으면 welfare
    result["category_code"] = cat_code_map.get(primary, "welfare")
        
    return result

class IconUpdate(BaseModel):
    user_email: str
    icon_name: str

class LikeDeleteRequest(BaseModel):
    user_email: str
    policy_ids: List[int]

# ==================== [API 엔드포인트] ====================

# 4. 사용자 프로필 및 활동 지수 조회 (우선 배치)
@router.get("/profile")
def get_user_profile(user_email: str, db: Session = Depends(get_db)):
    """
    사용자 기본 정보(이름, 이메일, 지역)와 활동 지수(레벨, 뱃지)를 반환합니다.
    """
    # 1. 유저 정보 조회
    user = db.query(User).filter(User.email == user_email).first()
    
    if not user:
        # 유저가 없으면 에러보다는 기본값 반환 (로그인 세션 문제일 수 있음)
        return {"error": "User not found", "name": "알 수 없음", "region": "지역 미설정"}

    # 2. 활동 지수 계산 분모: 해당 지역 정책 개수
    user_region = user.region or "전국"
    search_region = normalize_region_name(user_region)
    
    # 지역 정책 개수
    if search_region == "전국":
        total_policies = db.query(Policy).count()
    else:
        from sqlalchemy import or_
        total_policies = db.query(Policy).filter(
            or_(Policy.region.like(f"%{search_region}%"), Policy.region == "전국")
        ).count()
        
    if total_policies == 0:
        total_policies = 1

    # 3. 활동 지수 계산 분자: 내가 찜한 활동 개수
    like_count = db.query(UserAction).filter(
        UserAction.user_email == user_email, 
        UserAction.type == 'like'
    ).count()

    # 4. 퍼센트 계산
    percentage = int((like_count / total_policies) * 100)
    
    # 5. 레벨 및 칭호 부여
    level_badge = "#정책_기웃러 👀"
    if percentage >= 100:
        level_badge = "#정책_오지라퍼 🗣️📢"
    elif percentage >= 61:
        level_badge = "#인간_정책백과 📖"
    elif percentage >= 31:
        level_badge = "#지원금_사냥꾼 🏹"
    elif percentage >= 11:
        level_badge = "#혜택_줍줍러 🍬"

    # [NEW] 마감 임박 (D-7) 개수 계산
    today = date.today()
    deadline = today + timedelta(days=7)
    
    closing_soon_count = db.query(UserAction)\
        .join(Policy, UserAction.policy_id == Policy.id)\
        .filter(
            UserAction.user_email == user_email,
            UserAction.type == 'like',
            Policy.end_date >= today,
            Policy.end_date <= deadline
        ).count()
        
    return {
        "name": user.name,
        "email": user.email,
        "region": user_region,
        "region_badge": f"#{user_region}",
        "activity_index": percentage,
        "level_badge": level_badge,
        "like_count": like_count,
        "apply_count": 0,
        "closing_soon_count": closing_soon_count, # [NEW]
        "profile_icon": user.profile_icon or "avatar_1",
        "mbti": calculate_mbti_result(user_email, db)
    }

# 5. 프로필 아이콘 변경
@router.put("/profile/icon")
def update_profile_icon(data: IconUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.profile_icon = data.icon_name
    db.commit()
    
    return {"message": "Profile icon updated", "icon": user.profile_icon}

# 1. 사용자 액션 저장 (좋아요/패스/좋아요 취소)
@router.post("/action")
def save_user_action(action: ActionCreate, db: Session = Depends(get_db)):
    """
    사용자의 스와이프 액션(like/pass) 또는 모달 찜하기(like/unlike)를 처리합니다.
    """
    # 1. 좋아요 취소 (unlike) 처리
    if action.type == 'unlike':
        db.query(UserAction).filter(
            UserAction.user_email == action.user_email,
            UserAction.policy_id == action.policy_id,
            UserAction.type == 'like'
        ).delete()
        db.commit()
        return {"message": "Like removed"}

    # 2. 좋아요 (like) 중복 방지 처리
    if action.type == 'like':
        existing = db.query(UserAction).filter(
            UserAction.user_email == action.user_email,
            UserAction.policy_id == action.policy_id,
            UserAction.type == 'like'
        ).first()
        
        if existing:
            return {"message": "Already liked"}

    # 3. 새로운 액션 저장 (like or pass)
    new_action = UserAction(
        user_email=action.user_email,
        policy_id=action.policy_id,
        type=action.type
    )
    db.add(new_action)
    db.commit()
    
    return {"message": "Action saved", "action_id": new_action.id}

# 1-1. 특정 정책에 대한 좋아요 여부 확인 (버튼 활성화용)
@router.get("/check")
def check_action_status(user_email: str, policy_id: int, db: Session = Depends(get_db)):
    """
    특정 유저가 특정 정책을 이미 'like' 했는지 확인합니다.
    """
    existing = db.query(UserAction).filter(
        UserAction.user_email == user_email,
        UserAction.policy_id == policy_id,
        UserAction.type == 'like'
    ).first()
    
    return {"liked": True if existing else False}


# 2. 찜한 정책 목록 조회 (마이페이지용)
# 2. 찜한 정책 목록 조회 (마이페이지용 - 페이지네이션 적용)
@router.get("/likes")
def get_liked_policies(
    user_email: str, 
    page: int = 1, 
    limit: int = 12, 
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    region: Optional[str] = None,
    sort: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    해당 유저가 'like'한 정책들의 상세 정보를 반환합니다. (검색/필터/정렬/페이지네이션 적용)
    """
    # 1. Base Query: Join UserAction and Policy to allow filtering on Policy fields
    query = db.query(UserAction, Policy).join(Policy, UserAction.policy_id == Policy.id).filter(
        UserAction.user_email == user_email, 
        UserAction.type == 'like'
    )
    
    # 2. Apply Filters
    # 2-1. Keyword Search (Title or Summary)
    if keyword:
        query = query.filter(
            (Policy.title.ilike(f"%{keyword}%")) | 
            (Policy.summary.ilike(f"%{keyword}%"))
        )

    # 2-2. Category Filter
    if category and category != "전체":
        # Simply check if the genre string contains the category keyword
        query = query.filter(Policy.genre.ilike(f"%{category}%"))

    # 2-3. Region Filter
    if region and region != "전체" and region != "전국":
        # '전국' policies are usually shown for everyone, 
        # but if user specifically selects a region (e.g., 'Seoul'), 
        # they might want to see 'Seoul' ONLY or 'Seoul' + 'Nationwide'.
        # Following typical logic: Show policies matching region OR nationwide policies.
        query = query.filter(
            (Policy.region.ilike(f"%{region}%")) | 
            (Policy.region == "전국")
        )

    # 2-4. Closed Policy Filter (for 'closed' sort option or special filter)
    today = date.today()
    if sort == 'closed':
        # Show ONLY closed policies? Or sort by closed?
        # Usually "마감 정책" implies filtering for closed ones.
        query = query.filter(Policy.end_date < today)
    # If not specifically looking for closed, usually we don't filter them out unless requested
    # But often users want to see "Active" policies by default. 
    # For "My Likes", we usually show everything unless filtered.

    # 3. Apply Sorting
    if sort == 'deadline':
        # Order by closest deadline first (active policies first)
        # Null end_date (permanent) usually comes last or first depending on logic.
        # Let's put imminent deadlines first.
        query = query.order_by(Policy.end_date.asc())
    elif sort == 'popular':
        # If 'views' exists, use it. Otherwise, use ID as proxy or random.
        # Assuming we don't have a reliable 'views' on Policy in this snippet context (it wasn't imported/shown).
        # We'll fallback to Policy.id or just keep latest like.
        # Let's try UserAction count if possible? Too complex for now.
        # Fallback: Latest liked (Default)
        query = query.order_by(UserAction.created_at.desc())
    elif sort == 'latest':
        query = query.order_by(UserAction.created_at.desc())
    elif sort == 'closed':
         # Already filtered above, assume sorting by end_date desc (most recently closed)
        query = query.order_by(Policy.end_date.desc())
    else:
        # Default: Recently Liked
        query = query.order_by(UserAction.created_at.desc())

    # 4. Count Total Results
    total_count = query.count()
    if total_count == 0:
        return {
            "policies": [],
            "total_count": 0,
            "total_pages": 0,
            "current_page": page
        }

    total_pages = (total_count + limit - 1) // limit
    
    # Page Correction
    if page < 1: page = 1
    if page > total_pages: page = total_pages

    offset = (page - 1) * limit

    # 5. Fetch Data with Pagination
    # Note: Query returns tuples (UserAction, Policy) due to the join structure
    results = query.offset(offset).limit(limit).all()
    
    formatted_policies = []
    
    for action, policy in results:
        # Image Processing
        img_src = get_image_for_category(policy.genre)
        
        # Date Processing
        date_str = "상시 모집"
        if policy.end_date:
            date_str = f"{policy.end_date} 마감"
        elif policy.period:
            date_str = policy.period

        formatted_policies.append({
            "id": policy.id,
            "title": policy.title,
            "summary": policy.summary or "상세 내용을 확인하세요.",
            "genre": policy.genre or "기타",
            "period": date_str,
            "image": img_src,
            "link": policy.link or "#",
            "region": policy.region or "전국",
            # Add is_active flag for frontend UI (gray out closed)
            "is_active": not (policy.end_date and policy.end_date < today) if policy.end_date else True
        })
            
    return {
        "policies": formatted_policies,
        "total_count": total_count,
        "total_pages": total_pages,
        "current_page": page
    }


# 2-1. 찜한 정책 선택 삭제 [NEW]
@router.post("/likes/delete")
def delete_liked_policies(data: LikeDeleteRequest, db: Session = Depends(get_db)):
    """
    사용자가 선택한 찜한 정책들을 일괄 삭제합니다.
    """
    # 1. 조건에 맞는(이메일, like타입, 정책ID리스트) 데이터 삭제
    #    synchronize_session=False는 대량 삭제 시 세션 동기화 비용을 줄임
    deleted_count = db.query(UserAction).filter(
        UserAction.user_email == data.user_email,
        UserAction.type == 'like',
        UserAction.policy_id.in_(data.policy_ids)
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return {"message": "Deleted successfully", "count": deleted_count}


# 3. 관심 키워드 트렌드 통계 (차트용)
@router.get("/stats")
def get_user_stats(user_email: str, db: Session = Depends(get_db)):
    """
    유저의 like/pass 데이터를 분석하여 카테고리별 관심도를 반환합니다.
    """
    # 1. 해당 유저의 모든 액션 + 정책 장르 조인 조회
    #    SELECT action.type, policy.genre 
    #    FROM users_action AS action 
    #    JOIN being_test AS policy ON action.policy_id = policy.id
    #    WHERE action.user_email = ...
    
    results = db.query(UserAction.type, Policy.genre)\
        .join(Policy, UserAction.policy_id == Policy.id)\
        .filter(UserAction.user_email == user_email)\
        .all()
        
    # 2. 점수 집계
    #    Like: +10점, Pass: +1점 (예시 로직)
    #    또는 단순히 Like 개수만 셀 수도 있음
    
    category_scores = {}
    
    # 초기화 (모든 카테고리 0점으로 시작하고 싶다면)
    base_categories = ["취업", "창업", "주거", "금융", "교육", "복지"]
    for cat in base_categories:
        category_scores[cat] = 0
        
    for type_, genre in results:
        if not genre: continue
        
        # DB에 저장된 genre가 "취업/직무" 처럼 되어있을 수 있으므로 매핑 확인 필요
        # models.py의 FRONT_TO_DB_CATEGORY는 프론트->DB용이므로, 여기선 DB값을 기준으로 그룹핑
        
        # 간단하게 앞 2글자만 따서 분류하거나 포함여부 확인
        key = "기타"
        if "취업" in genre: key = "취업"
        elif "창업" in genre: key = "창업"
        elif "주거" in genre: key = "주거"
        elif "금융" in genre: key = "금융"
        elif "교육" in genre: key = "교육"
        elif "복지" in genre: key = "복지"
        
        score = 0
        if type_ == 'like':
            score = 10
        elif type_ == 'pass':
            score = 2  # 패스해도 봤다는 것에 의미를 둔다면 점수 부여 (선택사항)
            
        category_scores[key] = category_scores.get(key, 0) + score
        
    # 3. 차트용 데이터 변환
    labels = list(category_scores.keys())
    data = list(category_scores.values())
    
    return {"labels": labels, "data": data}
