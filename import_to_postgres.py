import json
import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def create_connection():
    """PostgreSQL 데이터베이스 연결 생성"""
    try:
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST', 'postgresql_db'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'main_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres')
        )
        print("✅ PostgreSQL 데이터베이스 연결 성공")
        return connection
    except Error as e:
        print(f"❌ 데이터베이스 연결 오류: {e}")
        return None

def check_and_prepare_table(connection):
    """being_test 테이블 확인 및 준비"""
    cursor = connection.cursor()
    
    try:
        # 테이블 존재 확인
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'being_test'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("✅ being_test 테이블 발견")
        else:
            print("⚠️  being_test 테이블이 없습니다. 생성 중...")
            create_table_query = """
            CREATE TABLE being_test (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                summary TEXT,
                period TEXT,
                link TEXT,
                genre TEXT,
                region TEXT
            );
            """
            cursor.execute(create_table_query)
            connection.commit()
            print("✅ being_test 테이블 생성 완료")
        
        # 인덱스 생성
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_genre ON being_test(genre);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_region ON being_test(region);")
        connection.commit()
        print("✅ 인덱스 확인/생성 완료")
        
    except Error as e:
        print(f"❌ 테이블 준비 오류: {e}")
        connection.rollback()
    finally:
        cursor.close()

def clear_table(connection):
    """기존 데이터 삭제"""
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM being_test;")
        connection.commit()
        print("✅ 기존 데이터 삭제 완료")
    except Error as e:
        print(f"❌ 데이터 삭제 오류: {e}")
    finally:
        cursor.close()

def insert_policy_data(connection, policy):
    """단일 정책 데이터 삽입"""
    cursor = connection.cursor()
    
    query = """
    INSERT INTO being_test (title, summary, period, link, genre, region)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    values = (
        policy.get('title', ''),
        policy.get('summary', ''),
        policy.get('period', ''),
        policy.get('link', ''),
        policy.get('genre', ''),
        policy.get('region', '')
    )
    
    try:
        cursor.execute(query, values)
        return True
    except Error as e:
        print(f"❌ 정책 삽입 오류: {e}")
        return False
    finally:
        cursor.close()

def main():
    print("\n" + "="*60)
    print("PostgreSQL Being Test Database Import")
    print("="*60 + "\n")
    
    # JSON 파일 읽기
    json_file = 'policies_remake.json'
    print(f"📖 {json_file} 파일 읽는 중...")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            policies = json.load(f)
        print(f"✅ {len(policies)}개의 정책 데이터 로드 완료\n")
    except FileNotFoundError:
        print(f"❌ {json_file} 파일을 찾을 수 없습니다!")
        return
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 오류: {e}")
        return
    
    # 데이터베이스 연결
    connection = create_connection()
    if connection is None:
        return
    
    try:
        # 테이블 확인 및 준비
        check_and_prepare_table(connection)
        
        # 기존 데이터 삭제 여부 확인
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM being_test;")
        existing_count = cursor.fetchone()[0]
        cursor.close()
        
        if existing_count > 0:
            print(f"\n⚠️  기존 데이터 {existing_count}개 발견")
            print("기존 데이터를 삭제하고 새로 입력합니다...\n")
            clear_table(connection)
        
        # 데이터 삽입
        print("📥 데이터 삽입 중...\n")
        success_count = 0
        fail_count = 0
        
        for i, policy in enumerate(policies, 1):
            if insert_policy_data(connection, policy):
                success_count += 1
            else:
                fail_count += 1
            
            # 진행상황 표시
            if i % 100 == 0:
                print(f"진행중... {i}/{len(policies)} ({i*100//len(policies)}%)")
        
        # 커밋
        connection.commit()
        
        # 최종 통계
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM being_test;")
        total_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT genre) FROM being_test;")
        total_genres = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT region) FROM being_test;")
        total_regions = cursor.fetchone()[0]
        
        cursor.close()
        
        print("\n" + "="*60)
        print("✅ 데이터 임포트 완료!")
        print("="*60)
        print(f"성공: {success_count}개")
        print(f"실패: {fail_count}개")
        print(f"총 레코드: {total_records}개")
        print(f"장르 수: {total_genres}개")
        print(f"지역 수: {total_regions}개")
        print("="*60 + "\n")
        
        # 샘플 데이터 표시
        print("📋 샘플 데이터 (처음 5개):\n")
        cursor = connection.cursor()
        cursor.execute("SELECT id, title, genre, region FROM being_test ORDER BY id LIMIT 5;")
        for row in cursor.fetchall():
            print(f"  ID {row[0]}: {row[1][:50]}...")
            print(f"          장르: {row[2]}, 지역: {row[3]}\n")
        cursor.close()
        
    except Error as e:
        print(f"❌ 오류 발생: {e}")
        connection.rollback()
    finally:
        if connection:
            connection.close()
            print("데이터베이스 연결 종료")

if __name__ == "__main__":
    main()
