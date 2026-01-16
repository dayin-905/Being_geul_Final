from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, UserAction, Policy

DATABASE_URL = "sqlite:///./being_test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

email = "wjdekdls@naver.com"

print(f"--- Debugging User: {email} ---")
user = db.query(User).filter(User.email == email).first()
if not user:
    print("User not found!")
else:
    print(f"User Name: {user.name}, Region: {user.region}")

likes = db.query(UserAction).filter(UserAction.user_email == email, UserAction.type == 'like').all()
print(f"Total Like Count: {len(likes)}")

for action in likes:
    policy = db.query(Policy).filter(Policy.id == action.policy_id).first()
    p_title = policy.title[:20] if policy else "Unknown"
    print(f" - ActionID: {action.id}, PolicyID: {action.policy_id}, Title: {p_title}")

db.close()
