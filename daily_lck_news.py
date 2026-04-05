import os
import requests
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def get_lck_news():
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 구글 검색을 활용한 최신 LCK 뉴스 요약 프롬프트
    prompt = "오늘의 LCK(League of Legends Champions Korea) 최신 소식 5가지를 구글 검색을 통해 찾아서 요약해줘. [제목 - 요약 - 출처] 형식으로 작성하고, 마지막에 '오늘의 LCK 소식 배달 완료!'라고 덧붙여줘. 한국어로 작성해."
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"뉴스 가져오기 실패: {str(e)}"

def send_to_discord(content):
    if not content: return
    payload = {"content": content[:2000]}
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    news = get_lck_news()
    send_to_discord(news)
