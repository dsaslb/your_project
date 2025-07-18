# -*- coding: utf-8 -*-
"""
[자동 점검/업데이트/알림 스크립트 샘플]
- 패키지/의존성/보안 패치/환경 변수 변경 등 자동 감지 및 알림
- 초보자/운영자도 쉽게 확장/문의할 수 있도록 주석/문의 안내 포함
- 문의: support@example.com

[사용법]
- python scripts/auto_env_check_and_notify.py
"""
import os
import subprocess
import requests
import json

def check_outdated_packages():
    # pip list --outdated 결과를 가져옴
    result = subprocess.run(['pip', 'list', '--outdated', '--format=json'], capture_output=True, text=True)
    return json.loads(result.stdout) if result.returncode == 0 else []

def check_env_changes(env_file='.env'):
    # 환경 변수 파일 변경 감지(간단 예시)
    if not os.path.exists(env_file):
        return '환경 변수 파일 없음'
    mtime = os.path.getmtime(env_file)
    return f'{env_file} 최종 수정: {mtime}'

def send_alert(message, webhook_url=None):
    print('[알림]', message)
    if webhook_url:
        requests.post(webhook_url, data=json.dumps({'text': message}), headers={'Content-Type': 'application/json'})

if __name__ == '__main__':
    outdated = check_outdated_packages()
    env_status = check_env_changes()
    msg = f'[자동 점검] 패키지 업데이트: {len(outdated)}개, {env_status}'
    # send_alert(msg, 'https://hooks.slack.com/services/XXX/YYY/ZZZ')
    print(msg) 