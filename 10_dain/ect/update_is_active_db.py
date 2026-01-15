import sys
import os
from datetime import date
from sqlalchemy import text

# 프로젝트 루트 경로 추가 (모듈 임포트 가능하게)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import SessionLocal, engine
from models import Policy

def update_db_schema_and_data():
    db = SessionLocal()
    try:
        print("🚀 DB 마이그레이션 및 데이터 업데이트 시작...")

        # 1. 컬럼 추가 (DDL)
        # SQLAlchemy 모델에 추가했더라도 기존 테이블엔 자동으로 반영되지 않으므로 수동으로 추가 시도
        try:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE being_test ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
                conn.commit()
            print("✅ 'is_active' 컬럼이 성공적으로 추가되었습니다.")
        except Exception as e:
            # 컬럼이 이미 존재할 경우 에러가 발생할 수 있음
            if "duplicate column" in str(e) or "already exists" in str(e):
                print("ℹ️ 'is_active' 컬럼이 이미 존재합니다. 스킵합니다.")
            else:
                print(f"⚠️ 컬럼 추가 중 경고 발생 (이미 존재할 수 있음): {e}")

        # 2. 데이터 업데이트 시작
        print("🔄 데이터 상태 업데이트 중...")
        
        all_policies = db.query(Policy).all()
        total_count = len(all_policies)
        updated_count = 0
        active_count = 0
        inactive_count = 0
        
        today = date.today()
        
        for policy in all_policies:
            # 기본값 True로 설정 (없을 경우 대비)
            if policy.is_active is None:
                policy.is_active = True
            
            # 마감일 체크
            if policy.end_date:
                # end_date가 문자열이면 date 객체로 변환 필요할 수도 있으나, 
                # models.py에서 Date 타입이므로 객체로 올 것임.
                # 혹시 모르니 타입 체크
                target_date = policy.end_date
                if isinstance(target_date, str):
                    # 문자열인 경우 처리가 복잡해질 수 있으나, 보통 Date타입이면 변환됨
                    # 여기선 안전하게 패스하거나 로깅
                    pass 
                
                if target_date < today:
                    policy.is_active = False
                    updated_count += 1
                else:
                    policy.is_active = True
            else:
                # 마감일 없으면 상시 모집 -> Active
                policy.is_active = True
            
            if policy.is_active:
                active_count += 1
            else:
                inactive_count += 1
        
        db.commit()
        
        print("-" * 50)
        print(f"🎉 업데이트 완료!")
        print(f"📊 전체 정책 수: {total_count}개")
        print(f"🟢 모집 중 (Active): {active_count}개")
        print(f"🔴 모집 마감 (Inactive): {inactive_count}개")
        print("-" * 50)
        
        # 마감 정책 비율 계산
        if total_count > 0:
            inactive_ratio = (inactive_count / total_count) * 100
            print(f"📉 마감 정책 비율: {inactive_ratio:.1f}%")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_db_schema_and_data()
