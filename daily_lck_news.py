import os
import requests
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def get_lck_news():
    genai.configure(api_key=GEMINI_API_KEY)
    
    # 시도할 모델 리스트 (가장 최신 명칭 포함)
    models_to_try = [
        'gemini-1.5-flash-latest', 
        'gemini-1.5-flash', 
        'gemini-1.5-pro', 
        'gemini-pro'
    ]
    
    last_error = ""

    # 가용한 모델 목록 출력 (디버깅용)
    print("사용 가능한 모델 리스트 확인 중...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Found: {m.name}")
    except:
        print("모델 리스트를 가져올 수 없습니다.")

    for model_name in models_to_try:
        try:
            print(f"[{model_name}] 모델 시도 중...")
            model = genai.GenerativeModel(model_name)
            
            prompt = "오늘의 LCK(League of Legends Champions Korea) 최신 소식 5가지를 찾아서 요약해줘. [제목 - 요약 - 출처] 형식으로 작성하고, 마지막에 '오늘의 LCK 소식 배달 완료!'라고 덧붙여줘. 한국어로 작성해."
            
            response = model.generate_content(prompt)
            if response and response.text:
                print(f"[{model_name}] 성공!")
                return response.text
        except Exception as e:
            last_error = str(e)
            print(f"[{model_name}] 실패: {last_error}")
            continue
            
    return f"❌ 모든 모델 호출 실패. 마지막 에러: {last_error}"

def send_to_discord(content):
    if not content or "모든 모델 호출 실패" in content:
        payload = {"content": f"⚠️ LCK 봇 실행 실패 보고: \n{content}"}
    else:
        # 요약 내용만 깔끔하게 전송
        payload = {"content": f"📡 **오늘의 LCK 소식 브리핑**\n\n{content}"}
    
    requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)

if __name__ == "__main__":
    print("=== LCK 뉴스 수집 시작 ===")
    news = get_lck_news()
    send_to_discord(news)
    print("=== 모든 작업 완료 ===")
