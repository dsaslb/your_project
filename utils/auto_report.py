# utils/auto_report.py
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

def get_system_status():
    # 실제 시스템 상태/통계 데이터 조회 로직으로 교체
    return {
        "uptime": "99.99%",
        "active_users": 123,
        "feedback_count": 24,
        "critical_alerts": 1,
        "last_backup": "2024-06-01 02:00"
    }

def send_report_email(report, to_email):
    msg = MIMEText(report, "plain", "utf-8")
    msg["Subject"] = "[자동리포트] 시스템 상태/피드백 통계"
    msg["From"] = "noreply@example.com"
    msg["To"] = to_email

    # 실제 SMTP 서버 정보로 교체
    with smtplib.SMTP("smtp.example.com", 587) as server:
        server.starttls()
        server.login("noreply@example.com", "password")
        server.send_message(msg)

if __name__ == "__main__":
    status = get_system_status()
    report = (
        f"시스템 자동 리포트 ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n"
        f"- 가동률: {status['uptime']}\n"
        f"- 활성 사용자: {status['active_users']}\n"
        f"- 피드백 건수: {status['feedback_count']}\n"
        f"- 중요 알림: {status['critical_alerts']}\n"
        f"- 마지막 백업: {status['last_backup']}\n"
    )
    send_report_email(report, "admin@example.com")
    print("운영자에게 자동 리포트 전송 완료!") 