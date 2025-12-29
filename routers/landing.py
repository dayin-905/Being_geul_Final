from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Policy  # models.py에 정의된 Policy 클래스 사용

# 이 라우터의 주소는 무조건 /api/landing 으로 시작합니다.
router = APIRouter(prefix="/api/landing", tags=["landing"])

@router.get("/stats")
def get_region_stats(db: Session = Depends(get_db)):
    """
    DB(being_test 테이블)에서 지역(region)별로 몇 개가 있는지 세어서 반환합니다.
    결과 예시: {"서울": 150, "경기": 200, "제주": 50, ...}
    """
    # SQL: SELECT region, count(*) FROM being_test GROUP BY region;
    results = db.query(Policy.region, func.count(Policy.region))\
                .group_by(Policy.region)\
                .all()
    
    # 리스트 결과를 보기 편한 딕셔너리(JSON) 형태로 변환
    return {region: count for region, count in results}