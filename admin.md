# Admin 페이지 오류 분석 및 수정 로그

## 1. 오류 현상
- **증상**: 관리자 로그인 후 `/admin/dashboard` 접속 시 500 Internal Server Error 발생.
- **오류 메시지**: `Internal Server Error` (DB 컬럼 부재로 인한 `OperationalError`)

## 2. 원인 분석
- **불일치 발생**: `models.py` 코드에는 `User` 테이블에 `subscription_level` 및 `provider` 컬럼이 정의되어 있으나, 실제 운영 DB에는 해당 컬럼이 생성되지 않음.
- **이유**: SQLAlchemy의 `create_all()` 함수는 테이블이 존재하지 않을 때만 생성하며, 이미 존재하는 테이블의 스키마 변경(Alter)은 수행하지 않음.

## 3. 조치 내역
### 3-1. DB 스키마 업데이트 스크립트 작성 및 실행
안전하게 DB 상태를 확인(`inspect`)하고, 누락된 컬럼만 추가하는 Python 스크립트를 작성하여 실행함.

#### 수행된 코드 (`fix_schema_add_column.py`)
```python
from sqlalchemy import inspect, text
from database import engine

def fix_schema_safely():
    print("🔧 Checking database schema safely...")
    
    # 1. Inspect current columns without causing SQL errors
    # SQLAlchemy Inspector를 사용하여 현재 DB의 컬럼 목록을 안전하게 조회
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('users')]
    print(f"🧐 Current columns in 'users': {columns}")

    with engine.connect() as connection:
        # Start a transaction for changes
        trans = connection.begin()
        try:
            # 2. Check and Add 'subscription_level'
            if 'subscription_level' not in columns:
                print("⚠️ 'subscription_level' is MISSING. Adding it...")
                # 실제 스키마 변경 쿼리 실행
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
```

### 3-2. 실행 결과
- `subscription_level` 컬럼이 성공적으로 추가됨.
- `provider` 컬럼은 이미 존재함이 확인됨.
- 에러 없이 스키마 동기화 완료.

## 4. 최종 결과
- `/admin/dashboard` 접속 시 더 이상 500 에러가 발생하지 않음.
- 관리자 대시보드 및 통계 기능 정상 작동 확인.
