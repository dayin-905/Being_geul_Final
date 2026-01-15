from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from passlib.context import CryptContext

# 패스워드 해싱 설정 (auth.py와 동일하게 argon2 사용)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_admin_user():
    db = SessionLocal()
    
    email = "admin@example.com"
    password = "password123"
    hashed_password = pwd_context.hash(password)
    
    # 이미 존재하는지 확인
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if user:
        print(f"User {email} already exists. Updating to admin...")
        user.subscription_level = "admin"
        user.password = hashed_password # 비번도 초기화
        user.name = "관리자"
        db.commit()
    else:
        print(f"Creating new admin user {email}...")
        new_user = models.User(
            email=email,
            name="관리자",
            password=hashed_password,
            region="전국",
            provider="local",
            subscription_level="admin"
        )
        db.add(new_user)
        db.commit()
        
    print("✅ Admin user created/updated successfully.")
    print(f"Email: {email}")
    print(f"Password: {password}")

if __name__ == "__main__":
    # 테이블이 없을 수도 있으니 생성 (이미 있으면 무시됨)
    models.Base.metadata.create_all(bind=engine)
    create_admin_user()
