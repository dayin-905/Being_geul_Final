import json
import psycopg2
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 데이터베이스 연결 정보 (환경변수 우선, 없으면 기본값)
DB_HOST = os.getenv("DB_HOST", "postgresql_db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "main_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def create_and_import():
    conn = None  # conn 변수 미리 초기화
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        print("1. 기존 테이블 삭제 중...")
        cur.execute("DROP TABLE IF EXISTS being_test;")
        
        print("2. 새로운 테이블 생성 중...")
        create_table_query = """
        CREATE TABLE being_test (
            id INTEGER PRIMARY KEY,
            title TEXT,
            summary TEXT,
            period TEXT,
            link TEXT,
            genre TEXT,
            region TEXT,
            original_id TEXT,
            created_at TIMESTAMP,
            end_date DATE,
            view_count INTEGER
        );
        """
        cur.execute(create_table_query)

        print("3. JSON 파일 읽는 중...")
        with open('/apps/Being_geul_Final/12.29_being_test.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"4. 데이터 임포트 시작 ({len(data)}개 레코드)...")
        
        insert_query = """
        INSERT INTO being_test (id, title, summary, period, link, genre, region, original_id, created_at, end_date, view_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        for item in data:
            # end_date가 빈 문자열("")이거나 None인 경우 NULL로 처리
            end_date = item.get('end_date')
            if not end_date:
                end_date = None
                
            cur.execute(insert_query, (
                item.get('id'),
                item.get('title'),
                item.get('summary'),
                item.get('period'),
                item.get('link'),
                item.get('genre'),
                item.get('region'),
                item.get('original_id'),
                item.get('created_at'),
                end_date,
                item.get('view_count', 0)
            ))

        conn.commit()
        print("✅ 임포트 완료!")
        
        # 확인용 카운트 출력
        cur.execute("SELECT COUNT(*) FROM being_test;")
        count = cur.fetchone()[0]
        print(f"총 {count}개의 데이터가 being_test 테이블에 저장되었습니다.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        if conn:
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    create_and_import()
