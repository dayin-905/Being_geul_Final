from fastapi import APIRouter, Request, Depends, HTTPException, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
import models
import os

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

# 템플릿 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# [간단한 관리자 인증] 실제 서비스에선 DB의 is_admin 필드 등을 써야 함
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "password123" # 실제로는 환경변수로 빼거나 DB 해시 대조 필요
}

@router.get("/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """관리자 전용 로그인 페이지 (Dark Theme)"""
    return templates.TemplateResponse("admin/login.html", {"request": request})

@router.post("/login")
async def admin_login_process(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """관리자 로그인 처리"""
    if username == ADMIN_CREDENTIALS["username"] and password == ADMIN_CREDENTIALS["password"]:
        # 세션이나 쿠키에 관리자 인증 정보를 심어야 하지만, MVP 단계에선 URL 파라미터나 간단한 쿠키 검증으로 대체 가능
        # 여기서는 간단히 대시보드로 리다이렉트하며 쿼리 파라미터로 눈속임 (보안상 취약하지만 프로토타입용)
        # 제대로 하려면 auth.py의 JWT 로직을 Admin용으로 별도 사용하여 쿠키를 구워야 함.
        # 일단은 템플릿 렌더링 시 success 플래그를 넘기는 식으로 구현 (실제 세션 구현은 복잡도가 큼)
        response = RedirectResponse(url="/admin/dashboard", status_code=303)
        response.set_cookie(key="admin_session", value="valid", httponly=True)
        return response
    
    return templates.TemplateResponse("admin/login.html", {
        "request": request, 
        "error": "아이디 또는 비밀번호가 잘못되었습니다."
    })

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """관리자 대시보드 (Red Bar Theme)"""
    # 쿠키 체크 (간단)
    admin_session = request.cookies.get("admin_session")
    if admin_session != "valid":
         return RedirectResponse(url="/admin/login", status_code=303)

    # 데이터 조회 (통계용)
    total_users = db.query(models.User).count()
    total_policies = db.query(models.Policy).count()
    user_actions = db.query(models.UserAction).order_by(models.UserAction.created_at.desc()).limit(20).all()

    # [추가 기능 1] 인기 정책 TOP 5 (Hot Policies)
    # (UserAction에서 policy_id 별로 그룹화 -> 개수 세기 -> 내림차순 정렬 -> 상위 5개)
    # SQLAlchemy의 func.count 사용 필요
    from sqlalchemy import func
    hot_policies_data = db.query(
        models.UserAction.policy_id, 
        func.count(models.UserAction.id).label("count")
    ).group_by(models.UserAction.policy_id).order_by(func.count(models.UserAction.id).desc()).limit(5).all()

    # hot_policies_data는 (policy_id, count) 튜플 리스트임.
    # 템플릿에서 정책 제목을 보여주려면 Policy 테이블 정보를 가져와야 함.
    hot_policies = []
    for pid, count in hot_policies_data:
        policy = db.query(models.Policy).filter(models.Policy.id == pid).first()
        if policy:
            hot_policies.append({"title": policy.title, "count": count, "id": policy.id})

    # [추가 기능 2] 지역별 통계 (Regional Stats)
    # 유저 분포
    user_regions = db.query(models.User.region, func.count(models.User.id)).group_by(models.User.region).all()
    # 정책 분포
    policy_regions = db.query(models.Policy.region, func.count(models.Policy.id)).group_by(models.Policy.region).all()

    # [추가 기능 3] 구독 등급 통계 (Subscription Rate)
    sub_stats = db.query(models.User.subscription_level, func.count(models.User.id)).group_by(models.User.subscription_level).all()
    
    # 데이터 가공 (템플릿에서 쓰기 쉽게)
    sub_counts = {"free": 0, "premium": 0}
    for level, count in sub_stats:
        if level in sub_counts:
            sub_counts[level] = count

    # [추가 기능 4] 정책 건강 상태 (Health Check)
    # 1. 내용(summary)이 비어있는 정책
    empty_summary_count = db.query(models.Policy).filter((models.Policy.summary == None) | (models.Policy.summary == "")).count()
    # 2. 마감 기한이 지난 정책 (문자열이라 정확한 비교는 어렵지만, 간단히 예시로 구현)
    # 실제로는 날짜 파싱이 필요하지만, 여기선 '2023'년도 데이터가 포함되어 있다면 그걸 셀 수도 있음.
    # 일단은 '내용 없음' 개수만 전달.

    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "total_users": total_users,
        "total_policies": total_policies,
        "recent_actions": user_actions,
        "hot_policies": hot_policies,
        "user_regions": user_regions,
        "policy_regions": policy_regions,
        "sub_counts": sub_counts,
        "empty_summary_count": empty_summary_count
    })

@router.get("/users", response_class=HTMLResponse)
async def admin_users(request: Request, db: Session = Depends(get_db)):
    """관리자용 유저 관리 페이지"""
    admin_session = request.cookies.get("admin_session")
    if admin_session != "valid":
         return RedirectResponse(url="/admin/login", status_code=303)
         
    users = db.query(models.User).all()
    
    # [NEW] Fetch distinct regions from Policy for edit dropdown
    all_regions_rows = db.query(models.Policy.region).distinct().filter(models.Policy.region != None).all()
    all_regions = sorted([r[0] for r in all_regions_rows if r[0]])
    
    return templates.TemplateResponse("admin/users.html", {
        "request": request, 
        "users": users,
        "regions": all_regions
    })

@router.post("/users/update")
async def update_user(
    request: Request,
    user_id: int = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    region: str = Form(None),
    subscription_level: str = Form(...),
    db: Session = Depends(get_db)
):
    """사용자 정보 수정 (Admin)"""
    admin_session = request.cookies.get("admin_session")
    if admin_session != "valid":
         return RedirectResponse(url="/admin/login", status_code=303)
         
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.name = name
        user.email = email
        user.region = region
        user.subscription_level = subscription_level
        db.commit()
        
    return RedirectResponse(url="/admin/users", status_code=303)

@router.get("/policies", response_class=HTMLResponse)
async def admin_policies(
    request: Request, 
    page: int = 1, 
    q: str = None, 
    sort: str = "id", 
    order: str = "desc",
    genres: str = None, # checkbox filters (comma separated)
    regions: str = None, # checkbox filters (comma separated)
    db: Session = Depends(get_db)
):
    """관리자용 정책 관리 페이지 (검색 & 상세 필터 & 정렬 & 페이지네이션)"""
    admin_session = request.cookies.get("admin_session")
    if admin_session != "valid":
         return RedirectResponse(url="/admin/login", status_code=303)
    
    # 1. Base Query
    query = db.query(models.Policy)
    
    # 2. Search Filter (Title Integrated Search)
    if q:
        search_key = f"%{q}%"
        query = query.filter(
            (models.Policy.title.ilike(search_key)) | 
            (models.Policy.summary.ilike(search_key))
        )

    # 3. Checkbox Filters (Exact Match for multiple selection)
    selected_genres = genres.split(",") if genres else []
    if selected_genres:
        query = query.filter(models.Policy.genre.in_(selected_genres))
        
    selected_regions = regions.split(",") if regions else []
    if selected_regions:
        query = query.filter(models.Policy.region.in_(selected_regions))
    
    # 4. Sorting
    allowed_sort_columns = ["id", "title", "period"] # Genre/Region removed from sort, handled by filter
    if sort not in allowed_sort_columns:
        sort = "id"
    
    sort_column = getattr(models.Policy, sort)
    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
        
    # 5. Pagination
    limit = 50
    offset = (page - 1) * limit
    
    total_policies = query.count()
    policies = query.offset(offset).limit(limit).all()
    
    import math
    total_pages = math.ceil(total_policies / limit) if total_policies > 0 else 1

    # 6. Fetch Distinct Options for Filter UI
    # (Select distinct genre from being_test ...)
    all_genres_rows = db.query(models.Policy.genre).distinct().filter(models.Policy.genre != None).all()
    all_genres = [r[0] for r in all_genres_rows if r[0]]
    
    all_regions_rows = db.query(models.Policy.region).distinct().filter(models.Policy.region != None).all()
    all_regions = [r[0] for r in all_regions_rows if r[0]]
    
    # Sort: Selected first, then Alphabetical
    all_genres.sort(key=lambda x: (x not in selected_genres, x))
    all_regions.sort(key=lambda x: (x not in selected_regions, x))
    
    return templates.TemplateResponse("admin/policies.html", {
        "request": request, 
        "policies": policies,
        "current_page": page,
        "total_pages": total_pages,
        "total_count": total_policies,
        "q": q or "",
        "sort": sort,
        "order": order,
        "all_genres": all_genres,
        "all_regions": all_regions,
        "selected_genres": selected_genres,
        "selected_regions": selected_regions
    })

@router.get("/logout")
async def admin_logout():
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie("admin_session")
    return response