import os
import sys
from datetime import datetime, timedelta
from flask import Flask
from utils.email_utils import send_email
from models_main import db, Order, Notification

# Flask 앱/DB 초기화 (운영 환경에 맞게 조정)
app = Flask(__name__)
app.config.from_pyfile("config.py")
db.init_app(app)

# 관리자 이메일 환경변수/설정
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")


# 일간 자동 보고 스크립트 (초보자용 설명)
def send_daily_report():
    with app.app_context():
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        # 1. 어제 매출 합계
        sales = (
            db.session.query(db.func.sum(Order.total_amount))
            .filter(Order.created_at >= yesterday, Order.created_at < today)
            .scalar()
            or 0
        )
        # 2. 어제 이상징후(critical 알림)
        critical_alerts = Notification.query.filter(
            Notification.created_at >= yesterday,
            Notification.created_at < today,
            Notification.priority.in_(["critical", "emergency"]),
        ).all()
        # 3. 어제 전체 알림 개수
        total_alerts = Notification.query.filter(
            Notification.created_at >= yesterday, Notification.created_at < today
        ).count()
        # 4. 이메일 본문 생성
        body = f"""
[일간 운영 리포트]

- 일자: {yesterday.strftime('%Y-%m-%d')}
- 매출 합계: {sales:,}원
- 전체 알림: {total_alerts}건
- 이상징후(critical): {len(critical_alerts)}건

상세 알림:
"""
        for alert in critical_alerts:
            body += f"- {alert.title}: {alert.content} ({alert.created_at})\n"
        # 5. 이메일 발송
        subject = f"[일간 리포트] {yesterday.strftime('%Y-%m-%d')} 운영 요약"
        send_email(ADMIN_EMAIL, subject, body)
        print("✅ 일간 리포트 이메일 발송 완료")


if __name__ == "__main__":
    send_daily_report()
