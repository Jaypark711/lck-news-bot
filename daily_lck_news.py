import os
import requests
import google.generativeai as genai
from datetime import datetime

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def get_lck_news():
    try:
        if not GEMINI_API_KEY:
            return "오류: API 키가 설정되지 않았습니다."
            
        genai.configure(api_key=GEMINI_API_KEY)
        
        # 최신 정보를 위해 구글 검색 기능 사용 시도
        # google_search_retrieval은 최신 SDK에서 지원하는 표준 도구 이름입니다.
        try:
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                tools=[{"google_search_retrieval": {}}]
            )
            
            today = datetime.now().strftime("%Y년 %m월 %d일")
            prompt = f"{today} 기준, LCK(League of Legends Champions Korea)의 가장 최신 뉴스 5가지를 구글 검색으로 찾아서 요약해줘. [제목 - 요약 - 출처] 형식으로 작성하고, 마지막에 '오늘의 LCK 소식 배달 완료!'라고 덧붙여줘. 한국어로 작성해."
            
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text
            else:
                return "AI가 응답을 생성했지만 텍스트가 비어있습니다."
                
        except Exception as search_error:
            print(f"검색 도구 사용 중 오류(일반 모델로 전환): {search_error}")
            # 검색 도구 실패 시 일반 모델로 전환하여 시도
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"{datetime.now().strftime('%Y-%m-%d')} LCK 최신 뉴스를 알려줘.")
            return response.text if response.text else "뉴스 요약 실패."

    except Exception as e:
        return f"전체 프로세스 중 치명적 오류 발생: {str(e)}"

def send_to_discord(content):
    if not DISCORD_WEBHOOK_URL:
        print("오류: 디스코드 웹훅 URL이 없습니다.")
        return
        
    try:
        header = f"📡 **오늘의 LCK 소식 브리핑 ({datetime.now().strftime('%m/%d')})**\n\n"
        full_message = header + content
        
        # 디스코드 글자수 제한(2000자) 처리
        if len(full_message) > 2000:
            full_message = full_message[:1990] + "..."
            
        payload = {"content": full_message}
        res = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        res.raise_for_status()
        print("디스코드 전송 성공!")
    except Exception as e:
        print(f"디스코드 전송 실패: {e}")

if __name__ == "__main__":
    print("=== LCK 뉴스 수집기 가동 ===")
    news = get_lck_news()
    send_to_discord(news)
    print("=== 작업 완료 ===")
