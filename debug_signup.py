from database import SessionLocal
from models import User
from passlib.context import CryptContext
import traceback

# 1. Test Password Hashing
print(">>> Testing Password Hashing...")
try:
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
    hash_test = pwd_context.hash("test1234")
    print(f"Hash Success: {hash_test[:20]}...")
except Exception:
    print("!!! Password Hashing Failed !!!")
    traceback.print_exc()
    exit(1)

# 2. Test DB Insert
print("\n>>> Testing DB Insert...")
db = SessionLocal()
try:
    # Check if user exists
    existing_user = db.query(User).filter(User.email == "debug@test.com").first()
    if existing_user:
        print("User already exists, deleting...")
        db.delete(existing_user)
        db.commit()

    new_user = User(
        email="debug@test.com",
        password=hash_test,
        name="DebugUser",
        region="Seoul",
        provider="local"
    )
    db.add(new_user)
    db.commit()
    print("DB Insert Success!")
except Exception:
    print("!!! DB Insert Failed !!!")
    traceback.print_exc()
finally:
    db.close()
