import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    connection = psycopg2.connect(
        host=os.getenv('DB_HOST', 'postgresql_db'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'main_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )
    
    cursor = connection.cursor()
    
    # 테이블 구조 확인
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = 'being_test'
        ORDER BY ordinal_position;
    """)
    
    print("\n현재 being_test 테이블 구조:")
    print("="*60)
    columns = cursor.fetchall()
    
    if columns:
        for col in columns:
            print(f"  - {col[0]}: {col[1]}" + (f"({col[2]})" if col[2] else ""))
    else:
        print("  테이블이 존재하지 않거나 컬럼이 없습니다.")
    
    print("="*60 + "\n")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"오류: {e}")
