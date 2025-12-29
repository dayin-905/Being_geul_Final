# Being Test Database

이 프로젝트는 `policies_remake.json` 파일의 데이터를 SQLite 데이터베이스로 변환한 것입니다.

## 📊 데이터베이스 정보

- **데이터베이스 파일**: `being_test.db`
- **테이블 이름**: `being_test`
- **총 레코드 수**: 1,090개
- **장르 수**: 6개
- **지역 수**: 18개

## 🗂️ 테이블 구조

```sql
CREATE TABLE being_test (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    summary TEXT,
    period TEXT,
    link TEXT,
    genre TEXT,
    region TEXT,
    original_id TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 컬럼 설명
- `id`: 자동 증가 기본 키
- `title`: 정책 제목
- `summary`: 정책 요약
- `period`: 정책 기간
- `link`: 정책 상세 링크
- `genre`: 정책 장르 (취업/직무, 복지/문화, 교육/자격증, 창업/사업, 주거/자립, 금융/생활비)
- `region`: 지역 (전국, 울산, 충남, 경남 등)
- `original_id`: 원본 정책 ID (고유값)
- `created_at`: 생성 시간
- `updated_at`: 수정 시간

## 📁 파일 목록

1. **policies_remake.json** - 원본 JSON 데이터 파일
2. **being_test.db** - 생성된 SQLite 데이터베이스
3. **create_being_test_db.sql** - MySQL용 테이블 생성 SQL 스크립트
4. **import_to_sqlite.py** - SQLite 데이터베이스 생성 및 데이터 임포트 스크립트
5. **import_to_db.py** - MySQL 데이터베이스용 임포트 스크립트
6. **query_db.py** - 데이터베이스 조회 유틸리티 스크립트
7. **fix_json.py** - JSON 파일 오류 수정 스크립트

## 🚀 사용 방법

### 1. 데이터베이스 생성 (이미 완료됨)

```bash
python3 import_to_sqlite.py
```

### 2. 데이터베이스 조회

#### 통계 보기
```bash
python3 query_db.py stats
```

#### 장르별 검색
```bash
python3 query_db.py genre 취업/직무
python3 query_db.py genre 복지/문화
python3 query_db.py genre 창업/사업
```

#### 지역별 검색
```bash
python3 query_db.py region 충남
python3 query_db.py region 서울
python3 query_db.py region 전국
```

#### 키워드 검색
```bash
python3 query_db.py keyword 청년
python3 query_db.py keyword 주거
python3 query_db.py keyword 취업
```

#### 특정 정책 상세 보기
```bash
python3 query_db.py detail 1
python3 query_db.py detail 100
```

## 📈 데이터 통계

### 장르별 분포
- 취업/직무: 575개 (52.8%)
- 복지/문화: 159개 (14.6%)
- 교육/자격증: 122개 (11.2%)
- 창업/사업: 113개 (10.4%)
- 주거/자립: 88개 (8.1%)
- 금융/생활비: 33개 (3.0%)

### 지역별 분포 (상위 5개)
1. 전국: 191개
2. 울산: 156개
3. 충남: 136개
4. 경남: 114개
5. 경북: 62개

## 💻 Python으로 직접 쿼리하기

```python
import sqlite3

# 데이터베이스 연결
conn = sqlite3.connect('being_test.db')
cursor = conn.cursor()

# 예제 쿼리 1: 충남 지역의 취업 관련 정책 조회
cursor.execute("""
    SELECT title, summary, period 
    FROM being_test 
    WHERE region = '충남' AND genre = '취업/직무'
    LIMIT 5
""")

for row in cursor.fetchall():
    print(f"제목: {row[0]}")
    print(f"요약: {row[1]}")
    print(f"기간: {row[2]}\n")

# 예제 쿼리 2: 청년 관련 정책 검색
cursor.execute("""
    SELECT title, genre, region 
    FROM being_test 
    WHERE title LIKE '%청년%' OR summary LIKE '%청년%'
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"{row[0]} ({row[1]}, {row[2]})")

# 연결 종료
conn.close()
```

## 🔧 MySQL로 마이그레이션하기

MySQL을 사용하고 싶다면:

1. MySQL 데이터베이스 생성
```sql
CREATE DATABASE your_database_name;
USE your_database_name;
```

2. 테이블 생성
```bash
mysql -u root -p your_database_name < create_being_test_db.sql
```

3. 데이터 임포트 (import_to_db.py 파일 수정 필요)
```python
# import_to_db.py 파일에서 데이터베이스 설정 수정
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'your_password'
DB_NAME = 'your_database_name'
```

4. 실행
```bash
python3 import_to_db.py
```

## 📝 참고사항

- SQLite 데이터베이스는 별도의 서버 설치 없이 바로 사용 가능합니다
- 데이터베이스 파일(`being_test.db`)은 약 2MB 크기입니다
- 인덱스가 `genre`, `region`, `original_id` 컬럼에 생성되어 있어 빠른 검색이 가능합니다
- JSON 파일에 오류가 있었으나 `fix_json.py`로 수정되었습니다

## 🐛 문제 해결

### JSON 파일 오류가 발생하는 경우
```bash
python3 fix_json.py
```

### 데이터베이스를 다시 생성하고 싶은 경우
```bash
rm being_test.db
python3 import_to_sqlite.py
```

---

**생성일**: 2025-12-23
**데이터 소스**: policies_remake.json
**총 정책 수**: 1,090개
