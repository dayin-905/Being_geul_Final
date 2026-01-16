from database import SessionLocal
from models import UserAction, Policy

db = SessionLocal()
email = "wjdekdls@naver.com"

print(f"--- Deleting Orphaned Likes for: {email} ---")

try:
    # 1. Find all likes for the user
    user_likes = db.query(UserAction).filter(UserAction.user_email == email, UserAction.type == 'like').all()
    
    deleted_count = 0
    for action in user_likes:
        # 2. Check if policy exists
        policy = db.query(Policy).filter(Policy.id == action.policy_id).first()
        
        if not policy:
            # 3. Orphan found -> Delete
            print(f"Deleting Orphaned Action ID: {action.id} (Policy ID: {action.policy_id})")
            db.delete(action)
            deleted_count += 1
            
    if deleted_count > 0:
        db.commit()
        print(f"Successfully deleted {deleted_count} orphaned records.")
    else:
        print("No orphaned records found.")

except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
