from utils.notification_utils import send_email, slack_notify
import sys

# 자동 점검/리포트 결과를 관리자에게 이메일/슬랙 등으로 자동 발송하는 예시
# 사용 예시: python scripts/auto_report_notify.py [파일명]


def main():
    if len(sys.argv) < 2:
        print("사용법: python scripts/auto_report_notify.py [파일명]")
        return
    filename = sys.argv[1]
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    send_email("admin@example.com", "[자동리포트] 운영/보안 리포트", content)
    slack_notify(
        "#admin", f"[자동리포트]\n{content[:1000]}..."
    )  # 슬랙 메시지 길이 제한
    print(f"[알림] {filename} 관리자에게 자동 발송 완료")


if __name__ == "__main__":
    main()
