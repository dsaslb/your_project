# -*- coding: utf-8 -*-
"""
[자동화 스크립트 샘플]
- 시스템 상태/피드백 통계 리포트 자동화, 슬랙/이메일 알림 연동
- 초보자/운영자도 쉽게 수정/확장/문의할 수 있도록 주석/예시/문의 안내 포함
- 문의: support@example.com

[사용법]
- python scripts/auto_report_and_alert.py
- 윈도우: 작업 스케줄러 등록, 리눅스: crontab 등록 예시는 docs/ADMIN_OPERATION_GUIDE.md 참고
"""
import requests
import smtplib
from email.mime.text import MIMEText
import json
import datetime

# 시스템 상태/피드백 통계 리포트 자동화 샘플

def get_system_status():
    # API에서 시스템 상태 정보 가져오기
    resp = requests.get('http://localhost:5000/api/status')
    return resp.json() if resp.ok else {}

def get_feedback_stats():
    # API에서 피드백 통계 정보 가져오기
    resp = requests.get('http://localhost:5000/api/admin/brand_stats')
    return resp.json() if resp.ok else {}

def send_slack_alert(message, webhook_url):
    # 슬랙 웹훅으로 알림 전송
    payload = {"text": message}
    requests.post(webhook_url, data=json.dumps(payload), headers={"Content-Type": "application/json"})

def send_email_alert(subject, body, to_email, smtp_server, smtp_user, smtp_pass):
    # 이메일로 알림 전송
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = to_email
    with smtplib.SMTP_SSL(smtp_server, 465) as server:
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, [to_email], msg.as_string())

# [외부 연동 샘플] 자동화 상태/점검 결과를 슬랙/이메일/웹훅 등 외부 시스템으로 전송 가능
# 예: send_slack_alert, send_email_alert, send_webhook_alert 등 함수 활용
#
def send_webhook_alert(message, webhook_url):
    # 웹훅으로 알림 전송 (예: Discord, Teams 등)
    import requests
    requests.post(webhook_url, data=json.dumps({'content': message}), headers={'Content-Type': 'application/json'})

if __name__ == '__main__':
    # 1. 시스템 상태/피드백 통계 리포트 생성
    status = get_system_status()
    stats = get_feedback_stats()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    report = f"[리포트] {now}\n시스템 상태: {status}\n피드백 통계: {stats}"

    # 2. 슬랙 알림 전송 (webhook_url은 실제 값으로 교체)
    # send_slack_alert(report, 'https://hooks.slack.com/services/XXX/YYY/ZZZ')

    # 3. 이메일 알림 전송 (smtp 정보는 실제 값으로 교체)
    # send_email_alert('시스템 리포트', report, 'admin@example.com', 'smtp.example.com', 'user', 'pass')

    # 슬랙/이메일/웹훅 등 외부 시스템으로 자동화 상태/점검 결과 전송 예시
    # send_slack_alert(report, 'https://hooks.slack.com/services/XXX/YYY/ZZZ')
    # send_email_alert('자동화 리포트', report, 'admin@example.com', 'smtp.example.com', 'user', 'pass')
    # send_webhook_alert(report, 'https://discord.com/api/webhooks/XXX/YYY')

    # [확장 예시] 점검/최신화/보안 상태를 이메일/슬랙/알림으로 자동 전송
    # 예: auto_reminder_and_update_check.py, auto_env_check_and_notify.py 결과를 읽어와서 send_slack_alert/send_email_alert로 전송 가능
    # (아래는 샘플)
    #
    # with open('automation_status.json') as f:
    #     status = json.load(f)
    #     if not status['upToDate']:
    #         send_slack_alert(f"[경고] 미점검/미최신화 파일: {status['details']}", webhook_url)
    #         send_email_alert('자동화 점검 경고', str(status), 'admin@example.com', smtp_server, smtp_user, smtp_pass)

    print('자동화 리포트/알림 샘플 실행 완료') 