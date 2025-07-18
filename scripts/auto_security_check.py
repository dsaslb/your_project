import os
from models_main import AuditLog, EventLog, NotificationLog
from utils.notification_utils import send_email, slack_notify

# 운영/보안 자동 점검 스크립트 예시
# 시스템/서비스 상태, 알림/이력/이벤트, 외부 연동, 정책 적용 여부 점검


def check_services():
    # 예시: 서버/스케줄러/이벤트 감지 프로세스 확인
    running = os.popen(
        "ps aux | grep 'python' | grep -E 'app.py|auto_admin_alerts|event_auto_detector' | grep -v grep"
    ).read()
    return "[서비스 상태]\n" + (running if running else "실행 중인 서비스 없음")


def check_logs():
    # 예시: 최근 감사 로그/이벤트/알림 개수
    audit_count = AuditLog.query.count()
    event_count = EventLog.query.count()
    notif_count = NotificationLog.query.count()
    return f"[로그 현황]\n감사로그: {audit_count}건, 이벤트: {event_count}건, 알림: {notif_count}건"


def check_policy():
    # 예시: 환경변수/정책 파일 존재 여부
    env_exists = os.path.exists(".env")
    policy_exists = os.path.exists("docs/SECURITY_POLICY.md")
    return f"[정책 적용]\n.env: {env_exists}, SECURITY_POLICY.md: {policy_exists}"


def main():
    report = "\n".join([check_services(), check_logs(), check_policy()])
    print(report)
    # 관리자에게 이메일/슬랙 등으로 자동 발송 예시
    send_email("admin@example.com", "[자동점검] 운영/보안 점검 결과", report)
    slack_notify("#admin", f"[자동점검]\n{report}")


if __name__ == "__main__":
    main()
