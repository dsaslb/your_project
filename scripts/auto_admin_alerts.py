import time
from apscheduler.schedulers.background import BackgroundScheduler
import sys
import os

# 현재 스크립트의 상위 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 운영 자동화 중지됨 (서버는 계속 실행)
raise SystemExit("운영 자동화 중지: 승인 대기 알림 기능이 비활성화되었습니다.")

try:
    from app import app
    from models_main import PluginFeatureRequest  # noqa
    from utils.alert_notifier import send_alert
except ImportError as e:
    print(f"Import 오류: {e}")
    print("현재 디렉토리:", os.getcwd())
    print("Python 경로:", sys.path)
    sys.exit(1)

# 운영 자동화: 승인 대기 플러그인/요청 자동 알림 스크립트
# 초보자용: 서버와 함께 실행하면 주기적으로 승인 대기 알림을 관리자에게 전송합니다.


def send_pending_approval_alerts():
    with app.app_context():
        pending = PluginFeatureRequest.query.filter_by(status="pending").all()
        if pending:
            for req in pending:
                send_alert(
                    f"플러그인 승인 대기: {req.plugin_name} (요청자: {req.requester})",
                    level="warning"
                )
            print(
                f"[알림] 승인 대기 플러그인 {len(pending)}건 관리자에게 알림 전송 완료."
            )
        else:
            print("[알림] 승인 대기 플러그인 없음.")


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_pending_approval_alerts, "interval", minutes=10)
    scheduler.start()
    print("[운영자동화] 승인 대기 플러그인/요청 자동 알림 스케줄러 시작!")
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("[운영자동화] 스케줄러 종료.")
