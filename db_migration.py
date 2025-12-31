from sqlalchemy import inspect, text
from database import engine

def fix_schema_safely():
    print("🔧 Checking database schema safely...")
    
    # 1. Inspect current columns without causing SQL errors
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        print(f"🧐 Current columns in 'users': {columns}")
    except Exception as e:
        print(f"⚠️ Could not inspect table 'users' (it might not exist yet). Skipping migration.\nError: {e}")
        return

    with engine.connect() as connection:
        # Start a transaction for changes
        trans = connection.begin()
        try:
            # 2. Check and Add 'subscription_level'
            if 'subscription_level' not in columns:
                print("⚠️ 'subscription_level' is MISSING. Adding it...")
                connection.execute(text("ALTER TABLE users ADD COLUMN subscription_level VARCHAR DEFAULT 'free'"))
                print("✅ 'subscription_level' added successfully.")
            else:
                print("✅ 'subscription_level' already exists.")

            # 3. Check and Add 'provider'
            if 'provider' not in columns:
                print("⚠️ 'provider' is MISSING. Adding it...")
                connection.execute(text("ALTER TABLE users ADD COLUMN provider VARCHAR DEFAULT 'local'"))
                print("✅ 'provider' added successfully.")
            else:
                print("✅ 'provider' already exists.")

            trans.commit()
            print("\n🎉 Schema update completed successfully!")
            
        except Exception as e:
            trans.rollback()
            print(f"\n❌ Error during update: {e}")

if __name__ == "__main__":
    fix_schema_safely()
