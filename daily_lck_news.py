import os
import requests
import google.generativeai as genai
from datetime import datetime

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def get_lck_news():
    genai.configure(api_key=GEMINI_API_KEY)
    
    # 오늘 날짜 확인 (한국 시간 기준)
    today = datetime.now().strftime("%Y년 %m월 %d일")
    
    # 실시간 검색 도구 설정 (Grounding)
    # 최신 모델인 gemini-1.5-flash가 검색 기능을 가장 잘 지원합니다.
    try:
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=[{"google_search_preview": {}}]
        )
        
        prompt = f"{today} 기준, 최신 LCK(League of Legends Champions Korea) 소식 5가지를 구글 검색으로 찾아서 요약해줘. [제목 - 요약 - 출처] 형식으로 작성하고, 마지막에 '오늘의 LCK 소식 배달 완료!'라고 덧붙여줘. 한국어로 작성해."
        
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text
    except Exception as e:
        print(f"검색 모델 호출 실패: {e}")
        # 실패 시 일반 모델로 재시도
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"{today} 최신 LCK 뉴스 요약해줘.")
        return response.text
            
    return "뉴스를 가져오지 못했습니다."

def send_to_discord(content):
    if not content: return
    payload = {"content": f"📡 **오늘의 LCK 소식 브리핑**\n\n{content}"}
    requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)

if __name__ == "__main__":
    print(f"=== {datetime.now()} LCK 뉴스 실시간 수집 시작 ===")
    news = get_lck_news()
    send_to_discord(news)
    print("=== 작업 완료 ===")
