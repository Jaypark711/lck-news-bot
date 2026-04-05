import os
import requests
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def get_lck_news():
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # 모델명을 models/gemini-1.5-flash로 명시적으로 지정
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = "오늘의 LCK(League of Legends Champions Korea) 최신 소식 5가지를 찾아서 요약해줘. [제목 - 요약 - 출처] 형식으로 작성하고, 마지막에 '오늘의 LCK 소식 배달 완료!'라고 덧붙여줘. 한국어로 작성해."
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"뉴스 요약 중 오류 발생: {str(e)}"

def send_to_discord(content):
    if not content or "오류 발생" in content:
        print(f"전송할 내용이 없거나 오류가 있습니다: {content}")
        # 오류 내용이라도 디스코드로 보내서 상태를 확인하게 합니다.
        payload = {"content": f"⚠️ LCK 봇 실행 상태 보고: \n{content}"}
    else:
        payload = {"content": content[:2000]}
    
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    print("LCK 뉴스 생성 시작...")
    news = get_lck_news()
    print("디스코드 전송 시작...")
    send_to_discord(news)
    print("작업 완료.")
