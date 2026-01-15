# [수정] String, ForeignKey 추가, relationship 추가
from sqlalchemy import Column, Integer, Text, String, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# 1. 정책 테이블 (기존)
class Policy(Base):
    __tablename__ = "being_test"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    summary = Column(Text)
    period = Column(Text)
    link = Column(Text)
    genre = Column(Text)
    region = Column(Text)
    original_id = Column(Text)
    created_at = Column(DateTime)
    end_date = Column(Date)
    view_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True) # [NEW] 공개 여부 (True: 모집중, False: 마감)

# 2. 사용자 테이블 (신규)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 여기서 String을 사용하기 때문에 맨 위 import에 String이 꼭 있어야 합니다.
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=True)
    region = Column(String, nullable=True)
    provider = Column(String, default="local") # [NEW] 로그인 제공자 (local, google, naver)

    # [NEW] 유료 멤버십 등급 (free / premium)
    subscription_level = Column(String, default="free")
    
    # [NEW] 프로필 아이콘 (avatar_1 ~ avatar_6)
    profile_icon = Column(String, default="avatar_1")

    # [NEW] 관계 설정 (유저가 지워지면 행동 로그도 지워짐)
    actions = relationship("UserAction", back_populates="user", cascade="all, delete")

# 3. 사용자 행동(좋아요/패스) 테이블 (신규)
from datetime import datetime

class UserAction(Base):
    __tablename__ = "users_action"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 1. user_id 대신 user_email 사용
    user_email = Column(String, ForeignKey("users.email"))
    
    # 2. policy_id (동일)
    policy_id = Column(Integer, ForeignKey("being_test.id"))
    
    # 3. action_type -> type
    type = Column(String, nullable=False)
    
    # 4. timestamp -> created_at
    created_at = Column(DateTime, default=datetime.now)

    # Relationship (Join condition 명시)
    user = relationship("User", back_populates="actions", foreign_keys=[user_email])

# -------------------------------------------------------------------
# [추가] 서버 실행을 위한 상수 및 헬퍼 함수 (재복구)
# -------------------------------------------------------------------
import random

# 1. 카테고리 매핑 (프론트엔드 -> DB)
FRONT_TO_DB_CATEGORY = {
    "취업/직무": "취업",
    "창업/사업": "창업",
    "주거/자립": "주거",
    "금융/생활비": "금융",
    "교육/자격증": "교육",
    "복지/문화": "복지",
    "job": "취업",
    "startup": "창업",
    "housing": "주거",
    "finance": "금융",
    "growth": "교육",
    "welfare": "복지",
    "all": None
}

# 2. 카테고리별 색상 코드 (프론트엔드와 통일)
categoryColorMap = {
    "취업": "#00C4B4",
    "창업": "#FF6B6B",
    "주거": "#F48245",
    "금융": "#FFD166",
    "교육": "#4D96FF",
    "복지": "#FF9F43",
    "기타": "#777777"
}

# 3. 지역명 표준화 함수
def normalize_region_name(region):
    if not region:
        return '전국'
    region_mapping = {
        '서울': '서울', '서울특별시': '서울',
        '경기': '경기', '경기도': '경기',
        '인천': '인천', '인천광역시': '인천',
        '부산': '부산', '부산광역시': '부산',
        '대구': '대구', '대구광역시': '대구',
        '광주': '광주', '광주광역시': '광주',
        '대전': '대전', '대전광역시': '대전',
        '울산': '울산', '울산광역시': '울산',
        '세종': '세종', '세종특별자치시': '세종',
        '강원': '강원', '강원도': '강원', '강원특별자치도': '강원',
        '충북': '충북', '충청북도': '충북',
        '충남': '충남', '충청남도': '충남',
        '전북': '전북', '전라북도': '전북', '전북특별자치도': '전북',
        '전남': '전남', '전라남도': '전남',
        '경북': '경북', '경상북도': '경북',
        '경남': '경남', '경상남도': '경남',
        '제주': '제주', '제주도': '제주', '제주특별자치도': '제주'
    }
    clean_region = region.strip()
    return region_mapping.get(clean_region, clean_region[:2])

# 4. 카테고리별 이미지 선택 함수
def get_image_for_category(category: str) -> str:
    cat_code = "welfare"
    if not category:  # Handle None or empty string
        category = ""
        
    if "주거" in category:
        cat_code = "housing"
    elif "금융" in category:
        cat_code = "finance"
    elif "취업" in category:
        cat_code = "job"
    elif "창업" in category:
        cat_code = "startup"
    elif "교육" in category:
        cat_code = "growth"
    
    random_index = random.randint(1, 5)
    return f"/static/images/card_images/{cat_code}_{random_index}.webp"