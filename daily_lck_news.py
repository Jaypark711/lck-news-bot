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
        
        # 1. 사용 가능한 모델 목록 직접 확인
        print("사용 가능한 모델 목록을 확인합니다...")
        all_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    all_models.append(m.name)
            print(f"발견된 모델: {all_models}")
        except Exception as list_err:
            print(f"모델 목록 수집 실패: {list_err}")
            all_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']

        # 2. 우선 순위 모델 선정 (검색 기능 포함 모델 우선)
        # 모델 이름에서 'models/' 접두사 처리
        test_prompts = f"{datetime.now().strftime('%Y-%m-%d')} LCK 최신 뉴스 5개를 구글 검색으로 찾아서 요약해줘."
        
        for model_path in all_models:
            try:
                print(f"시도 중인 모델: {model_path}")
                # 검색 기능을 포함하여 시도
                model = genai.GenerativeModel(
                    model_name=model_path,
                    tools=[{"google_search_retrieval": {}}]
                )
                response = model.generate_content(test_prompts)
                if response and response.text:
                    return response.text
            except Exception as e:
                print(f"{model_path} 검색 기능 실패: {e}. 일반 모드로 재시도...")
                try:
                    # 검색 기능 없이 일반 모드로 재시도
                    model = genai.GenerativeModel(model_name=model_path)
                    response = model.generate_content(test_prompts)
                    if response and response.text:
                        return response.text
                except Exception as e2:
                    print(f"{model_path} 일반 모드도 실패: {e2}")
                    continue
        
        return f"❌ 모든 가용 모델({all_models}) 호출 실패. \n마지막 오류: {traceback.format_exc()}"

    except Exception as e:
        return f"🔥 치명적 시스템 오류 발생: {str(e)}\n{traceback.format_exc()}"

def send_to_discord(content):
    if not DISCORD_WEBHOOK_URL:
        return
        
    try:
        header = f"📡 **LCK 뉴스 봇 가동 보고 ({datetime.now().strftime('%m/%d %H:%M')})**\n\n"
        full_message = header + content
        
        if len(full_message) > 2000:
            full_message = full_message[:1990] + "..."
            
        requests.post(DISCORD_WEBHOOK_URL, json={"content": full_message}, timeout=10)
    except Exception as e:
        print(f"디스코드 전송 실패: {e}")

if __name__ == "__main__":
    print("=== LCK 뉴스 봇 (슈퍼 로버스트 버전) 가동 ===")
    news = get_lck_news()
    send_to_discord(news)
    print("=== 작업 완료 ===")
