import os
from dotenv import load_dotenv

load_dotenv()

print("=== 환경변수 점검 리포트 ===")
print(f"1. GOOGLE_CLIENT_ID 설정됨: {'YES' if os.getenv('GOOGLE_CLIENT_ID') else 'NO'}")
print(f"2. GOOGLE_REDIRECT_URI: {os.getenv('GOOGLE_REDIRECT_URI')}")
print(f"3. NAVER_CLIENT_ID 설정됨: {'YES' if os.getenv('NAVER_CLIENT_ID') else 'NO'}")
print(f"4. NAVER_REDIRECT_URI: {os.getenv('NAVER_REDIRECT_URI')}")
print("===========================")
