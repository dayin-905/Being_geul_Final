import json
import re

# 1. 파일 설정 (파일명을 정확히 입력해주세요)
input_file_name = 'being_test_export.json'
output_file_name = 'being_test_export_updated.json'

def update_end_date_from_period():
    try:
        # JSON 파일 읽기
        with open(input_file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 데이터가 리스트인지 확인 (구조에 따라 처리)
        items = data if isinstance(data, list) else data.get(list(data.keys())[0], [])
        
        updated_count = 0
        
        for item in items:
            period = str(item.get('period', '')).strip()
            # 공백 제거 (파싱 용이성을 위해)
            clean_period = period.replace(" ", "")
            
            new_date = None
            
            # [규칙 1] 'YYYY.MM.DD' 형태로 끝나는 날짜 추출 (예: ~2025.12.31.)
            date_match = re.search(r'~(\d{4})\.(\d{1,2})\.(\d{1,2})', clean_period)
            if date_match:
                new_date = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
            
            # [규칙 2] 'YYYY.MM' 형태로 끝나는 경우 -> 해당 월의 말일로 설정 (예: ~2025.12. -> 2025-12-31)
            elif re.search(r'~(\d{4})\.(\d{1,2})', clean_period):
                month_match = re.search(r'~(\d{4})\.(\d{1,2})', clean_period)
                year, month = month_match.group(1), month_match.group(2).zfill(2)
                # 12월은 31일, 그 외는 30일로 단순화 (필요 시 calendar 모듈로 정확하게 가능하나 현재 목적상 충분)
                day = "31" if month == "12" or month == "01" or month == "03" or month == "05" or month == "07" or month == "08" or month == "10" else "30"
                if month == "02": day = "28"
                new_date = f"{year}-{month}-{day}"
                
            # [규칙 3] '2025년' 단어 포함 시 연말까지로 간주
            elif "2025년" in clean_period and "~" not in clean_period:
                new_date = "2025-12-31"
                
            # [규칙 4] '상시', '계속', '연중' 등은 마감되지 않은 먼 미래로 설정
            elif any(word in clean_period for word in ["상시", "계속", "연중", "소진시"]):
                new_date = "9999-12-31"

            # 날짜가 추출되었다면 end_date 업데이트
            if new_date:
                item['end_date'] = new_date
                updated_count += 1
                
        # 결과 파일 저장
        with open(output_file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"✅ 작업 완료!")
        print(f"총 {len(items)}개 데이터 중 {updated_count}개의 'end_date'를 실제 기간 기반으로 업데이트했습니다.")
        print(f"생성된 파일: {output_file_name}")

    except FileNotFoundError:
        print(f"❌ 오류: '{input_file_name}' 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

# 실행
if __name__ == "__main__":
    update_end_date_from_period()
