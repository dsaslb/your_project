import time
from apscheduler.schedulers.background import BackgroundScheduler
from app import app
from models import PluginApprovalRequest
from utils.alert_notifier import send_admin_alert

# 운영 자동화: 승인 대기 플러그인/요청 자동 알림 스크립트
# 초보자용: 서버와 함께 실행하면 주기적으로 승인 대기 알림을 관리자에게 전송합니다.

def send_pending_approval_alerts():
    with app.app_context():
        pending = PluginApprovalRequest.query.filter_by(status='pending').all()
        if pending:
            for req in pending:
                send_admin_alert(f"플러그인 승인 대기: {req.plugin_name} (요청자: {req.requester})")
            print(f"[알림] 승인 대기 플러그인 {len(pending)}건 관리자에게 알림 전송 완료.")
        else:
            print("[알림] 승인 대기 플러그인 없음.")

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_pending_approval_alerts, 'interval', minutes=10)
    scheduler.start()
    print("[운영자동화] 승인 대기 플러그인/요청 자동 알림 스케줄러 시작!")
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("[운영자동화] 스케줄러 종료.") 