import os
from sqlalchemy import text
from database import SessionLocal
from models import User, UserAction, Policy

db = SessionLocal()
email = "wjdekdls@naver.com"

print(f"--- Debugging User: {email} ---")
try:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print("User not found in DB!")
    else:
        print(f"User Found: {user.name} (Region: {user.region}, Provider: {user.provider})")
        
        # Count Likes (Orphan check)
        likes = db.query(UserAction).filter(UserAction.user_email == email, UserAction.type == 'like').all()
        print(f"Total Like UserActions: {len(likes)}")
        
        valid_likes = db.query(UserAction).join(Policy, UserAction.policy_id == Policy.id).filter(UserAction.type == 'like', UserAction.user_email == email).count()
        print(f"Valid Joined Likes: {valid_likes}")


        # Check for Pass actions
        passes = db.query(UserAction).filter(UserAction.user_email == email, UserAction.type == 'pass').all()
        print(f"Total Pass Count: {len(passes)}")

except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
