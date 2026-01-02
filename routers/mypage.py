from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
import os

from database import get_db
from models import UserAction, Policy, categoryColorMap, get_image_for_category, FRONT_TO_DB_CATEGORY

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

# ==================== [API 엔드포인트] ====================

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
@router.get("/likes")
def get_liked_policies(user_email: str, db: Session = Depends(get_db)):
    """
    해당 유저가 'like'한 정책들의 상세 정보를 반환합니다.
    """
    # 1. UserAction 테이블에서 해당 유저의 'like' 기록 조회 (최신순)
    #    중복 like가 있을 경우를 대비해 DISTINCT나 로직 처리 필요하지만 일단 단순 조회
    actions = db.query(UserAction)\
        .filter(UserAction.user_email == user_email, UserAction.type == 'like')\
        .order_by(UserAction.created_at.desc())\
        .all()
    
    if not actions:
        return []

    # 2. Policy ID 리스트 추출
    policy_ids = [a.policy_id for a in actions]
    
    # 3. Policy 테이블에서 정보 조회
    #    policy_ids에 포함된 정책들을 한 번에 가져옴
    policies = db.query(Policy).filter(Policy.id.in_(policy_ids)).all()
    
    # 4. 순서 보장 및 데이터 포맷팅
    #    DB in_ 쿼리는 순서를 보장하지 않으므로, actions 순서대로 정렬하거나 딕셔너리로 매핑
    policy_map = {p.id: p for p in policies}
    
    result = []
    seen_ids = set() # 중복 제거용

    for action in actions:
        pid = action.policy_id
        if pid in seen_ids:
            continue
        
        policy = policy_map.get(pid)
        if policy:
            seen_ids.add(pid)
            
            # 카테고리 이미지 처리
            img_src = get_image_for_category(policy.genre)
            
            # 날짜 처리
            date_str = "상시 모집"
            if policy.end_date:
                date_str = f"{policy.end_date} 마감"
            elif policy.period:
                date_str = policy.period

            result.append({
                "id": policy.id,
                "title": policy.title,
                "desc": policy.summary or "상세 내용을 확인하세요.",
                "category": policy.genre or "기타",
                "date": date_str,
                "image": img_src,
                "link": policy.link or "#",
                "region": policy.region or "전국",
                "colorCode": categoryColorMap.get(policy.genre, "#777777")
            })
            
    return result


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