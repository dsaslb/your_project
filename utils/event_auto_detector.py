from utils.notification_utils import send_email, send_push  # pyright: ignore
from models_main import EventLog, db
import datetime

# 운영/보안 이벤트 자동 감지/알림 유틸리티
# 사용 예시: detect_and_alert_event('critical',  'DB 장애 발생')


def detect_and_alert_event(level, message):
    # 이벤트 자동 등록
    event = EventLog(message=message, level=level, timestamp=datetime.datetime.utcnow())
    db.session.add(event)
    db.session.commit()
    # 관리자 알림(이메일/푸시)
    send_email("admin@example.com", f"[이벤트] {level.upper()}", message)
    send_push("admin", f"[이벤트] {level.upper()}", message)
    print(f"[이벤트] {level} - {message} 자동 등록 및 알림 완료")
