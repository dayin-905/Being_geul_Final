from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from database import get_db
from models import Policy, User, UserAction, FRONT_TO_DB_CATEGORY

router = APIRouter(prefix="/api/recommend", tags=["recommendation"])

# DB 카테고리 역매핑 (취업 -> job) - 프론트엔드 링크 생성용
DB_TO_FRONT_CATEGORY = {v: k for k, v in FRONT_TO_DB_CATEGORY.items() if v}

@router.get("/status")
def get_recommendation_status(
    user_email: str | None = Query(None),
    db: Session = Depends(get_db)
):
    """
    Stateless Recommendation Logic (DB 추가 없이 실시간 계산)
    """
    alerts = []
    
    # 0. 비로그인 유저 (기본 인기 정책만)
    if not user_email:
        # 전국 인기 정책 1개
        best = db.query(Policy).order_by(desc(Policy.view_count)).first()
        if best:
            alerts.append({
                "type": "best",
                "icon": "🔥",
                "title": "지금 가장 핫한 정책",
                "message": f"'{best.title}' 지금 확인해보세요!",
                "link": f"/all.html?policy_id={best.id}" # 상세 페이지로 바로 이동
            })
        return alerts

    # 로그인 유저 정보 가져오기
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        return []

    user_region = user.region if user.region else "전국"

    # ====================================================
    # 1. [New Arrivals] 우리 동네 신규 (최근 7일)
    # ====================================================
    seven_days_ago = datetime.now() - timedelta(days=7)
    new_count = db.query(Policy).filter(
        Policy.region.like(f"%{user_region}%"),
        Policy.created_at >= seven_days_ago
    ).count()

    if new_count > 0:
        alerts.append({
            "type": "new",
            "icon": "✨",
            "title": f"{user_region} 신규 정책",
            "message": f"최근 7일간 <span class='text-primary-teal font-bold'>{new_count}건</span>이 새로 올라왔어요.",
            "link": f"/all.html?region={user_region}&sort=new"
        })

    # ====================================================
    # 2. [Deadline Watch] 찜한 정책 마감 임박 (3일 내)
    # ====================================================
    # 유저가 좋아요(like)한 정책 ID 목록
    liked_policy_ids = db.query(UserAction.policy_id).filter(
        UserAction.user_email == user_email,
        UserAction.type == "like"
    ).all()
    liked_ids = [pid[0] for pid in liked_policy_ids]

    if liked_ids:
        three_days_later = datetime.now().date() + timedelta(days=3)
        today = datetime.now().date()
        
        imminent_policy = db.query(Policy).filter(
            Policy.id.in_(liked_ids),
            Policy.end_date >= today,
            Policy.end_date <= three_days_later
        ).first()

        if imminent_policy:
            days_left = (imminent_policy.end_date - today).days
            d_day_str = "오늘 마감" if days_left == 0 else f"D-{days_left}"
            
            alerts.append({
                "type": "deadline",
                "icon": "🚨",
                "title": "찜한 정책 마감 임박",
                "message": f"'{imminent_policy.title}' (<span class='text-red-500 font-bold'>{d_day_str}</span>)",
                "link": f"/mypage.html?policy_id={imminent_policy.id}&open_modal=true"
            })

    # ====================================================
    # 3. [Interest Match] 관심 분야 추천
    # ====================================================
    # 유저가 가장 많이 찜한 카테고리 추출
    if liked_ids:
        # 가장 많이 등장한 카테고리 1위
        top_category = db.query(Policy.genre).filter(Policy.id.in_(liked_ids))\
            .group_by(Policy.genre).order_by(func.count(Policy.genre).desc()).first()
        
        if top_category:
            cat_name = top_category[0]
            # 해당 카테고리의 인기 정책 (이미 본 것 제외)
            rec_policy = db.query(Policy).filter(
                Policy.genre == cat_name,
                ~Policy.id.in_(liked_ids)
            ).order_by(desc(Policy.view_count)).first()

            if rec_policy:
                alerts.append({
                    "type": "interest",
                    "icon": "❤️",
                    "title": f"<span class='text-blue-500 font-bold'>'{cat_name}'</span> 분야 추천",
                    "message": f"<span class='text-primary-orange font-bold'>{user.name}</span>님 취향저격! '{rec_policy.title}'",
                    "link": f"/all.html?policy_id={rec_policy.id}&open_modal=true"
                })

    # ====================================================
    # 4. [Region Best] 우리 동네 인기 1위
    # ====================================================
    local_best = db.query(Policy).filter(
        Policy.region.like(f"%{user_region}%")
    ).order_by(desc(Policy.view_count)).first()

    if local_best:
        alerts.append({
            "type": "best_local",
            "icon": "🔥",
            "title": f"{user_region} 인기 <span class='text-red-500 font-bold'>1위</span>",
            "message": f"'{local_best.title}'",
            "link": f"/all.html?policy_id={local_best.id}&open_modal=true"
        })

    return alerts

# [NEW] 단일 정책 조회 API (모달 띄우기용)
@router.get("/policy/{policy_id}")
def get_policy_detail(
    policy_id: int,
    db: Session = Depends(get_db)
):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        return None
    
    # 프론트엔드 모달 포맷에 맞춰 데이터 변환
    # (policy_modal.js가 기대하는 데이터 구조)
    return {
        "id": policy.id,
        "title": policy.title,
        "summary": policy.summary, # or desc
        "desc": policy.summary,
        "genre": policy.genre, # or category
        "category": policy.genre,
        "period": policy.period,
        "date": policy.period,
        "link": policy.link,
        "image": f"/static/images/card_images/{(DB_TO_FRONT_CATEGORY.get(policy.genre, 'welfare'))}_{policy.id % 5 + 1}.webp"
    }
