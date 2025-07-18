import os
from datetime import datetime
import requests
from utils.email_utils import send_email

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
API_URL = "http://localhost:5000/api/ai/assistant/report"


# AI 경영 어시스턴트 자동화 스케줄러 (초보자용 설명)
def send_ai_assistant_report():
    today = datetime.utcnow().date()
    res = requests.post(API_URL)
    data = res.json()
    subject = f"[AI 경영 리포트] {today} 자동 진단/예측/개선점"
    body = f"""
[AI 경영 어시스턴트 리포트]

- 진단: {data.get('diagnosis')}
- 개선점: {data.get('improvement')}
- 예측: {data.get('prediction')}
- 자연어 리포트: {data.get('llm_report')}

(이 리포트가 도움이 되었나요? 피드백 환영)
"""
    send_email(ADMIN_EMAIL, subject, body)
    print("✅ AI 경영 어시스턴트 리포트 이메일 발송 완료")


if __name__ == "__main__":
    send_ai_assistant_report()
