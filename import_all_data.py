import json
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# DB 연결 정보
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")  # 팀원들 각자 환경에 맞게
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "main_db")

# 연결 URL 구성
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

def import_table_from_json(table_name, json_file):
    print(f"\n🔄 Importing '{table_name}' from {json_file}...")
    
    if not os.path.exists(json_file):
        print(f"⚠️ File not found: {json_file}. Skipping.")
        return

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not data:
        print("⚠️ No data in JSON file. Skipping.")
        return

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # 1. 기존 데이터 삭제 (Clean slate)
            conn.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))
            print(f"🧹 Cleared existing data in table '{table_name}'.")

            # 2. 데이터 삽입
            # 첫 번째 아이템으로 컬럼 명 추출
            columns = list(data[0].keys())
            cols_str = ", ".join(columns)
            vals_str = ", ".join([f":{c}" for c in columns])
            
            stmt = text(f"INSERT INTO {table_name} ({cols_str}) VALUES ({vals_str})")
            
            # 대량 삽입 실행
            conn.execute(stmt, data)
            
            trans.commit()
            print(f"✅ Successfully imported {len(data)} rows into '{table_name}'.")
            
            # 3. ID 시퀀스 동기화 (PK 충돌 방지)
            if 'id' in columns:
                try:
                    # id 중 가장 큰 값을 찾아서 시퀀스를 그 다음 값으로 설정
                    seq_name = f"{table_name}_id_seq"
                    # PostgreSQL에서 시퀀스 업데이트
                    conn.execute(text(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), COALESCE(MAX(id), 1)) FROM {table_name}"))
                    print("🔢 ID sequence updated.")
                except Exception as seq_err:
                    print(f"ℹ️ Sequence update skipped (might not exist or different name): {seq_err}")
                    
        except Exception as e:
            trans.rollback()
            print(f"❌ Error importing {table_name}: {e}")

if __name__ == "__main__":
    print("🚀 Starting Data Import Process...")
    
    # 순서 중요: users (부모) -> being_test (부모) -> users_action (자식)
    import_table_from_json("users", "shared_users.json")
    import_table_from_json("being_test", "shared_being_test.json")
    import_table_from_json("users_action", "shared_users_action.json")
    
    print("\n✨ All imports completed!")
