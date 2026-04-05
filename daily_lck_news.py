import os
import requests
import google.generativeai as genai
from datetime import datetime
import traceback

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def get_lck_news():
    try:
        if not GEMINI_API_KEY:
            return "오류: API 키가 설정되지 않았습니다."
            
        genai.configure(api_key=GEMINI_API_KEY)
        
        # 모델 목록 확인 및 최적 모델 선택
        available_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
        except:
            available_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro']

        # 날짜를 특정하지 않고 "가장 최신(current)" 소식을 요청
        prompt = """
        LCK(League of Legends Champions Korea)의 가장 최근 뉴스 5가지를 구글 검색으로 찾아서 요약해줘. 
        어제나 오늘 발생한 따끈따끈한 소식을 우선적으로 찾아줘.
        [제목 - 요약 - 출처 링크] 형식으로 작성하고, 마지막에 '오늘의 LCK 소식 배달 완료!'라고 덧붙여줘. 
        한국어로 친절하게 작성해줘.
        """
        
        # 가용한 모델 중 첫 번째 모델로 시도 (구글 검색 도구 포함)
        for model_path in available_models:
            try:
                print(f"[{model_path}] 모델로 최신 뉴스 검색 중...")
                model = genai.GenerativeModel(
                    model_name=model_path,
                    tools=[{"google_search_retrieval": {}}]
                )
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text
            except Exception as e:
                print(f"{model_path} 검색 모드 실패: {e}. 일반 모드로 시도...")
                try:
                    model = genai.GenerativeModel(model_name=model_path)
                    response = model.generate_content("최신 LCK 뉴스 5개만 알려줘.")
                    if response and response.text:
                        return response.text
                except:
                    continue
        
        return "뉴스 데이터를 가져오는 데 실패했습니다."

    except Exception as e:
        return f"시스템 오류 발생: {str(e)}"

def send_to_discord(content):
    if not DISCORD_WEBHOOK_URL: return
    try:
        # 헤더에 실제 현재 날짜 표시
        display_date = datetime.now().strftime("%Y-%m-%d")
        payload = {"content": f"📡 **LCK 최신 소식 브리핑 ({display_date})**\n\n{content[:1900]}"}
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        print("디스코드 전송 완료!")
    except Exception as e:
        print(f"전송 실패: {e}")

if __name__ == "__main__":
    news = get_lck_news()
    send_to_discord(news)
