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

# 패스워드 검증을 위한 설정 (auth.py와 동일)
from sqlalchemy import func
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

@router.get("/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """관리자 전용 로그인 페이지 (Dark Theme)"""
    return templates.TemplateResponse("admin/login.html", {"request": request})

@router.post("/login")
async def admin_login_process(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """관리자 로그인 처리 (DB 연동)"""
    # 1. 유저 조회
    user = db.query(models.User).filter(models.User.email == email).first()
    
    # 2. 유저 존재 여부 및 비밀번호 검증
    if not user or not pwd_context.verify(password, user.password):
        return templates.TemplateResponse("admin/login.html", {
            "request": request, 
            "error": "이메일 또는 비밀번호가 잘못되었습니다."
        })
    
    # 3. 관리자 권한(Admin Role) 체크
    if user.subscription_level != "admin":
        return templates.TemplateResponse("admin/login.html", {
            "request": request, 
            "error": "관리자 접근 권한이 없습니다."
        })

    # 4. 로그인 성공 처리
    response = RedirectResponse(url="/admin/dashboard", status_code=303)
    # 보안: 실제로는 JWT 등을 써야 하지만, MVP에서는 HttpOnly 쿠키로 세션 흉내
    response.set_cookie(key="admin_session", value="valid", httponly=True)
    return response

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """관리자 대시보드 (통계 시각화 추가)"""
    admin_session = request.cookies.get("admin_session")
    if admin_session != "valid":
         return RedirectResponse(url="/admin/login", status_code=303)

    # 1. Basic Stats
    total_users = db.query(models.User).count()
    total_policies = db.query(models.Policy).count()
    premium_users = db.query(models.User).filter(models.User.subscription_level == 'premium').count()
    
    # 2. Recent Actions (Logs)
    recent_actions = db.query(models.UserAction).order_by(models.UserAction.created_at.desc()).limit(10).all()
    
    # [Restored] 3. Popular Policies (Hot Policies)
    from sqlalchemy import func
    hot_policies_data = db.query(
        models.UserAction.policy_id, 
        func.count(models.UserAction.id).label("count")
    ).group_by(models.UserAction.policy_id).order_by(func.count(models.UserAction.id).desc()).limit(5).all()

    hot_policies = []
    for pid, count in hot_policies_data:
        policy = db.query(models.Policy).filter(models.Policy.id == pid).first()
        if policy:
             hot_policies.append({"title": policy.title, "count": count, "id": policy.id})

    # [Restored] 4. Regional Stats (for HTML Bar Chart)
    # 유저 분포
    user_regions = db.query(models.User.region, func.count(models.User.id)).group_by(models.User.region).all()
    
    # [Restored] 5. Health Check
    empty_summary_count = db.query(models.Policy).filter((models.Policy.summary == None) | (models.Policy.summary == "")).count()

    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "total_users": total_users,
        "total_policies": total_policies,
        "recent_actions": recent_actions,
        "hot_policies": hot_policies,
        "user_regions": user_regions,
        "empty_summary_count": empty_summary_count
    })

@router.get("/users", response_class=HTMLResponse)
async def admin_users(
    request: Request, 
    q: str = None,
    level: str = None,
    db: Session = Depends(get_db)
):
    """관리자용 유저 관리 페이지 (검색 및 필터 추가)"""
    admin_session = request.cookies.get("admin_session")
    if admin_session != "valid":
         return RedirectResponse(url="/admin/login", status_code=303)
         
    query = db.query(models.User)
    
    # 1. Search (Name or Email)
    if q:
        search_key = f"%{q}%"
        query = query.filter(
            (models.User.email.ilike(search_key)) | 
            (models.User.name.ilike(search_key))
        )
        
    # 2. Filter (Subscription Level)
    if level:
        query = query.filter(models.User.subscription_level == level)
        
    users = query.all()
    
    # Distinct regions for edit modal
    all_regions_rows = db.query(models.Policy.region).distinct().filter(models.Policy.region != None).all()
    all_regions = sorted([r[0] for r in all_regions_rows if r[0]])
    
    return templates.TemplateResponse("admin/users.html", {
        "request": request, 
        "users": users,
        "regions": all_regions,
        "q": q or "",       # for template value
        "level": level or "" # for template selected
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

# [NEW] Policy CRUD Operations

@router.get("/policies/{policy_id}/edit", response_class=HTMLResponse)
async def admin_policy_edit(request: Request, policy_id: int, db: Session = Depends(get_db)):
    """정책 수정 페이지"""
    admin_session = request.cookies.get("admin_session")
    if admin_session != "valid":
         return RedirectResponse(url="/admin/login", status_code=303)

    policy = db.query(models.Policy).filter(models.Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    # Dropdown Options
    all_genres_rows = db.query(models.Policy.genre).distinct().filter(models.Policy.genre != None).all()
    all_genres = [r[0] for r in all_genres_rows if r[0]]

    all_regions_rows = db.query(models.Policy.region).distinct().filter(models.Policy.region != None).all()
    all_regions = sorted([r[0] for r in all_regions_rows if r[0]])

    return templates.TemplateResponse("admin/policy_edit.html", {
        "request": request,
        "policy": policy,
        "all_genres": all_genres,
        "all_regions": all_regions
    })

@router.post("/policies/{policy_id}/update")
async def admin_policy_update(
    request: Request,
    policy_id: int,
    title: str = Form(...),
    summary: str = Form(None),
    period: str = Form(None),
    link: str = Form(None),
    genre: str = Form(None),
    region: str = Form(None),
    db: Session = Depends(get_db)
):
    """정책 수정 처리"""
    admin_session = request.cookies.get("admin_session")
    if admin_session != "valid":
         return RedirectResponse(url="/admin/login", status_code=303)

    policy = db.query(models.Policy).filter(models.Policy.id == policy_id).first()
    if policy:
        policy.title = title
        policy.summary = summary
        policy.period = period
        policy.link = link
        policy.genre = genre
        policy.region = region
        db.commit()

    return RedirectResponse(url="/admin/policies", status_code=303)

@router.post("/policies/{policy_id}/delete")
async def admin_policy_delete(request: Request, policy_id: int, db: Session = Depends(get_db)):
    """정책 삭제 처리"""
    admin_session = request.cookies.get("admin_session")
    if admin_session != "valid":
         return RedirectResponse(url="/admin/login", status_code=303)

    policy = db.query(models.Policy).filter(models.Policy.id == policy_id).first()
    if policy:
        db.delete(policy)
        db.commit()

    return RedirectResponse(url="/admin/policies", status_code=303)